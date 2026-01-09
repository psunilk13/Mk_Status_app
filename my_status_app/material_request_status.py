import frappe


def update_material_request_status(mr_name):
    if not mr_name:
        return

    mr = frappe.get_doc("Material Request", mr_name)

    # ✅ SAME CONDITION AS DEPENDS ON (Python way)
    if mr.material_request_type != "Purchase":
        # Clear PO status for non-purchase MRs
        if mr.custom_po_status:
            frappe.db.set_value(
                "Material Request",
                mr.name,
                "custom_po_status",
                ""
            )
        return

    total_qty = 0
    ordered_qty = 0
    received_qty = 0

    for row in mr.items:
        total_qty += row.qty or 0
        ordered_qty += row.ordered_qty or 0
        received_qty += row.received_qty or 0

    # 🔹 RECEIPT STATUS (highest priority)
    if received_qty > 0 and received_qty < total_qty:
        status = "Partially Received"
    elif received_qty >= total_qty and total_qty > 0:
        status = "Received"

    # 🔹 ORDER STATUS
    else:
        if ordered_qty == 0:
            status = "Pending"
        elif ordered_qty >= total_qty:
            status = "Ordered"
        else:
            status = "Partially Ordered"

    # Update only if changed
    if mr.custom_po_status != status:
        frappe.db.set_value(
            "Material Request",
            mr.name,
            "custom_po_status",
            status
        )


def po_update(doc, method):
    for item in doc.items:
        if item.material_request:
            update_material_request_status(item.material_request)


def pr_update(doc, method):
    for item in doc.items:
        if item.material_request:
            update_material_request_status(item.material_request)

def clear_po_status_for_non_purchase(doc, method):
    if doc.material_request_type != "Purchase":
        doc.custom_po_status = ""
