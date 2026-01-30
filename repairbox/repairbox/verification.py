
import frappe

def run_checks():
    print("Starting verification checks...")
    set_default_print_format()
    check_charts()
    fix_workspace()
    print("Verification complete.")

def set_default_print_format():
    try:
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
    try:
        doc = frappe.new_doc("Dashboard Chart")
        doc.chart_name = chart_name
        doc.document_type = "Repair Order"
        doc.is_public = 1
        doc.filters_json = "[]"
        
        if "Status" in chart_name:
             doc.chart_type = "Group By"  # Aggregation
             doc.type = "Donut"           # Visual
             doc.group_by_based_on = "status"
             doc.group_by_type = "Count"
        else:
             doc.chart_type = "Sum"       # Aggregation
             doc.type = "Bar"             # Visual
             doc.based_on = "booking_date"
             doc.value_based_on = "grand_total"
             doc.timespan = "Last Year"
             
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"CREATED: Chart '{chart_name}'")
    except Exception as e:
        print(f"ERROR creating chart '{chart_name}': {e}")




import json

def fix_workspace():
    try:
        ws_name = "Repair Box"
        if not frappe.db.exists("Workspace", ws_name):
            print(f"FAIL: Workspace '{ws_name}' not found.")
            return

        ws = frappe.get_doc("Workspace", ws_name)
        
        # Load content JSON
        content = json.loads(ws.content) if ws.content else []
        modified = False
        
        # 1. Ensure Charts are linked in backend
        expected_charts = [
            {"chart_name": "Repairs by Status", "label": "Repairs by Status"},
            {"chart_name": "Monthly Revenue", "label": "Monthly Revenue"}
        ]
        
        current_db_charts = [c.chart_name for c in ws.charts] if ws.charts else []
        for chart in expected_charts:
            if chart["chart_name"] not in current_db_charts:
                ws.append("charts", chart)
                modified = True
                
        # 2. Add Charts to Content JSON
        # Check if charts header exists
        has_chart_header = any(b.get("data", {}).get("text") == "Dashboards" for b in content)
        if not has_chart_header:
            content.append({"type": "header", "data": {"text": "Dashboards", "level": 4, "col": 12}})
            modified = True
            
        existing_content_charts = [b.get("data", {}).get("chart_name") for b in content if b["type"] == "chart"]
        
        for chart in expected_charts:
            if chart["chart_name"] not in existing_content_charts:
                print(f"Adding chart to layout: {chart['chart_name']}")
                content.append({"type": "chart", "data": {"chart_name": chart["chart_name"], "col": 6}})
                modified = True

        # 3. Ensure Shortcuts are linked in backend
        kanban_url = "/app/kanban-board/view/detail/Repair Order/Repair Status"
        expected_shortcuts = [
            {"label": "New Repair Order", "type": "Url", "url": "/app/repair-order/new"},
            {"label": "Add Device", "type": "Url", "url": "/app/device/new"},
            {"label": "New Checklist", "type": "Url", "url": "/app/inspection-checklist-template/new"},
            {"label": "Repair Kanban", "type": "Url", "url": kanban_url},
            {"label": "My Repairs", "type": "Url", "url": "/app/repair-order?assigned_to=Current%20User"}
        ]
        
        current_db_shortcuts = [s.label for s in ws.shortcuts] if ws.shortcuts else []
        for sc in expected_shortcuts:
             if sc["label"] not in current_db_shortcuts:
                 ws.append("shortcuts", sc)
                 modified = True
        
        # 4. Add Shortcuts to Content JSON
        existing_content_shortcuts = [b.get("data", {}).get("shortcut_name") for b in content if b["type"] == "shortcut"]
        
        # Find index of first shortcut or header to insert roughly at top
        insert_idx = 1 # After first header usually
        
        for sc in expected_shortcuts:
            if sc["label"] not in existing_content_shortcuts:
                 print(f"Adding shortcut to layout: {sc['label']}")
                 # Rename 'label' to 'shortcut_name' for content block
                 block = {"type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
                 content.insert(insert_idx, block)
                 insert_idx += 1
                 modified = True

        if modified:
            ws.content = json.dumps(content)
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            print("Workspace updated successfully with new layout.")
        else:
            print("Workspace already up to date.")
            
    except Exception as e:
        print(f"ERROR in fix_workspace: {e}")

