"""
Sample data creation for RepairBox - iPhone 12 repair example
"""

import frappe
from datetime import datetime, timedelta


def create_sample_data():
    """Create comprehensive iPhone 12 repair example."""
    
    print("🚀 Creating iPhone 12 repair example...")
    
    # 1. Create/Get Customer
    customer = create_customer()
    
    # 2. Ensure Brand and Device exist
    ensure_brand_exists()
    ensure_device_exists()
    
    # 3. Create Defects
    create_defects()
    
    # 4. Create Repair Order
    repair_order = create_repair_order(customer)
    
    print(f"✅ Sample repair order created: {repair_order.name}")
    print(f"📱 Customer: {customer.customer_name}")
    print(f"📱 Device: iPhone 12")
    print(f"💰 Total: {repair_order.grand_total} TND")
    
    return repair_order.name


def create_customer():
    """Create or get sample customer."""
    customer_name = "Ahmed Ben Ali"
    
    if frappe.db.exists("Customer", {"customer_name": customer_name}):
        customer = frappe.get_doc("Customer", {"customer_name": customer_name})
        print(f"✓ Customer '{customer_name}' already exists")
    else:
        customer = frappe.new_doc("Customer")
        customer.customer_name = customer_name
        customer.customer_type = "Individual"
        customer.customer_group = "Individual"
        customer.territory = "All Territories"
        customer.mobile_no = "+216 98 765 432"
        customer.email_id = "ahmed.benali@example.tn"
        customer.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✓ Created customer '{customer_name}'")
    
    return customer


def ensure_brand_exists():
    """Ensure Apple brand exists."""
    brand_name = "Apple"
    if not frappe.db.exists("Brand", brand_name):
        brand = frappe.new_doc("Brand")
        brand.brand = brand_name
        brand.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✓ Created brand '{brand_name}'")
    else:
        print(f"✓ Brand '{brand_name}' exists")


def ensure_device_exists():
    """Ensure iPhone 12 device exists."""
    device_name = "iPhone 12"
    if not frappe.db.exists("Device", device_name):
        device = frappe.new_doc("Device")
        device.device_name = device_name
        device.brand = "Apple"
        device.device_type = "Smartphone"
        device.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✓ Created device '{device_name}'")
    else:
        print(f"✓ Device '{device_name}' exists")


def create_defects():
    """Create common iPhone 12 defects/services."""
    defects_data = [
        {"title": "Screen Replacement", "price": 280.00, "desc": "OLED screen replacement"},
        {"title": "Battery Replacement", "price": 120.00, "desc": "Battery 2815 mAh"},
        {"title": "Back Glass Replacement", "price": 150.00, "desc": "Back glass panel"},
        {"title": "Camera Lens Repair", "price": 80.00, "desc": "Rear camera lens"},
        {"title": "Charging Port Cleaning", "price": 25.00, "desc": "Lightning port cleaning"},
        {"title": "Water Damage Treatment", "price": 95.00, "desc": "Water damage treatment"}
    ]
    
    for defect_data in defects_data:
        # Defect name is auto-generated as {device}-{defect_title}
        defect_name = f"iPhone 12-{defect_data['title']}"
        
        if not frappe.db.exists("Defect", defect_name):
            defect = frappe.new_doc("Defect")
            defect.device = "iPhone 12"  # Required field
            defect.defect_title = defect_data["title"]  # Required field
            defect.selling_price = defect_data["price"]  # Required field
            defect.description = defect_data["desc"]
            defect.estimated_time = 60  # minutes
            defect.cost_amount = defect_data["price"] * 0.6  # 60% cost
            defect.insert(ignore_permissions=True)
            print(f"✓ Created defect '{defect_name}'")
        else:
            print(f"✓ Defect '{defect_name}' exists")
    
    frappe.db.commit()


def create_repair_order(customer):
    """Create comprehensive repair order."""
    
    ro = frappe.new_doc("Repair Order")
    
    # Customer
    ro.customer = customer.name
    ro.contact_number = "+216 98 765 432"
    ro.email = "ahmed.benali@example.tn"
    
    # Device
    ro.brand = "Apple"
    ro.device = "iPhone 12"
    ro.device_model = "iPhone 12 (A2403)"
    ro.serial_number = "F17XH8QYPN72"
    ro.device_password = "1234"
    
    # Status
    ro.status = "In Progress"
    ro.priority = "Express"
    ro.assigned_to = "Administrator"
    
    # Dates
    ro.booking_date = datetime.now()
    ro.expected_completion = datetime.now() + timedelta(days=2)
    
    # Defects
    major_defects = [
        "iPhone 12-Screen Replacement",
        "iPhone 12-Battery Replacement",
        "iPhone 12-Back Glass Replacement",
        "iPhone 12-Camera Lens Repair",
        "iPhone 12-Water Damage Treatment"
    ]
    
    for defect_name in major_defects:
        if frappe.db.exists("Defect", defect_name):
            defect = frappe.get_doc("Defect", defect_name)
            ro.append("defects", {
                "defect": defect.name,
                "description": defect.description,
                "selling_price": defect.selling_price
            })
    
    # Notes
    ro.additional_notes = """Phone dropped from 2m, screen shattered, back glass cracked, water exposure, battery draining fast, camera lens scratched. Express service needed for business use."""
    
    ro.technician_notes = """DIAGNOSTIC: Screen shattered, back glass cracked, battery 78% health (swollen), water corrosion on port, camera lens scratched. PLAN: Water treatment, battery replacement, screen/back glass/camera lens replacement, full testing."""
    
    # Payment
    ro.paid_amount = 400.00
    ro.payment_status = "Partially Paid"
    
    ro.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return ro
