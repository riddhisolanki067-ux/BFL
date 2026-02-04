# Copyright (c) 2026, r and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class GATEENTRY(Document):
    pass


import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_purchase_invoice(gate_entry):
    gate_entry_doc = frappe.get_doc("GATE ENTRY", gate_entry)

    if not gate_entry_doc.supplier:
        frappe.throw("Supplier is mandatory to create Purchase Invoice")

    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = gate_entry_doc.supplier
    pi.posting_date = frappe.utils.today()
    pi.due_date = frappe.utils.today()
    pi.set_posting_time = 1
    pi.update_stock = 1
    pi.custom_gate_entry = gate_entry_doc.name
    # optional link field

    for row in gate_entry_doc.item:
        pi.append("items", {
            "item_code": row.product,
            "qty": row.qty,    
            "rate": row.value or 0,
            
        })

    pi.insert(ignore_permissions=True)
    gate_entry_doc.purchase_invoice = pi.name
    gate_entry_doc.save(ignore_permissions=True)

    frappe.db.commit()
    


    return pi.name