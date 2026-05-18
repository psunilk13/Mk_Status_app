#--------------------------------WITHOUT STOPPING AND RE-OPENED FLOW------------------
# import frappe

# # -----------------------------
# # Update Material Request Status
# # -----------------------------
# def update_material_request_status(mr_name):
#     """
#     Updates the custom PO status of a Material Request based on item quantities.
#     Only for Purchase type MRs.
#     """
#     if not mr_name:
#         return

#     mr = frappe.get_doc("Material Request", mr_name)

#     # Only update Purchase type MRs
#     if mr.material_request_type != "Purchase":
#         # Clear if set incorrectly
#         if mr.custom_po_status:
#             frappe.db.set_value("Material Request", mr.name, "custom_po_status", "")
#         return

#     total_qty = ordered_qty = received_qty = 0
#     for row in mr.items:
#         total_qty += row.qty or 0
#         ordered_qty += row.ordered_qty or 0
#         received_qty += row.received_qty or 0

#     # Determine PO status
#     if received_qty >= total_qty and total_qty > 0:
#         status = "Received"
#     elif received_qty > 0:
#         status = "Partially Received"
#     elif ordered_qty >= total_qty and total_qty > 0:
#         status = "Ordered"
#     elif ordered_qty > 0:
#         status = "Partially Ordered"
#     else:
#         status = "Pending"

#     # Only update if changed
#     if mr.custom_po_status != status:
#         frappe.db.set_value("Material Request", mr.name, "custom_po_status", status)
#         # Sync status to linked indents
#         sync_po_status_to_indent(mr.name)


# # -----------------------------
# # Sync MR status to Indents
# # -----------------------------
# def sync_po_status_to_indent(mr_name):
#     """
#     Sync the custom PO status from Material Request to all linked Material Request Indent(s)
#     """
#     po_status = frappe.db.get_value("Material Request", mr_name, "custom_po_status") or ""

#     indents = frappe.get_all(
#         "Material Request Indent",
#         filters={"material_request": mr_name},
#         fields=["name", "po_status"]
#     )

#     for indent in indents:
#         if indent.po_status != po_status:
#             frappe.db.set_value("Material Request Indent", indent.name, "po_status", po_status)


# # -----------------------------
# # Sync Indent update to MR status
# # -----------------------------
# def sync_po_status_on_indent_update(doc, method):
#     """
#     Sync Material Request Indent's po_status to match parent MR's custom_po_status.
#     Trigger: on_update of Material Request Indent
#     """
#     if not doc.material_request:
#         return

#     po_status = frappe.db.get_value("Material Request", doc.material_request, "custom_po_status") or ""

#     if doc.po_status != po_status:
#         frappe.db.set_value("Material Request Indent", doc.name, "po_status", po_status)


# # -----------------------------
# # Trigger: Purchase Order Update
# # -----------------------------
# def po_update(doc, method):
#     """
#     Trigger: on_submit / on_cancel of Purchase Order
#     Updates all linked Purchase type Material Requests.
#     """
#     for item in doc.items:
#         if item.material_request:
#             mr_type = frappe.db.get_value("Material Request", item.material_request, "material_request_type")
#             if mr_type == "Purchase":
#                 update_material_request_status(item.material_request)


# # -----------------------------
# # Trigger: Purchase Receipt Update
# # -----------------------------
# def pr_update(doc, method):
#     """
#     Trigger: on_submit / on_cancel of Purchase Receipt
#     Updates all linked Purchase type Material Requests.
#     """
#     for item in doc.items:
#         if item.material_request:
#             mr_type = frappe.db.get_value("Material Request", item.material_request, "material_request_type")
#             if mr_type == "Purchase":
#                 update_material_request_status(item.material_request)


