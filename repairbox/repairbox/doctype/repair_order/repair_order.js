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
