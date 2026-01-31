// Copyright (c) 2026, Me and contributors
// For license information, please see license.txt

frappe.ui.form.on('Repair Order', {
    // ========================================
    // 1. INITIALIZATION & SMART DEFAULTS
    // ========================================

    onload: function (frm) {
        if (frm.is_new()) {
            // Auto-assign to current user if Technician role
            if (frappe.user_roles.includes('Technician') && !frm.doc.assigned_to) {
                frm.set_value('assigned_to', frappe.session.user);
            }

            // Set default status
            frappe.db.get_value('Repair Status',
                { is_default: 1 },
                'name',
                (r) => {
                    if (r && r.name) {
                        frm.set_value('status', r.name);
                    }
                }
            );

            // Set default priority
            frappe.db.get_value('Repair Priority',
                { is_default: 1 },
                'name',
                (r) => {
                    if (r && r.name) {
                        frm.set_value('priority', r.name);
                    }
                }
            );

            // Set booking date to now
            frm.set_value('booking_date', frappe.datetime.now_datetime());
        }
    },

    // ========================================
    // 2. CONTEXTUAL ACTIONS BY STATUS
    // ========================================

    refresh: function (frm) {
        // Clear previous custom buttons
        frm.clear_custom_buttons();

        if (!frm.is_new()) {
            // Add contextual buttons based on status
            add_status_actions(frm);

            // Add utility buttons (always visible)
            add_utility_buttons(frm);

            // Update field locking
            update_field_permissions(frm);

            // Add status indicator
            add_status_indicator(frm);
        }

        // Render inspection toggle buttons if checklist has items
        if (frm.doc.device_inspection && frm.doc.device_inspection.length > 0) {
            render_inspection_toggle_buttons(frm);
        }
    },

    // ========================================
    // 3. FIELD LOCKING BY STATUS
    // ========================================

    status: function (frm) {
        update_field_permissions(frm);
    },

    // ========================================
    // 4. AUTO-CALCULATIONS
    // ========================================

    defects: function (frm) {
        calculate_totals(frm);
    },

    priority: function (frm) {
        // Fetch priority charge
        if (frm.doc.priority) {
            frappe.db.get_value('Repair Priority', frm.doc.priority, 'extra_charge', (r) => {
                if (r) {
                    frm.set_value('priority_charge', r.extra_charge || 0);
                    calculate_totals(frm);
                }
            });
        }
    },

    paid_amount: function (frm) {
        update_payment_status(frm);
    },

    // ========================================
    // 5. DEVICE SELECTION HELPERS
    // ========================================

    brand: function (frm) {
        // Filter devices by brand
        frm.set_query('device', function () {
            return {
                filters: {
                    brand: frm.doc.brand,
                    is_active: 1
                }
            };
        });

        // Filter defects by brand
        frm.fields_dict['defects'].grid.get_field('defect').get_query = function () {
            return {
                filters: {
                    brand: frm.doc.brand,
                    is_active: 1
                }
            };
        };
    },

    device: function (frm) {
        // Filter defects by device
        if (frm.doc.device) {
            frm.fields_dict['defects'].grid.get_field('defect').get_query = function () {
                return {
                    filters: {
                        device: frm.doc.device,
                        is_active: 1
                    }
                };
            };

            // Auto-load inspection checklist when device is selected
            load_inspection_checklist(frm);
        }
    }
});

// ========================================
// CHILD TABLE: Repair Order Defect
// ========================================

frappe.ui.form.on('Repair Order Defect', {
    defect: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.defect) {
            // Auto-fill amount from defect master
            frappe.db.get_value('Defect', row.defect, 'selling_price', (r) => {
                if (r) {
                    // FIX: Use 'selling_price' instead of 'amount'
                    frappe.model.set_value(cdt, cdn, 'selling_price', r.selling_price);
                    calculate_totals(frm);
                }
            });
        }
    },

    selling_price: function (frm) {
        calculate_totals(frm);
    },

    defects_remove: function (frm) {
        calculate_totals(frm);
    }
});

