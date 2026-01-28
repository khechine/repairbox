# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RepairPriority(Document):
	def validate(self):
		"""Validate repair priority before saving"""
		if self.priority_name:
			self.priority_name = self.priority_name.strip()
		
		# Ensure only one default priority
		if self.is_default:
			frappe.db.sql("""
				UPDATE `tabRepair Priority`
				SET is_default = 0
				WHERE name != %s
			""", self.name)
