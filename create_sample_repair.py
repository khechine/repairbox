"""
Script to create a comprehensive iPhone 12 repair example
with multiple broken parts and complete invoice data.
"""

import frappe
from datetime import datetime, timedelta


def create_sample_iphone_repair():
    """Create a complete iPhone 12 repair example."""
    
    print("🚀 Creating iPhone 12 repair example...")
    
    # 1. Create/Get Customer
    customer = create_customer()
    
    # 2. Create/Get Device
    device = create_device()
    
    # 3. Create Defects
    defects = create_defects()
    
    # 4. Create Repair Order
    repair_order = create_repair_order(customer, device, defects)
    
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
        customer.territory = "Tunisia"
        customer.mobile_no = "+216 98 765 432"
        customer.email_id = "ahmed.benali@example.tn"
        customer.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✓ Created customer '{customer_name}'")
    
    return customer


def create_device():
    """Create or get iPhone 12 device."""
    device_name = "iPhone 12"
    brand_name = "Apple"
    
    # Ensure Brand exists
    if not frappe.db.exists("Brand", brand_name):
        brand = frappe.new_doc("Brand")
        brand.brand = brand_name
        brand.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✓ Created brand '{brand_name}'")
    
    # Ensure Device exists
    if frappe.db.exists("Device", device_name):
        device = frappe.get_doc("Device", device_name)
        print(f"✓ Device '{device_name}' already exists")
    else:
        device = frappe.new_doc("Device")
        device.device_name = device_name
        device.brand = brand_name
        device.device_type = "Smartphone"
        device.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✓ Created device '{device_name}'")
    
    return device


def create_defects():
    """Create common iPhone 12 defects/services."""
    defects_data = [
        {
            "defect_title": "Screen Replacement",
            "selling_price": 280.00,
            "description": "OLED screen replacement with original quality display"
        },
        {
            "defect_title": "Battery Replacement",
            "selling_price": 120.00,
            "description": "High capacity battery replacement (2815 mAh)"
        },
        {
            "defect_title": "Back Glass Replacement",
            "selling_price": 150.00,
            "description": "Back glass panel replacement with adhesive"
        },
        {
            "defect_title": "Camera Lens Repair",
            "selling_price": 80.00,
            "description": "Rear camera lens glass replacement"
        },
        {
            "defect_title": "Charging Port Cleaning",
            "selling_price": 25.00,
            "description": "Deep cleaning of lightning port"
        },
        {
            "defect_title": "Water Damage Treatment",
            "selling_price": 95.00,
            "description": "Complete water damage diagnostic and treatment"
        }
    ]
    
    created_defects = []
    for defect_data in defects_data:
        # Defect name is auto-generated as: device-defect_title
        defect_name = f"iPhone 12-{defect_data['defect_title']}"
        
        if frappe.db.exists("Defect", defect_name):
            print(f"✓ Defect '{defect_name}' already exists")
        else:
            defect = frappe.new_doc("Defect")
            defect.device = "iPhone 12"  # Mandatory field
            defect.defect_title = defect_data["defect_title"]  # Mandatory field
            defect.selling_price = defect_data["selling_price"]
            defect.description = defect_data["description"]
            defect.insert(ignore_permissions=True)
            print(f"✓ Created defect '{defect_name}'")
        
        created_defects.append(defect_name)
    
    frappe.db.commit()
    return created_defects


def create_repair_order(customer, device, defects):
    """Create a comprehensive repair order."""
    
    # Create repair order
    ro = frappe.new_doc("Repair Order")
    
    # Customer info
    ro.customer = customer.name
    ro.contact_number = customer.mobile_no
    ro.email = customer.email_id
    
    # Device info
    ro.brand = "Apple"
    ro.device = device.name
    ro.device_model = "iPhone 12 (A2403)"
    ro.serial_number = "F17XH8QYPN72"
    ro.device_password = "1234"
    
    # Status and priority
    ro.status = "In Progress"
    ro.priority = "Express"
    ro.assigned_to = "administrator"
    
    # Dates
    ro.booking_date = datetime.now()
    ro.expected_completion = datetime.now() + timedelta(days=2)
    
    # Add defects - iPhone 12 with multiple issues
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
    ro.additional_notes = """
    <p><strong>Customer Report:</strong></p>
    <ul>
        <li>Phone dropped from 2 meters onto concrete</li>
        <li>Screen completely shattered with touch not responding</li>
        <li>Back glass also cracked</li>
        <li>Phone was briefly exposed to water (rain)</li>
        <li>Battery draining very fast (20% in 2 hours)</li>
        <li>Camera lens scratched</li>
    </ul>
    <p><strong>Customer Priority:</strong> Express service needed - phone used for business</p>
    """
    
    ro.technician_notes = """
    <p><strong>Initial Diagnostic:</strong></p>
    <ul>
        <li>✓ Screen: Completely shattered, digitizer not responding</li>
        <li>✓ Back glass: Multiple cracks, needs replacement</li>
        <li>✓ Battery: Health at 78%, swollen, immediate replacement required</li>
        <li>✓ Water damage: Minor corrosion detected on charging port</li>
        <li>✓ Camera: Rear lens scratched, affecting photo quality</li>
        <li>✓ Other components: Logic board OK, Face ID working</li>
    </ul>
    <p><strong>Repair Plan:</strong></p>
    <ol>
        <li>Water damage treatment first (ultrasonic cleaning)</li>
        <li>Replace battery (safety priority)</li>
        <li>Replace screen with OLED original quality</li>
        <li>Replace back glass</li>
        <li>Replace camera lens</li>
        <li>Full testing and calibration</li>
    </ol>
    <p><strong>Parts Ordered:</strong> All parts in stock, ready to proceed</p>
    """
    
    # Payment
    ro.paid_amount = 400.00  # Partial payment
    ro.payment_status = "Partially Paid"
    
    # Insert and calculate
    ro.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return ro


if __name__ == "__main__":
    create_sample_iphone_repair()
