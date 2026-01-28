# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Defect(Document):
	def validate(self):
		"""Validate defect before saving"""
		if self.defect_title:
			self.defect_title = self.defect_title.strip()
		
		# Fetch brand from device
		if self.device and not self.brand:
			self.brand = frappe.db.get_value("Device", self.device, "brand")
