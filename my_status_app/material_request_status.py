import frappe

# -----------------------------
# Update Material Request Status
# -----------------------------
def update_material_request_status(mr_name):
    """
    Updates the custom PO status of a Material Request based on item quantities.
    Only for Purchase type MRs.
    """
    if not mr_name:
        return

    mr = frappe.get_doc("Material Request", mr_name)

    # Only update Purchase type MRs
    if mr.material_request_type != "Purchase":
        # Clear if set incorrectly
        if mr.custom_po_status:
            frappe.db.set_value("Material Request", mr.name, "custom_po_status", "")
        return

    total_qty = ordered_qty = received_qty = 0
    for row in mr.items:
        total_qty += row.qty or 0
        ordered_qty += row.ordered_qty or 0
        received_qty += row.received_qty or 0

    # Determine PO status
    if received_qty >= total_qty and total_qty > 0:
        status = "Received"
    elif received_qty > 0:
        status = "Partially Received"
    elif ordered_qty >= total_qty and total_qty > 0:
        status = "Ordered"
    elif ordered_qty > 0:
        status = "Partially Ordered"
    else:
        status = "Pending"

    # Only update if changed
    if mr.custom_po_status != status:
        frappe.db.set_value("Material Request", mr.name, "custom_po_status", status)
        # Sync status to linked indents
        sync_po_status_to_indent(mr.name)


# -----------------------------
# Sync MR status to Indents
# -----------------------------
def sync_po_status_to_indent(mr_name):
    """
    Sync the custom PO status from Material Request to all linked Material Request Indent(s)
    """
    po_status = frappe.db.get_value("Material Request", mr_name, "custom_po_status") or ""

    indents = frappe.get_all(
        "Material Request Indent",
        filters={"material_request": mr_name},
        fields=["name", "po_status"]
    )

    for indent in indents:
        if indent.po_status != po_status:
            frappe.db.set_value("Material Request Indent", indent.name, "po_status", po_status)


# -----------------------------
# Sync Indent update to MR status
# -----------------------------
def sync_po_status_on_indent_update(doc, method):
    """
    Sync Material Request Indent's po_status to match parent MR's custom_po_status.
    Trigger: on_update of Material Request Indent
    """
    if not doc.material_request:
        return

    po_status = frappe.db.get_value("Material Request", doc.material_request, "custom_po_status") or ""

    if doc.po_status != po_status:
        frappe.db.set_value("Material Request Indent", doc.name, "po_status", po_status)


# -----------------------------
# Trigger: Purchase Order Update
# -----------------------------
def po_update(doc, method):
    """
    Trigger: on_submit / on_cancel of Purchase Order
    Updates all linked Purchase type Material Requests.
    """
    for item in doc.items:
        if item.material_request:
            mr_type = frappe.db.get_value("Material Request", item.material_request, "material_request_type")
            if mr_type == "Purchase":
                update_material_request_status(item.material_request)


# -----------------------------
# Trigger: Purchase Receipt Update
# -----------------------------
def pr_update(doc, method):
    """
    Trigger: on_submit / on_cancel of Purchase Receipt
    Updates all linked Purchase type Material Requests.
    """
    for item in doc.items:
        if item.material_request:
            mr_type = frappe.db.get_value("Material Request", item.material_request, "material_request_type")
            if mr_type == "Purchase":
                update_material_request_status(item.material_request)


# -----------------------------
# Clear PO Status for Non-Purchase MR
# -----------------------------
def clear_po_status_for_non_purchase(doc, method):
    """
    Trigger: before_save of Material Request
    Clears custom_po_status if MR is not of type Purchase.
    """
    if doc.material_request_type != "Purchase" and doc.custom_po_status:
        doc.custom_po_status = ""  # Use doc field instead of db.set_value
