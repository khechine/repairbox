# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RepairLog(Document):
	def validate(self):
		"""Validate repair log before saving"""
		# Set updated_by to current user
		if not self.updated_by:
			self.updated_by = frappe.session.user
		
		# Fetch current status from repair order if not set
		if not self.status and self.repair_order:
			self.status = frappe.db.get_value("Repair Order", self.repair_order, "status")
	
	def after_insert(self):
		"""Actions after log is created"""
		# Update repair order status if status is set
		if self.status and self.repair_order:
			frappe.db.set_value("Repair Order", self.repair_order, "status", self.status)
		
		# TODO: Send notification to customer if notify_customer is checked
		# This would integrate with Frappe's notification system
