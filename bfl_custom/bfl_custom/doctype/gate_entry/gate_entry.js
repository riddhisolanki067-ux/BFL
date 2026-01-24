frappe.ui.form.on("GATE ENTRY", {
    refresh:function(frm) {
       console.log("ass")
            frm.add_custom_button(("Purchase Invoice"),
                function() {
                    frappe.call({
                        method: "bfl_custom.bfl_custom.doctype.gate_entry.gate_entry.make_purchase_invoice",
                        args: {
                            gate_entry: frm.doc.name
                        },
                        callback(r) {
                            if (r.message) {
                                frappe.set_route("Form", "Purchase Invoice", r.message);
                            }
                        }
                    });
                },
                __("Create")
            );
        }
    
}); 