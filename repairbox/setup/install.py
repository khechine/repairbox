"""
RepairBox Installation Setup
Automatically configures workspace, charts, and defaults during app installation.
"""

import frappe
import json


def after_install():
    """
    Main installation hook - called automatically after app installation.
    """
    print("🚀 Setting up RepairBox...")
    
    set_default_print_format()
    create_dashboard_charts()
    setup_workspace()
    
    print("✅ RepairBox setup completed successfully!")


def set_default_print_format():
    """Set 'Repair Receipt' as default print format for Repair Order."""
    try:
        if not frappe.db.exists("Property Setter", "Repair Order-main-default_print_format"):
            frappe.make_property_setter({
                "doctype": "Repair Order",
                "doctype_or_field": "DocType",
                "property": "default_print_format",
                "value": "Repair Receipt"
            })
            frappe.db.commit()
            print("✓ Default Print Format set to 'Repair Receipt'")
        else:
            print("✓ Default Print Format already configured")
    except Exception as e:
        print(f"⚠ Error setting default print format: {e}")


def create_dashboard_charts():
    """Create dashboard charts for Repair Box workspace."""
    charts = [
        {
            "chart_name": "Repairs by Status",
            "chart_type": "Group By",
            "type": "Donut",
            "document_type": "Repair Order",
            "group_by_based_on": "status",
            "group_by_type": "Count",
            "is_public": 1,
            "filters_json": "[]"
        },
        {
            "chart_name": "Monthly Revenue",
            "chart_type": "Sum",
            "type": "Bar",
            "document_type": "Repair Order",
            "based_on": "booking_date",
            "value_based_on": "grand_total",
            "timespan": "Last Year",
            "is_public": 1,
            "filters_json": "[]"
        }
    ]
    
    for chart_data in charts:
        chart_name = chart_data["chart_name"]
        
        if frappe.db.exists("Dashboard Chart", chart_name):
            print(f"✓ Chart '{chart_name}' already exists")
            continue
            
        try:
            doc = frappe.new_doc("Dashboard Chart")
            for key, value in chart_data.items():
                setattr(doc, key, value)
            
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"✓ Created chart '{chart_name}'")
        except Exception as e:
            print(f"⚠ Error creating chart '{chart_name}': {e}")


def setup_workspace():
    """Configure Repair Box workspace with shortcuts and charts."""
    try:
        ws_name = "Repair Box"
        
        if not frappe.db.exists("Workspace", ws_name):
            print(f"⚠ Workspace '{ws_name}' not found - skipping configuration")
            return
        
        ws = frappe.get_doc("Workspace", ws_name)
        
        # Load content JSON
        content = json.loads(ws.content) if ws.content else []
        modified = False
        
        # 1. Link Charts to Workspace (backend)
        expected_charts = [
            {"chart_name": "Repairs by Status", "label": "Repairs by Status"},
            {"chart_name": "Monthly Revenue", "label": "Monthly Revenue"}
        ]
        
        current_db_charts = [c.chart_name for c in ws.charts] if ws.charts else []
        for chart in expected_charts:
            if chart["chart_name"] not in current_db_charts:
                ws.append("charts", chart)
                modified = True
        
        # 2. Add Charts to Content JSON (frontend layout)
        has_chart_header = any(b.get("data", {}).get("text") == "Dashboards" for b in content)
        if not has_chart_header:
            content.append({"type": "header", "data": {"text": "Dashboards", "level": 4, "col": 12}})
            modified = True
        
        existing_content_charts = [b.get("data", {}).get("chart_name") for b in content if b.get("type") == "chart"]
        for chart in expected_charts:
            if chart["chart_name"] not in existing_content_charts:
                content.append({"type": "chart", "data": {"chart_name": chart["chart_name"], "col": 6}})
                modified = True
        
        # 3. Link Shortcuts to Workspace (backend)
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
        
        # 4. Add Shortcuts to Content JSON (frontend layout)
        existing_content_shortcuts = [b.get("data", {}).get("shortcut_name") for b in content if b.get("type") == "shortcut"]
        
        # Insert shortcuts after first header (position 1)
        insert_idx = 1
        for sc in expected_shortcuts:
            if sc["label"] not in existing_content_shortcuts:
                block = {"type": "shortcut", "data": {"shortcut_name": sc["label"], "col": 3}}
                content.insert(insert_idx, block)
                insert_idx += 1
                modified = True
        
        # Save workspace if modified
        if modified:
            ws.content = json.dumps(content)
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            print("✓ Workspace configured successfully")
        else:
            print("✓ Workspace already configured")
            
    except Exception as e:
        print(f"⚠ Error configuring workspace: {e}")