// ========================================
// HELPER FUNCTIONS
// ========================================

// ... [Keep helper functions unchanged except for field name references]

function add_status_actions(frm) {
    const status = frm.doc.status;

    // Pending Review → Start Repair
    if (status === 'Pending Review') {
        frm.add_custom_button(__('Start Repair'), () => {
            frm.set_value('status', 'In Progress');
            frm.save();
        }).addClass('btn-primary');

        frm.add_custom_button(__('Request More Info'), () => {
            show_customer_message_dialog(frm, 'Request Information');
        });
    }

    // In Progress → Multiple options
    if (status === 'In Progress') {
        frm.add_custom_button(__('Mark as Testing'), () => {
            frm.set_value('status', 'Testing');
            frm.save();
        }).addClass('btn-primary');

        frm.add_custom_button(__('Order Parts'), () => {
            frm.set_value('status', 'Awaiting Parts');
            frm.save();
        });

        frm.add_custom_button(__('Request Customer Approval'), () => {
            show_customer_approval_dialog(frm);
        });
    }

    // Awaiting Parts → Resume
    if (status === 'Awaiting Parts') {
        frm.add_custom_button(__('Parts Received - Resume'), () => {
            frm.set_value('status', 'In Progress');
            frm.save();
        }).addClass('btn-primary');
    }

    // Awaiting Customer Approval → Approved
    if (status === 'Awaiting Customer Approval') {
        frm.add_custom_button(__('Customer Approved'), () => {
            frm.set_value('status', 'In Progress');
            frm.save();
        }).addClass('btn-primary');

        frm.add_custom_button(__('Send Reminder'), () => {
            send_approval_reminder(frm);
        });
    }

    // Testing → Complete
    if (status === 'Testing') {
        frm.add_custom_button(__('Mark as Completed'), () => {
            frm.set_value('status', 'Completed');
            frm.set_value('actual_completion', frappe.datetime.now_datetime());
            frm.save();
        }).addClass('btn-primary');

        frm.add_custom_button(__('Return to Repair'), () => {
            frappe.prompt({
                label: 'Reason',
                fieldname: 'reason',
                fieldtype: 'Small Text',
                reqd: 1
            }, (values) => {
                frm.add_comment('Comment', `Returned to repair: ${values.reason}`);
                frm.set_value('status', 'In Progress');
                frm.save();
            }, __('Why returning to repair?'));
        });
    }

    // Completed → Ready for Pickup
    if (status === 'Completed') {
        frm.add_custom_button(__('Notify Customer - Ready'), () => {
            notify_customer_ready(frm);
        }).addClass('btn-primary');

        frm.add_custom_button(__('Mark Ready for Pickup'), () => {
            frm.set_value('status', 'Ready for Pickup');
            frm.save();
        });
    }

    // Ready for Pickup → Delivered
    if (status === 'Ready for Pickup') {
        frm.add_custom_button(__('Mark as Delivered'), () => {
            // Check payment
            if (frm.doc.payment_status !== 'Paid') {
                frappe.confirm(
                    __('Payment is not complete. Continue anyway?'),
                    () => {
                        mark_as_delivered(frm);
                    }
                );
            } else {
                mark_as_delivered(frm);
            }
        }).addClass('btn-primary');
    }

    // Any status → Put on Hold / Cancel
    if (!['Delivered', 'Cancelled'].includes(status)) {
        frm.add_custom_button(__('Put on Hold'), () => {
            frappe.prompt({
                label: 'Reason',
                fieldname: 'reason',
                fieldtype: 'Small Text',
                reqd: 1
            }, (values) => {
                frm.add_comment('Comment', `Put on hold: ${values.reason}`);
                frm.set_value('status', 'On Hold');
                frm.save();
            }, __('Reason for hold'));
        }, __('Actions'));

        frm.add_custom_button(__('Cancel Order'), () => {
            frappe.prompt({
                label: 'Reason',
                fieldname: 'reason',
                fieldtype: 'Small Text',
                reqd: 1
            }, (values) => {
                frm.add_comment('Comment', `Cancelled: ${values.reason}`);
                frm.set_value('status', 'Cancelled');
                frm.save();
            }, __('Reason for cancellation'));
        }, __('Actions'));
    }

    // On Hold → Resume
    if (status === 'On Hold') {
        frm.add_custom_button(__('Resume Repair'), () => {
            frm.set_value('status', 'In Progress');
            frm.save();
        }).addClass('btn-primary');
    }
}