# # -----------------------------
# # Clear PO Status for Non-Purchase MR
# # -----------------------------
# def clear_po_status_for_non_purchase(doc, method):
#     """
#     Trigger: before_save of Material Request
#     Clears custom_po_status if MR is not of type Purchase.
#     """
#     if doc.material_request_type != "Purchase" and doc.custom_po_status:
#         doc.custom_po_status = ""  # Use doc field instead of db.set_value

#--------------------------------WITH STOPPING AND RE-OPENED FLOW------------------
import frappe

# -----------------------------
# Update Material Request Status
# -----------------------------
def update_material_request_status(mr_name):
    if not mr_name:
        return

    mr = frappe.get_doc("Material Request", mr_name)

    # Only update Purchase type MRs
    if mr.material_request_type != "Purchase":
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

    # Update only if changed
    if mr.custom_po_status != status:
        frappe.db.set_value("Material Request", mr.name, "custom_po_status", status)

        # Sync to Indent
        sync_po_status_to_indent(mr.name)


# -----------------------------
# Sync MR status to Indents
# -----------------------------
def sync_po_status_to_indent(mr_name):
    po_status = frappe.db.get_value("Material Request", mr_name, "custom_po_status") or ""

    indents = frappe.get_all(
        "Material Request Indent",
        filters={"material_request": mr_name},
        fields=["name", "po_status"]
    )

    for indent in indents:

        # 🚫 DO NOT OVERRIDE IF STOPPED
        if indent.po_status == "Stopped":
            continue

        if indent.po_status != po_status:
            frappe.db.set_value(
                "Material Request Indent",
                indent.name,
                "po_status",
                po_status
            )


# -----------------------------
# Sync Indent update to MR status
# -----------------------------
def sync_po_status_on_indent_update(doc, method):
    """
    Sync MR status to Indent ONLY if not manually stopped
    """

    if not doc.material_request:
        return

    # 🚫 IMPORTANT FIX: DO NOT OVERRIDE STOPPED
    if doc.po_status == "Stopped":
        return

    po_status = frappe.db.get_value(
        "Material Request",
        doc.material_request,
        "custom_po_status"
    ) or ""

    if doc.po_status != po_status:
        frappe.db.set_value(
            "Material Request Indent",
            doc.name,
            "po_status",
            po_status
        )


# -----------------------------
# Trigger: Purchase Order Update
# -----------------------------
def po_update(doc, method):
    for item in doc.items:
        if item.material_request:
            mr_type = frappe.db.get_value(
                "Material Request",
                item.material_request,
                "material_request_type"
            )
            if mr_type == "Purchase":
                update_material_request_status(item.material_request)


# -----------------------------
# Trigger: Purchase Receipt Update
# -----------------------------
def pr_update(doc, method):
    for item in doc.items:
        if item.material_request:
            mr_type = frappe.db.get_value(
                "Material Request",
                item.material_request,
                "material_request_type"
            )
            if mr_type == "Purchase":
                update_material_request_status(item.material_request)


# -----------------------------
# Clear PO Status for Non-Purchase MR
# -----------------------------
def clear_po_status_for_non_purchase(doc, method):
    if doc.material_request_type != "Purchase" and doc.custom_po_status:
        doc.custom_po_status = ""

# Copyright (c) 2026, shiva and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2026, shiva and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# --------------------------------------------------------
# COLUMNS
# --------------------------------------------------------

def get_columns():

    columns = [

        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": "Asset",
            "fieldname": "asset_name",
            "fieldtype": "Data",
            "width": 220
        },

        {
            "label": "Engine Hrs",
            "fieldname": "engine_hrs",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Pump Hrs",
            "fieldname": "pump_hrs",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Next Service Due",
            "fieldname": "next_service_due",
            "fieldtype": "Datetime",
            "width": 170
        },

        {
            "label": "Next Lubricant Due",
            "fieldname": "next_lubricant_due",
            "fieldtype": "Datetime",
            "width": 170
        },

        {
            "label": "Maintenance Type",
            "fieldname": "maintenance_type",
            "fieldtype": "Data",
            "width": 150
        },

        {
            "label": "Maintenance Item",
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 220
        },

        {
            "label": "UOM",
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 90
        },

        {
            "label": "Qty",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100
        },

        {
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120
        },

        {
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 130
        },

        {
            "label": "Remarks",
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 220
        }
    ]

    return columns


