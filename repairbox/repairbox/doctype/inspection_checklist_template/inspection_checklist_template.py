# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InspectionChecklistTemplate(Document):
	def validate(self):
		"""Validate inspection checklist template before saving"""
		if self.template_name:
			self.template_name = self.template_name.strip()
		
		# Ensure only one default template per device type
		if self.is_default and self.device_type:
			frappe.db.sql("""
				UPDATE `tabInspection Checklist Template`
				SET is_default = 0
				WHERE device_type = %s AND name != %s
			""", (self.device_type, self.name))