function add_utility_buttons(frm) {
    // Print Receipt
    frm.add_custom_button(__('Print Receipt'), () => {
        frappe.ui.get_print_settings(false, (print_settings) => {
            let w = window.open(
                frappe.urllib.get_full_url(
                    '/api/method/frappe.utils.print_format.download_pdf?' +
                    'doctype=' + encodeURIComponent('Repair Order') +
                    '&name=' + encodeURIComponent(frm.doc.name) +
                    '&format=Repair Receipt' +
                    '&no_letterhead=0'
                )
            );
            if (!w) {
                frappe.msgprint(__('Please enable pop-ups'));
            }
        });
    }, __('Print'));

    // Call Customer
    if (frm.doc.contact_number) {
        frm.add_custom_button(__('Call Customer'), () => {
            window.location.href = 'tel:' + frm.doc.contact_number;
        }, __('Contact'));
    }

    // Email Customer
    if (frm.doc.email) {
        frm.add_custom_button(__('Email Customer'), () => {
            frappe.call({
                method: 'frappe.core.doctype.communication.email.make',
                args: {
                    recipients: frm.doc.email,
                    subject: `Repair Order ${frm.doc.name}`,
                    content: get_email_template(frm),
                    doctype: 'Repair Order',
                    name: frm.doc.name
                }
            });
        }, __('Contact'));
    }
}

function update_field_permissions(frm) {
    const status = frm.doc.status;
    const locked_statuses = ['Completed', 'Ready for Pickup', 'Delivered', 'Cancelled'];
    const is_locked = locked_statuses.includes(status);

    // Lock customer and device info after initial review
    if (status !== 'Pending Review') {
        frm.set_df_property('customer', 'read_only', 1);
        frm.set_df_property('brand', 'read_only', 1);
        frm.set_df_property('device', 'read_only', 1);
        frm.set_df_property('device_model', 'read_only', 1);
        frm.set_df_property('serial_number', 'read_only', 1);
    }

    // Lock defects after completion
    if (is_locked) {
        frm.set_df_property('defects', 'read_only', 1);
        frm.set_df_property('device_inspection', 'read_only', 1);
    }

    // Lock technician notes after delivery
    if (['Delivered', 'Cancelled'].includes(status)) {
        frm.set_df_property('technician_notes', 'read_only', 1);
        frm.set_df_property('additional_notes', 'read_only', 1);
    }

    // Payment fields only editable in final stages
    const payment_editable = ['Completed', 'Ready for Pickup'].includes(status);
    frm.set_df_property('paid_amount', 'read_only', !payment_editable);
    frm.set_df_property('payment_status', 'read_only', !payment_editable);
}

function add_status_indicator(frm) {
    // Add visual indicator for overdue repairs
    if (frm.doc.expected_completion && frm.doc.status !== 'Delivered') {
        const now = frappe.datetime.now_datetime();
        const expected = frm.doc.expected_completion;

        if (now > expected) {
            const hours_overdue = frappe.datetime.get_hour_diff(now, expected);
            frm.dashboard.add_indicator(
                __('Overdue by {0} hours', [Math.round(hours_overdue)]),
                'red'
            );
        }
    }

    // Payment indicator
    if (frm.doc.payment_status === 'Unpaid' && ['Ready for Pickup', 'Completed'].includes(frm.doc.status)) {
        frm.dashboard.add_indicator(__('Payment Pending'), 'orange');
    }
}

