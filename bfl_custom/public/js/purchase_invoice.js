frappe.ui.form.on('Purchase Invoice', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Purchase Comparison'), () => {
                frappe.set_route(
                    'purchase-comparision',
                    { pi: frm.doc.name }
                );
            });
            

        }
    }
});
