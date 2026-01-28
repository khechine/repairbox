# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class QuickReply(Document):
	def validate(self):
		"""Validate quick reply before saving"""
		if self.title:
			self.title = self.title.strip()