function calculate_totals(frm) {
    let total = 0;

    // Sum defects
    if (frm.doc.defects) {
        frm.doc.defects.forEach(row => {
            // FIX: Use 'selling_price' instead of 'amount'
            total += flt(row.selling_price);
        });
    }

    frm.set_value('total_service_amount', total);

    // Add priority charge
    const priority_charge = flt(frm.doc.priority_charge);

    // Calculate tax (assuming 19% TVA - adjust as needed)
    const tax_rate = 0.19;
    const tax_amount = (total + priority_charge) * tax_rate;

    frm.set_value('tax_amount', tax_amount);
    frm.set_value('grand_total', total + priority_charge + tax_amount);
}

function update_payment_status(frm) {
    const paid = flt(frm.doc.paid_amount);
    const total = flt(frm.doc.grand_total);

    if (paid === 0) {
        frm.set_value('payment_status', 'Unpaid');
    } else if (paid >= total) {
        frm.set_value('payment_status', 'Paid');
    } else {
        frm.set_value('payment_status', 'Partially Paid');
    }
}

function mark_as_delivered(frm) {
    frm.set_value('status', 'Delivered');
    frm.set_value('actual_completion', frappe.datetime.now_datetime());
    frm.save().then(() => {
        frappe.show_alert({
            message: __('Repair Order marked as delivered'),
            indicator: 'green'
        });
    });
}

function show_customer_approval_dialog(frm) {
    frappe.prompt([
        {
            label: 'Message to Customer',
            fieldname: 'message',
            fieldtype: 'Text',
            default: `Dear ${frm.doc.customer_name},\n\nYour ${frm.doc.device} repair requires approval.\n\nTotal Cost: ${format_currency(frm.doc.grand_total)}\n\nPlease confirm to proceed.`
        }
    ], (values) => {
        frappe.call({
            method: 'frappe.core.doctype.communication.email.make',
            args: {
                recipients: frm.doc.email,
                subject: `Approval Required - Repair Order ${frm.doc.name}`,
                content: values.message,
                doctype: 'Repair Order',
                name: frm.doc.name
            },
            callback: () => {
                frm.set_value('status', 'Awaiting Customer Approval');
                frm.save();
                frappe.show_alert({
                    message: __('Approval request sent'),
                    indicator: 'green'
                });
            }
        });
    }, __('Request Customer Approval'));
}

function show_customer_message_dialog(frm, title) {
    frappe.prompt([
        {
            label: 'Message',
            fieldname: 'message',
            fieldtype: 'Text',
            reqd: 1
        }
    ], (values) => {
        frappe.call({
            method: 'frappe.core.doctype.communication.email.make',
            args: {
                recipients: frm.doc.email,
                subject: `${title} - Repair Order ${frm.doc.name}`,
                content: values.message,
                doctype: 'Repair Order',
                name: frm.doc.name
            },
            callback: () => {
                frappe.show_alert({
                    message: __('Message sent'),
                    indicator: 'green'
                });
            }
        });
    }, __(title));
}

function send_approval_reminder(frm) {
    frappe.call({
        method: 'frappe.core.doctype.communication.email.make',
        args: {
            recipients: frm.doc.email,
            subject: `Reminder: Approval Required - ${frm.doc.name}`,
            content: `Dear ${frm.doc.customer_name},\n\nThis is a reminder that your repair order requires approval.\n\nTotal: ${format_currency(frm.doc.grand_total)}`,
            doctype: 'Repair Order',
            name: frm.doc.name
        },
        callback: () => {
            frappe.show_alert({
                message: __('Reminder sent'),
                indicator: 'green'
            });
        }
    });
}

function notify_customer_ready(frm) {
    frappe.call({
        method: 'frappe.core.doctype.communication.email.make',
        args: {
            recipients: frm.doc.email,
            subject: `Your Device is Ready - ${frm.doc.name}`,
            content: `Dear ${frm.doc.customer_name},\n\nGood news! Your ${frm.doc.device} repair is complete and ready for pickup.\n\nTracking ID: ${frm.doc.tracking_id}\nTotal: ${format_currency(frm.doc.grand_total)}`,
            doctype: 'Repair Order',
            name: frm.doc.name
        },
        callback: () => {
            frm.set_value('status', 'Ready for Pickup');
            frm.save();
            frappe.show_alert({
                message: __('Customer notified'),
                indicator: 'green'
            });
        }
    });
}

