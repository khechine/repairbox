# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InspectionChecklistTemplate(Document):
	def validate(self):
		"""Validate inspection checklist template before saving"""
		if self.template_name:
			self.template_name = self.template_name.strip()

		# If device is set, auto-set device_type from device
		if self.device and not self.device_type:
			device_type = frappe.db.get_value('Device', self.device, 'device_type')
			if device_type:
				self.device_type = device_type

		# Ensure only one default template per device (specific device takes priority)
		if self.is_default and self.device:
			frappe.db.sql("""
				UPDATE `tabInspection Checklist Template`
				SET is_default = 0
				WHERE device = %s AND name != %s
			""", (self.device, self.name))
		# Ensure only one default template per device type (if no specific device)
		elif self.is_default and self.device_type and not self.device:
			frappe.db.sql("""
				UPDATE `tabInspection Checklist Template`
				SET is_default = 0
				WHERE device_type = %s AND device IS NULL AND name != %s
			""", (self.device_type, self.name))
