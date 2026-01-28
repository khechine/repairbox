# Copyright (c) 2026, Me and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_install():
	"""Called after app is installed"""
	try:
		# Import fixtures
		import_fixtures()
		
		# Print success message
		frappe.msgprint(
			_("RepairBox app installed successfully with default data!"),
			title=_("Installation Complete"),
			indicator="green"
		)
		
	except Exception as e:
		frappe.log_error(f"Error during RepairBox installation: {str(e)}")
		frappe.msgprint(
			_("RepairBox app installed but there was an error loading default data. Please check the error log."),
			title=_("Installation Warning"),
			indicator="orange"
		)


def import_fixtures():
	"""Import fixture data from JSON files"""
	import os
	import json
	
	# Get the fixtures directory path
	fixtures_dir = frappe.get_app_path("repairbox", "repairbox", "fixtures")
	
	# List of fixture files to import
	fixture_files = [
		"repair_status.json",
		"repair_priority.json",
		"quick_reply.json",
		"inspection_checklist_template.json"
	]
	
	for fixture_file in fixture_files:
		file_path = os.path.join(fixtures_dir, fixture_file)
		
		if not os.path.exists(file_path):
			frappe.log_error(f"Fixture file not found: {file_path}")
			continue
		
		try:
			with open(file_path, 'r') as f:
				data = json.load(f)
			
			# Import each record
			for record in data:
				doctype = record.get("doctype")
				
				# Check if record already exists
				if doctype and "name" in record:
					exists = frappe.db.exists(doctype, record.get("name"))
					if exists:
						continue
				
				# Create new document
				doc = frappe.get_doc(record)
				doc.insert(ignore_permissions=True)
			
			frappe.db.commit()
			print(f"Imported fixture: {fixture_file}")
			
		except Exception as e:
			frappe.log_error(f"Error importing fixture {fixture_file}: {str(e)}")
			continue
