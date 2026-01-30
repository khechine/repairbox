
import frappe
import json

def execute():
    workspace_content = [
        {"type":"header","data":{"text":"Quick Actions","level":4,"col":12}},
        {"type":"shortcut","data":{"shortcut_name":"New Repair Order","col":3}},
        {"type":"shortcut","data":{"shortcut_name":"Add Device","col":3}},
        {"type":"shortcut","data":{"shortcut_name":"New Checklist","col":3}},
        {"type":"shortcut","data":{"shortcut_name":"Defects","col":3}},
        {"type":"header","data":{"text":"Repair Operations","level":4,"col":12}},
        {"type":"card","data":{"card_name":"Repair Operations","col":4}},
        {"type":"card","data":{"card_name":"Master Data","col":4}},
        {"type":"card","data":{"card_name":"Inspections","col":4}},
        {"type":"header","data":{"text":"Settings","level":4,"col":12}},
        {"type":"card","data":{"card_name":"Settings","col":4}}
    ]

    doc_data = {
        "doctype": "Workspace",
        "label": "Repair Box",
        "name": "Repair Box",
        "module": "RepairBox",
        "public": 1,
        "is_hidden": 0,
        "content": json.dumps(workspace_content),
        "icon": "tools",
        "indicator_color": "blue",
        "title": "Repair Box",
        "shortcuts": [
            {
                "color": "Blue",
                "doc_view": "List",
                "icon": "plus",
                "label": "New Repair Order",
                "stats_filter": "{}",
                "type": "URL",
                "url": "/app/repair-order/new"
            },
            {
                "color": "Green",
                "doc_view": "List",
                "icon": "plus",
                "label": "Add Device",
                "stats_filter": "{}",
                "type": "URL",
                "url": "/app/device/new"
            },
            {
                "color": "Orange",
                "doc_view": "List",
                "icon": "plus",
                "label": "New Checklist",
                "stats_filter": "{}",
                "type": "URL",
                "url": "/app/inspection-checklist-template/new"
            },
            {
                "color": "Red",
                "doc_view": "List",
                "icon": "list",
                "label": "Defects",
                "link_to": "Defect",
                "stats_filter": "{}",
                "type": "DocType",
                "url": ""
            }
        ],
        "links": [
            {
                "label": "Repair Operations",
                "link_type": "DocType",
                "link_to": "Repair Order",
                "type": "Link"
            },
            {
                "label": "Repair Operations",
                "link_type": "DocType",
                "link_to": "Repair Log",
                "type": "Link"
            },
            {
                "label": "Repair Operations",
                "link_type": "DocType",
                "link_to": "Repair Status",
                "type": "Link"
            },
            {
                "label": "Repair Operations",
                "link_type": "DocType",
                "link_to": "Repair Priority",
                "type": "Link"
            },
            {
                "label": "Master Data",
                "link_type": "DocType",
                "link_to": "Device",
                "type": "Link"
            },
            {
                "label": "Master Data",
                "link_type": "DocType",
                "link_to": "Brand",
                "type": "Link"
            },
            {
                "label": "Master Data",
                "link_type": "DocType",
                "link_to": "Defect",
                "type": "Link"
            },
            {
                "label": "Master Data",
                "link_type": "DocType",
                "link_to": "Quick Reply",
                "type": "Link"
            },
            {
                "label": "Inspections",
                "link_type": "DocType",
                "link_to": "Inspection Checklist Template",
                "type": "Link"
            },
            {
                "label": "Inspections",
                "link_type": "DocType",
                "link_to": "Inspection Checklist Item",
                "type": "Link"
            },
            {
                "label": "Inspections",
                "link_type": "DocType",
                "link_to": "Device Inspection Item",
                "type": "Link"
            },
            {
                "label": "Settings",
                "link_type": "DocType",
                "link_to": "Repair Order Defect",
                "type": "Link"
            }
        ]
    }
    
    if frappe.db.exists("Workspace", "Repair Box"):
        frappe.delete_doc("Workspace", "Repair Box", force=True)
        
    doc = frappe.get_doc(doc_data)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Successfully created 'Repair Box' workspace")
