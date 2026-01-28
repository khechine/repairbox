# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Brand(Document):
	def validate(self):
		"""Validate brand before saving"""
		if self.brand_name:
			self.brand_name = self.brand_name.strip()
