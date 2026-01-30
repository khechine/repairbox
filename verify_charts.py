
import frappe
import os

def init_site():
    site = "gsmrepair.erpbox.tn"
    frappe.init(site=site, sites_path="sites")
    frappe.connect()

def set_default_print_format():
    try:
        # Create Property Setter for default print format
        if not frappe.db.exists("Property Setter", "Repair Order-main-default_print_format"):
            frappe.make_property_setter({
                "doctype": "Repair Order",
                "doctype_or_field": "DocType",
                "property": "default_print_format",
                "value": "Repair Receipt"
            })
            print("SET: Default Print Format to 'Repair Receipt'")
        else:
            print("Default Print Format already set.")
            
    except Exception as e:
        print(f"ERROR setting default print format: {e}")


def check_charts():
    charts = ["Repairs by Status", "Monthly Revenue"]
    for chart_name in charts:
        if frappe.db.exists("Dashboard Chart", chart_name):
            print(f"PASS: Chart '{chart_name}' exists.")
        else:
            print(f"FAIL: Chart '{chart_name}' does NOT exist. Creating it...")
            create_chart(chart_name)

def create_chart(chart_name):
    # Basic creation if missing (fallback)
    try:
        doc = frappe.new_doc("Dashboard Chart")
        doc.chart_name = chart_name
        doc.chart_type = "Donut" if "Status" in chart_name else "Bar"
        doc.document_type = "Repair Order"
        doc.is_public = 1
        
        if "Status" in chart_name:
             doc.group_by_based_on = "status"
        else:
             doc.based_on = "booking_date"
             doc.value_based_on = "grand_total"
             doc.group_by_type = "Sum"
             doc.timespan = "Monthly"
             
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"CREATED: Chart '{chart_name}'")
    except Exception as e:
        print(f"ERROR creating chart: {e}")

def fix_workspace():
    try:
        ws_name = "Repair Box"
        
        # Check if Workspace exists
        if not frappe.db.exists("Workspace", ws_name):
            print(f"FAIL: Workspace '{ws_name}' not found.")
            return

        ws = frappe.get_doc("Workspace", ws_name)
        
        # 1. Ensure Charts are linked
        expected_charts = [
            {"chart_name": "Repairs by Status", "label": "Repairs by Status"},
            {"chart_name": "Monthly Revenue", "label": "Monthly Revenue"}
        ]
        
        current_charts = [c.chart_name for c in ws.charts] if ws.charts else []
        modified = False
        
        for chart in expected_charts:
            if chart["chart_name"] not in current_charts:
                print(f"Adding missing chart: {chart['chart_name']}")
                ws.append("charts", chart)
                modified = True
                
        # 2. Ensure Shortcuts are linked
        expected_shortcuts = [
            {"label": "New Repair Order", "type": "Url", "url": "/app/repair-order/new"},
            {"label": "Add Device", "type": "Url", "url": "/app/device/new"},
            {"label": "New Checklist", "type": "Url", "url": "/app/inspection-checklist-template/new"},
            {"label": "Repair Kanban", "type": "Url", "url": "/app/repair-order/view/kanban"},
            {"label": "My Repairs", "type": "Url", "url": "/app/repair-order?assigned_to=Current%20User"}
        ]
        
        current_shortcuts = [s.label for s in ws.shortcuts] if ws.shortcuts else []
        for sc in expected_shortcuts:
             if sc["label"] not in current_shortcuts:
                 print(f"Adding missing shortcut: {sc['label']}")
                 ws.append("shortcuts", sc)
                 modified = True
        
        if modified:
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            print("Workspace updated successfully.")
        else:
            print("Workspace already up to date.")
            
    except Exception as e:
        print(f"ERROR in fix_workspace: {e}")

if __name__ == "__main__":
    init_site()
    set_default_print_format()
    check_charts()
    fix_workspace()

    charts = ["Repairs by Status", "Monthly Revenue"]
    for chart_name in charts:
        if frappe.db.exists("Dashboard Chart", chart_name):
            print(f"PASS: Chart '{chart_name}' exists.")
        else:
            print(f"FAIL: Chart '{chart_name}' does NOT exist.")

def fix_workspace():
    ws = frappe.get_doc("Workspace", "Repair Box")
    
    # 1. Ensure Charts are linked
    expected_charts = [
        {"chart_name": "Repairs by Status", "label": "Repairs by Status"},
        {"chart_name": "Monthly Revenue", "label": "Monthly Revenue"}
    ]
    
    current_charts = [c.chart_name for c in ws.charts]
    for chart in expected_charts:
        if chart["chart_name"] not in current_charts:
            print(f"Adding missing chart: {chart['chart_name']}")
            ws.append("charts", chart)
            
    # 2. Ensure Shortcuts are linked
    # (Just verifying presence for now, assuming standard ones are there)
    
    ws.save()
    frappe.db.commit()
    print("Workspace updated.")

if __name__ == "__main__":
    check_charts()
    fix_workspace()
