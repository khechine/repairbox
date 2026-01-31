from . import __version__ as app_version

app_name = "repairbox"
app_title = "RepairBox"
app_publisher = "Me"
app_description = "RepairBox"
app_email = "me@example.com"
app_license = "mit"

# Home Page
# ---------
home_page = "/app/repair-box"

# Fixtures
# --------
# Fixtures will be synced to the database when the app is installed
fixtures = [
	{
		"doctype": "Repair Status",
		"filters": [
			["name", "in", [
				"Pending Review",
				"In Progress",
				"Awaiting Parts",
				"Awaiting Customer Approval",
				"Testing",
				"Completed",
				"Ready for Pickup",
				"Delivered",
				"Cancelled",
				"On Hold"
			]]
		]
	},
	{
		"doctype": "Repair Priority",
		"filters": [
			["name", "in", [
				"Standard",
				"Express",
				"Urgent",
				"Economy"
			]]
		]
	},
	{
		"doctype": "Quick Reply"
	},
	{
		"doctype": "Inspection Checklist Template"
	}
]

# Installation
# ------------
after_install = "repairbox.setup.install.after_install"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/repairbox/css/repairbox.css"
# app_include_js = "/assets/repairbox/js/repairbox.js"

# include js, css files in header of web template
# web_include_css = "/assets/repairbox/css/repairbox.css"
# web_include_js = "/assets/repairbox/js/repairbox.js"
