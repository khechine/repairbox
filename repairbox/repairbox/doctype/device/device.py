# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Device(Document):
	def validate(self):
		"""Validate device before saving"""
		if self.device_name:
			self.device_name = self.device_name.strip()
