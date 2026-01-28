# RepairBox

RepairBox is a comprehensive Frappe application for managing repair shop operations, from device intake to delivery.

## Features

### Core Functionality
- **Device Management** - Organize devices by brand and model
- **Repair Order Tracking** - Complete repair workflow management
- **Customer Management** - Integrated with Frappe Customer DocType
- **Device Inspection** - Systematic checklist for device intake
- **Status Tracking** - Customizable repair statuses with color coding
- **Priority Levels** - Multiple priority options with pricing
- **Repair Logs** - Detailed activity tracking for each order
- **Quick Replies** - Pre-configured message templates for customer communication

### Business Features
- **Automatic Calculations** - Service totals, priority charges, and grand totals
- **Payment Tracking** - Track paid amounts and payment status
- **Unique Tracking IDs** - Auto-generated IDs for customer tracking
- **Technician Assignment** - Assign repairs to specific technicians
- **Public Tracking** - Customer-facing repair tracking (coming soon)
- **Online Booking** - Public repair booking form (coming soon)

### Seed Data Included
The app comes with ready-to-use default data:
- **10 Repair Statuses** - From "Pending Review" to "Delivered"
- **4 Priority Levels** - Standard, Express, Urgent, Economy
- **6 Message Templates** - Common customer notifications
- **3 Inspection Checklists** - For smartphones, laptops, and tablets

## Installation

This app is designed to be installed in a Frappe/ERPNext environment.

```bash
# In your bench directory
bench get-app /path/to/repairbox
bench --site your-site install-app repairbox
bench --site your-site migrate
```

After installation, the app will automatically:
1. Create all DocTypes
2. Import default statuses, priorities, and templates
3. Set up inspection checklists
4. Configure the RepairBox module

## Quick Start

1. **Set Up Master Data**
   - Create Brands (Apple, Samsung, etc.)
   - Create Devices linked to brands
   - Create Defects/Services for each device

2. **Configure Settings** (Optional)
   - Customize repair statuses
   - Adjust priority pricing
   - Modify inspection checklists
   - Edit message templates

3. **Create Repair Orders**
   - Select customer and device
   - System auto-loads inspection checklist
   - Add defects/services
   - Assign technician and priority
   - Track progress with repair logs

## Documentation

- [Implementation Plan](./implementation_plan.md) - Technical architecture
- [Inspection Checklist Guide](./inspection_checklist_guide.md) - Device inspection system
- [Seed Data Guide](./seed_data_guide.md) - Default data and customization
- [Sample Checklists](./INSPECTION_CHECKLISTS.md) - Inspection templates

## DocTypes

### Master Data
- **Brand** - Device manufacturers
- **Device** - Repairable devices
- **Defect** - Services and repairs

### Configuration
- **Repair Status** - Workflow statuses
- **Repair Priority** - Priority levels with pricing
- **Quick Reply** - Message templates
- **Inspection Checklist Template** - Device inspection templates

### Transactional
- **Repair Order** - Main repair document
- **Repair Log** - Activity tracking
- **Repair Order Defect** - Selected services (child table)
- **Device Inspection Item** - Inspection results (child table)
- **Inspection Checklist Item** - Template items (child table)

## License

MIT
