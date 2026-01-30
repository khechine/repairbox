# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, add_to_date
import hashlib
import random
import string


class RepairOrder(Document):
	def before_insert(self):
		"""Generate tracking ID before insert"""
		self.tracking_id = self.generate_tracking_id()
	
	def validate(self):
		"""Validation logic"""
		# Calculate totals
		self.calculate_totals()
		
		# Validate status transitions
		self.validate_status_change()
		
		# Auto-set expected completion if not set
		if not self.expected_completion and self.defects:
			self.set_expected_completion()
	
	def on_update(self):
		"""After save logic"""
		# Send notifications if status changed
		if self.has_value_changed('status'):
			self.notify_status_change()
	
	def calculate_totals(self):
		"""Calculate pricing totals"""
		total_service = 0
		
		# Sum all defects
		for defect in self.defects:
			# FIX: Use 'selling_price' instead of 'amount'
			total_service += flt(defect.selling_price)
		
		self.total_service_amount = total_service
		
		# Add priority charge
		priority_charge = flt(self.priority_charge)
		
		# Calculate tax (19% TVA)
		tax_rate = 0.19
		self.tax_amount = (total_service + priority_charge) * tax_rate
		
		# Grand total
		self.grand_total = total_service + priority_charge + self.tax_amount
	
	def set_expected_completion(self):
		"""Auto-calculate expected completion based on defects"""
		total_minutes = 0
		
		for defect_row in self.defects:
			if defect_row.defect:
				try:
					defect_doc = frappe.get_doc('Defect', defect_row.defect)
					if defect_doc.estimated_time:
						total_minutes += flt(defect_doc.estimated_time)
				except frappe.DoesNotExistError:
					continue
		
		if total_minutes > 0:
			# Add buffer (20%)
			total_minutes = total_minutes * 1.2
			
			# Set expected completion
			self.expected_completion = add_to_date(
				self.booking_date or now_datetime(),
				hours=total_minutes / 60
			)
	
	def validate_status_change(self):
		"""Validate status transitions"""
		if not self.has_value_changed('status'):
			return
		
		old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
		new_status = self.status
		
		# Cannot mark as Delivered if payment not complete (unless Manager)
		if new_status == 'Delivered' and self.payment_status != 'Paid':
			if 'System Manager' not in frappe.get_roles():
				frappe.throw(
					frappe._('Cannot mark as Delivered without full payment. Contact Manager for override.'),
					title='Payment Required'
				)
		
		# Cannot mark as Completed without defects/services
		if new_status == 'Completed' and not self.defects:
			frappe.throw(
				frappe._('Cannot complete repair without defects/services recorded.'),
				title='Missing Information'
			)
		
		# Cannot go back to Pending Review from other statuses
		if old_status and old_status != 'Pending Review' and new_status == 'Pending Review':
			frappe.throw(
				frappe._('Cannot return to Pending Review status'),
				title='Invalid Status Change'
			)
	
	def notify_status_change(self):
		"""Send notification to customer on status change"""
		# Check if this status should notify customer
		if not self.status:
			return

		try:
			status_doc = frappe.get_doc('Repair Status', self.status)
			if not status_doc.notify_customer:
				return
		except frappe.DoesNotExistError:
			return
		
		if not self.email:
			return
		
		# Get email template
		subject = f"Repair Order {self.name} - Status Update"
		message = self.get_status_email_message()
		
		# Send email
		try:
			frappe.sendmail(
				recipients=[self.email],
				subject=subject,
				message=message,
				reference_doctype=self.doctype,
				reference_name=self.name
			)
		except frappe.OutgoingEmailError:
			frappe.log_error(frappe.get_traceback(), _("Email setup required for Repair Order notifications"))
			# Don't throw the error, just log and continue
			pass
	
	def get_status_email_message(self):
		"""Get email message for status change"""
		messages = {
			'In Progress': f"Your {self.device} repair is now in progress. Our technician is working on it.",
			'Testing': f"Your {self.device} repair is complete and undergoing quality testing.",
			'Completed': f"Good news! Your {self.device} repair is complete.",
			'Ready for Pickup': f"Your {self.device} is ready for pickup! Tracking ID: {self.tracking_id}",
			'Delivered': f"Thank you for choosing us! Your {self.device} has been delivered.",
			'Awaiting Customer Approval': f"Your repair requires approval. Total cost: {frappe.utils.fmt_money(self.grand_total)}. Please confirm to proceed.",
			'On Hold': f"Your repair order has been put on hold. We will contact you shortly.",
			'Cancelled': f"Your repair order has been cancelled."
		}
		
		base_message = messages.get(self.status, f"Your repair order status has been updated to: {self.status}")
		
		return f"""
		<p>Dear {self.customer_name},</p>
		<p>{base_message}</p>
		<p><strong>Order Details:</strong></p>
		<ul>
			<li>Order ID: {self.name}</li>
			<li>Device: {self.device}</li>
			<li>Status: {self.status}</li>
			{f'<li>Tracking ID: {self.tracking_id}</li>' if self.tracking_id else ''}
		</ul>
		<p>If you have any questions, please contact us.</p>
		<p>Best regards,<br>RepairBox Team</p>
		"""
	
	def generate_tracking_id(self):
		"""Generate unique tracking ID"""
		# Format: RB-XXXXX (RB = RepairBox, XXXXX = random alphanumeric)
		random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
		return f"RB-{random_part}"


@frappe.whitelist()
def get_my_repairs():
	"""Get repairs assigned to current user (for Dashboard)"""
	user = frappe.session.user
	
	repairs = frappe.get_all(
		'Repair Order',
		filters={
			'assigned_to': user,
			'status': ['not in', ['Delivered', 'Cancelled']]
		},
		fields=['name', 'customer_name', 'device', 'status', 'priority', 'expected_completion'],
		order_by='expected_completion asc'
	)
	
	return repairs


@frappe.whitelist()
def get_overdue_repairs():
	"""Get overdue repairs"""
	repairs = frappe.get_all(
		'Repair Order',
		filters={
			'expected_completion': ['<', now_datetime()],
			'status': ['not in', ['Delivered', 'Cancelled', 'Completed']]
		},
		fields=['name', 'customer_name', 'device', 'status', 'expected_completion', 'assigned_to'],
		order_by='expected_completion asc'
	)
	
	return repairs


@frappe.whitelist()
def quick_create_customer(customer_name, contact_number, email=None):
	"""Quick create customer from Repair Order form"""
	customer = frappe.get_doc({
		'doctype': 'Customer',
		'customer_name': customer_name,
		'customer_type': 'Individual',
		'mobile_no': contact_number,
		'email_id': email
	})
	
	customer.insert(ignore_permissions=True)
	
	return customer.name