# --------------------------------------------------------
# DATA
# --------------------------------------------------------

def get_data(filters):

    filters = filters or {}

    conditions = ""
    date_conditions = ""

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    if filters.get("asset"):
        conditions += " AND mm.asset = %(asset)s "

    if filters.get("item_code"):
        conditions += " AND mmi.item_code = %(item_code)s "

    # DATE FILTER

    if (
        filters.get("from_date")
        and filters.get("to_date")
    ):

        date_conditions += """

            AND mm.date BETWEEN %(from_date)s
            AND %(to_date)s

        """

    # --------------------------------------------------------
    # MAIN QUERY
    # --------------------------------------------------------

    records = frappe.db.sql("""

        SELECT

            mm.name,
            mm.date,
            a.asset_name,
            mm.asset,
            mm.next_service_due,
            mm.next_lubricant_due,

            mmi.maintenance_type,
            mmi.item_code,
            mmi.uom,
            mmi.qty,
            mmi.rate,
            mmi.amount,
            mmi.remarks

        FROM `tabMachine Maintenance` mm

        LEFT JOIN `tabMachine Maintenance Item` mmi
            ON mmi.parent = mm.name

        LEFT JOIN `tabAsset` a
            ON a.name = mm.asset

        WHERE
            1=1

            {date_conditions}

            {conditions}

        ORDER BY
            mm.date ASC

    """.format(
        conditions=conditions,
        date_conditions=date_conditions
    ), filters, as_dict=True)

    data = []

    total_amount = 0

    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------

    for row in records:

        previous = frappe.db.sql("""

            SELECT
                mm.date

            FROM `tabMachine Maintenance` mm

            LEFT JOIN `tabMachine Maintenance Item` mmi
                ON mmi.parent = mm.name

            WHERE
                mm.asset = %s
                AND mmi.item_code = %s
                AND mm.date < %s

            ORDER BY
                mm.date DESC

            LIMIT 1

        """, (
            row.asset,
            row.item_code,
            row.date
        ), as_dict=True)

        engine_hrs = 0
        pump_hrs = 0

        # --------------------------------------------------------
        # CALCULATE HOURS
        # --------------------------------------------------------

        if previous:

            previous_date = previous[0].date

            hrs = frappe.db.sql("""

                SELECT

                    SUM(engine_hours) AS engine_hrs,
                    SUM(pump_hours) AS pump_hrs

                FROM `tabMachine Daily Log`

                WHERE
                    asset = %s
                    AND date > %s
                    AND date <= %s

            """, (
                row.asset,
                previous_date,
                row.date
            ), as_dict=True)

            if hrs:

                engine_hrs = (
                    hrs[0].engine_hrs or 0
                )

                pump_hrs = (
                    hrs[0].pump_hrs or 0
                )

        data.append({

            "date": row.date,

            "asset_name": row.asset_name,

            "engine_hrs": engine_hrs,

            "pump_hrs": pump_hrs,

            "next_service_due":
                row.next_service_due,

            "next_lubricant_due":
                row.next_lubricant_due,

            "maintenance_type":
                row.maintenance_type,

            "item_code":
                row.item_code,

            "uom":
                row.uom,

            "qty":
                row.qty,

            "rate":
                row.rate,

            "amount":
                row.amount,

            "remarks":
                row.remarks
        })

        total_amount += (
            row.amount or 0
        )

    # --------------------------------------------------------
    # TOTAL ROW
    # --------------------------------------------------------

    data.append({

        "date": "TOTAL",

        "amount": total_amount

    })

    return data
