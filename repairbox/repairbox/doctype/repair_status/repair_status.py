# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RepairStatus(Document):
	def validate(self):
		"""Validate repair status before saving"""
		if self.status_name:
			self.status_name = self.status_name.strip()
		
		# Ensure only one default status
		if self.is_default:
			frappe.db.sql("""
				UPDATE `tabRepair Status`
				SET is_default = 0
				WHERE name != %s
			""", self.name)
