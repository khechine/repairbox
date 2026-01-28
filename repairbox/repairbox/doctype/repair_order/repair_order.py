# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, random_string


class RepairOrder(Document):
	def before_insert(self):
		"""Generate tracking ID before inserting"""
		if not self.tracking_id:
			self.tracking_id = random_string(10).upper()
	
	def validate(self):
		"""Validate and calculate totals"""
		self.calculate_totals()
		self.update_payment_status()
		self.load_inspection_checklist()
		
		# Set default status and priority if not set
		if not self.status:
			default_status = frappe.db.get_value("Repair Status", {"is_default": 1}, "name")
			if default_status:
				self.status = default_status
		
		if not self.priority:
			default_priority = frappe.db.get_value("Repair Priority", {"is_default": 1}, "name")
			if default_priority:
				self.priority = default_priority
	
	def load_inspection_checklist(self):
		"""Load inspection checklist from template if not already loaded"""
		# Only load if device is set and inspection list is empty
		if not self.device or len(self.device_inspection) > 0:
			return
		
		# Get device type from device
		device_doc = frappe.get_doc("Device", self.device)
		if not device_doc:
			return
		
		# Try to find a default template for this device type
		# For now, we'll use a generic template or create items manually
		# You can extend this to link devices to device types
		
		# Get default smartphone template as fallback
		template = frappe.db.get_value(
			"Inspection Checklist Template",
			{"is_default": 1, "is_active": 1},
			"name"
		)
		
		if not template:
			# Get any active template
			template = frappe.db.get_value(
				"Inspection Checklist Template",
				{"is_active": 1},
				"name"
			)
		
		if template:
			template_doc = frappe.get_doc("Inspection Checklist Template", template)
			
			# Clear existing items
			self.device_inspection = []
			
			# Add items from template
			for item in template_doc.checklist_items:
				self.append("device_inspection", {
					"item_name": item.item_name,
					"category": item.category,
					"is_mandatory": item.is_mandatory,
					"status": "Not Tested"
				})
	
	def calculate_totals(self):
		"""Calculate total service amount and grand total"""
		# Sum all defect prices
		total_service = 0
		for defect in self.defects:
			if defect.selling_price:
				total_service += defect.selling_price
		
		self.total_service_amount = total_service
		
		# Get priority charge
		if self.priority:
			priority_charge = frappe.db.get_value("Repair Priority", self.priority, "extra_charge") or 0
			self.priority_charge = priority_charge
		else:
			self.priority_charge = 0
		
		# Calculate tax (placeholder - can be configured later)
		# For now, assume 0% tax
		self.tax_amount = 0
		
		# Calculate grand total
		self.grand_total = self.total_service_amount + self.priority_charge + self.tax_amount
	
	def update_payment_status(self):
		"""Update payment status based on paid amount"""
		if not self.paid_amount or self.paid_amount == 0:
			self.payment_status = "Unpaid"
		elif self.paid_amount >= self.grand_total:
			self.payment_status = "Paid"
		else:
			self.payment_status = "Partially Paid"
