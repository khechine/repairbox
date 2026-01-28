frappe.ui.form.on('Repair Order', {
    refresh: function (frm) {
        // Add custom button to toggle inspection checklist
        if (!frm.is_new()) {
            // Add button to load/show inspection checklist
            frm.add_custom_button(__('Load Inspection Checklist'), function () {
                load_inspection_checklist(frm);
            }, __('Actions'));
        }

        // Add button in new form to load checklist when device is selected
        if (frm.is_new() && frm.doc.device) {
            frm.add_custom_button(__('Load Inspection Checklist'), function () {
                load_inspection_checklist(frm);
            }, __('Actions'));
        }
    },

    device: function (frm) {
        // Show load button when device is selected
        if (frm.doc.device && frm.is_new()) {
            frm.trigger('refresh');
        }
    },

    onload: function (frm) {
        // Hide inspection section by default
        toggle_inspection_section(frm, false);
    }
});

function load_inspection_checklist(frm) {
    if (!frm.doc.device) {
        frappe.msgprint(__('Please select a device first'));
        return;
    }

    // Check if checklist already loaded
    if (frm.doc.device_inspection && frm.doc.device_inspection.length > 0) {
        frappe.confirm(
            __('Inspection checklist already loaded. Do you want to reload it? This will clear existing inspection data.'),
            function () {
                // Yes - reload
                fetch_and_load_checklist(frm);
            },
            function () {
                // No - just show the section
                toggle_inspection_section(frm, true);
            }
        );
    } else {
        // Load for first time
        fetch_and_load_checklist(frm);
    }
}

function fetch_and_load_checklist(frm) {
    frappe.call({
        method: 'repairbox.repairbox.doctype.repair_order.repair_order.get_inspection_checklist',
        args: {
            device: frm.doc.device
        },
        callback: function (r) {
            if (r.message) {
                // Clear existing items
                frm.clear_table('device_inspection');

                // Add items from template
                r.message.forEach(function (item) {
                    let row = frm.add_child('device_inspection');
                    row.item_name = item.item_name;
                    row.category = item.category;
                    row.is_mandatory = item.is_mandatory;
                    row.status = 'Not Tested';
                });

                // Refresh the field
                frm.refresh_field('device_inspection');

                // Show the section
                toggle_inspection_section(frm, true);

                frappe.show_alert({
                    message: __('Inspection checklist loaded successfully'),
                    indicator: 'green'
                });
            } else {
                frappe.msgprint(__('No inspection checklist template found for this device type'));
            }
        }
    });
}

function toggle_inspection_section(frm, show) {
    // Toggle the inspection section visibility
    let section = frm.fields_dict.device_inspection.wrapper.closest('.form-section');
    if (section) {
        if (show) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    }
}
