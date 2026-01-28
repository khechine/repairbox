# RepairBox Fixtures

This directory contains seed data (fixtures) that are automatically imported when the RepairBox app is installed.

## Fixture Files

### 1. repair_status.json
Default repair statuses with colors and notification settings:
- Pending Review (default)
- In Progress
- Awaiting Parts
- Awaiting Customer Approval
- Testing
- Completed
- Ready for Pickup
- Delivered
- Cancelled
- On Hold

### 2. repair_priority.json
Default priority levels with pricing:
- Standard ($0) - default, 3-5 business days
- Express ($15) - 1-2 business days
- Urgent ($30) - same-day or next-day
- Economy (-$5) - 7-10 business days

### 3. quick_reply.json
Pre-configured message templates:
- Device Received
- Repair Started
- Repair Completed
- Ready for Pickup
- Awaiting Approval
- Parts Ordered

### 4. inspection_checklist_template.json
Device inspection checklists:
- Smartphone Standard Inspection (20 items)
- Laptop Standard Inspection (12 items)
- Tablet Standard Inspection (10 items)

## How Fixtures Work

1. **Installation**: When you run `bench --site yoursite install-app repairbox`, the `after_install` hook is triggered
2. **Import**: The `install.py` script reads all JSON files from this directory
3. **Creation**: Each record is created in the database if it doesn't already exist
4. **Skip Duplicates**: If a record with the same name exists, it's skipped

## Customizing Fixtures

### Adding New Records

1. Edit the appropriate JSON file
2. Add your new record following the existing format
3. Reinstall the app or manually import using:
   ```bash
   bench --site yoursite execute repairbox.install.import_fixtures
   ```

### Modifying Existing Records

**Warning**: Modifying fixtures only affects new installations. Existing installations won't be updated automatically.

To update existing installations:
1. Manually update records through the UI
2. Or create a migration script

### Creating New Fixture Files

1. Create a new JSON file in this directory
2. Add it to the `fixture_files` list in `repairbox/install.py`
3. Follow the Frappe document structure

## Example Fixture Format

```json
[
  {
    "doctype": "Your DocType",
    "field_name": "value",
    "another_field": "another value",
    "child_table": [
      {
        "doctype": "Child DocType",
        "child_field": "child value"
      }
    ]
  }
]
```

## Exporting Current Data as Fixtures

To export your current data as fixtures:

```bash
bench --site yoursite export-fixtures
```

Or export specific doctypes:

```bash
bench --site yoursite export-doc "Repair Status" "Pending Review"
```

## Troubleshooting

### Fixtures Not Importing

1. Check the error log: `bench --site yoursite console` then `frappe.get_error_log()`
2. Verify JSON syntax is valid
3. Ensure all required fields are present
4. Check that DocTypes exist before importing

### Duplicate Records

If you see duplicate records:
1. The fixture might not have a unique `name` field
2. The existence check in `install.py` might not be working
3. Manually delete duplicates through the UI

### Updating Fixtures After Installation

Fixtures are only imported during installation. To update:
1. Manually update through UI
2. Create a patch/migration
3. Or reinstall the app (will lose custom data)

## Best Practices

1. **Use Descriptive Names**: Make fixture names clear and unique
2. **Set Defaults**: Mark one record as default where applicable
3. **Include Sort Orders**: For ordered lists like statuses
4. **Add Descriptions**: Help users understand each record's purpose
5. **Test Before Committing**: Always test fixtures on a fresh installation