function get_email_template(frm) {
    return `Dear ${frm.doc.customer_name},

Regarding your repair order ${frm.doc.name}:

Device: ${frm.doc.device}
Status: ${frm.doc.status}
${frm.doc.tracking_id ? 'Tracking ID: ' + frm.doc.tracking_id : ''}

Best regards`;
}

// ========================================
// INSPECTION CHECKLIST FUNCTIONS
// ========================================

function load_inspection_checklist(frm) {
    if (!frm.doc.device) {
        return;
    }

    // Only auto-load if checklist is empty
    if (frm.doc.device_inspection && frm.doc.device_inspection.length > 0) {
        frappe.confirm(
            __('Device inspection checklist already has items. Do you want to replace them with the template for this device?'),
            () => {
                fetch_and_populate_checklist(frm);
            }
        );
        return;
    }

    fetch_and_populate_checklist(frm);
}

function fetch_and_populate_checklist(frm) {
    frappe.call({
        method: 'repairbox.repairbox.doctype.repair_order.repair_order.get_inspection_checklist',
        args: {
            device: frm.doc.device
        },
        callback: function (r) {
            if (r.message && r.message.items && r.message.items.length > 0) {
                // Clear existing items
                frm.clear_table('device_inspection');

                // Add items from template
                r.message.items.forEach(item => {
                    let row = frm.add_child('device_inspection');
                    row.item_name = item.item_name;
                    row.category = item.category;
                    row.is_mandatory = item.is_mandatory;
                    row.status = '';
                    row.is_defective = 0;
                    row.notes = '';
                });

                frm.refresh_field('device_inspection');

                // Render toggle buttons
                render_inspection_toggle_buttons(frm);

                frappe.show_alert({
                    message: __('Inspection checklist loaded from template: {0}', [r.message.template_name]),
                    indicator: 'green'
                });
            } else {
                frappe.show_alert({
                    message: __('No inspection checklist template found for this device'),
                    indicator: 'orange'
                });
            }
        }
    });
}

function render_inspection_toggle_buttons(frm) {
    // Wait for grid to render
    setTimeout(() => {
        const grid = frm.fields_dict.device_inspection.grid;

        // Add quick action buttons above the grid
        add_checklist_quick_actions(frm);

        // Render toggle buttons for each row
        if (grid && grid.grid_rows) {
            grid.grid_rows.forEach((row, idx) => {
                render_row_toggle_buttons(frm, row, idx);
            });
        }
    }, 100);
}

function add_checklist_quick_actions(frm) {
    const wrapper = frm.fields_dict.device_inspection.$wrapper;

    // Remove existing quick actions
    wrapper.find('.checklist-quick-actions').remove();

    // Add quick action buttons
    const quick_actions = $(`
        <div class="checklist-quick-actions" style="margin-bottom: 10px; display: flex; gap: 10px; align-items: center;">
            <span style="font-weight: 500; margin-right: 10px;">${__('Quick Actions')}:</span>
            <button class="btn btn-xs btn-success checklist-all-pass">
                <i class="fa fa-check"></i> ${__('All Pass')}
            </button>
            <button class="btn btn-xs btn-secondary checklist-all-na">
                <i class="fa fa-minus"></i> ${__('All N/A')}
            </button>
            <button class="btn btn-xs btn-default checklist-reset">
                <i class="fa fa-refresh"></i> ${__('Reset')}
            </button>
        </div>
    `);

    wrapper.find('.frappe-control').first().before(quick_actions);

    // Bind events
    quick_actions.find('.checklist-all-pass').on('click', () => {
        set_all_checklist_status(frm, 'Pass');
    });

    quick_actions.find('.checklist-all-na').on('click', () => {
        set_all_checklist_status(frm, 'N/A');
    });

    quick_actions.find('.checklist-reset').on('click', () => {
        set_all_checklist_status(frm, '');
    });
}

function set_all_checklist_status(frm, status) {
    frm.doc.device_inspection.forEach(row => {
        row.status = status;
        row.is_defective = status === 'Fail' ? 1 : 0;
    });
    frm.refresh_field('device_inspection');
    render_inspection_toggle_buttons(frm);
}

function render_row_toggle_buttons(frm, row, idx) {
    if (!row || !row.doc) return;

    const grid_row = row.grid_row || row;
    const $row = $(grid_row);

    // Find the status cell
    const status_field = $row.find('[data-fieldname="status"]');
    if (!status_field.length) return;

    // Hide the default select field
    status_field.find('select, .like-disabled-input').hide();

    // Remove existing toggle buttons
    status_field.find('.inspection-toggle-buttons').remove();

    // Create toggle button group
    const current_status = row.doc.status || '';
    const is_mandatory = row.doc.is_mandatory;

    const toggle_html = `
        <div class="inspection-toggle-buttons" data-idx="${row.doc.idx}" style="display: flex; gap: 4px;">
            <button type="button" class="btn btn-xs inspection-btn inspection-btn-pass ${current_status === 'Pass' ? 'active' : ''}"
                    data-status="Pass" title="${__('Pass')}">
                <i class="fa fa-check"></i>
            </button>
            <button type="button" class="btn btn-xs inspection-btn inspection-btn-fail ${current_status === 'Fail' ? 'active' : ''}"
                    data-status="Fail" title="${__('Fail')}">
                <i class="fa fa-times"></i>
            </button>
            <button type="button" class="btn btn-xs inspection-btn inspection-btn-na ${current_status === 'N/A' ? 'active' : ''}"
                    data-status="N/A" title="${__('N/A')}">
                <i class="fa fa-minus"></i>
            </button>
        </div>
    `;

    status_field.append(toggle_html);

    // Bind click events
    status_field.find('.inspection-btn').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const new_status = $(this).data('status');
        const row_idx = $(this).closest('.inspection-toggle-buttons').data('idx');

        // Update the status
        frappe.model.set_value(row.doc.doctype, row.doc.name, 'status', new_status);

        // Auto-set is_defective based on status
        if (new_status === 'Fail') {
            frappe.model.set_value(row.doc.doctype, row.doc.name, 'is_defective', 1);
        } else {
            frappe.model.set_value(row.doc.doctype, row.doc.name, 'is_defective', 0);
        }

        // Update button states
        $(this).siblings().removeClass('active');
        $(this).addClass('active');
    });

    // Add mandatory indicator styling
    if (is_mandatory) {
        const item_name_field = $row.find('[data-fieldname="item_name"]');
        if (item_name_field.length && !item_name_field.find('.mandatory-indicator').length) {
            item_name_field.find('.like-disabled-input, .static-area').prepend(
                '<span class="mandatory-indicator" style="color: var(--red-500); margin-right: 4px;">*</span>'
            );
        }
    }

    // Add category badge styling
    const category_field = $row.find('[data-fieldname="category"]');
    if (category_field.length) {
        const category = row.doc.category;
        if (category) {
            const category_colors = {
                'Display': '#3498db',
                'Audio': '#9b59b6',
                'Connectivity': '#1abc9c',
                'Battery': '#f39c12',
                'Camera': '#e74c3c',
                'Buttons & Ports': '#34495e',
                'Sensors': '#27ae60',
                'Performance': '#2980b9',
                'Physical Condition': '#8e44ad',
                'Other': '#95a5a6'
            };
            const color = category_colors[category] || '#95a5a6';

            category_field.find('.like-disabled-input, .static-area').each(function () {
                if (!$(this).hasClass('category-styled')) {
                    $(this).addClass('category-styled').css({
                        'background-color': color,
                        'color': 'white',
                        'padding': '2px 8px',
                        'border-radius': '4px',
                        'font-size': '11px',
                        'display': 'inline-block'
                    });
                }
            });
        }
    }
}
