# Copyright (c) 2026, shiva and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2026, shiva and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


# --------------------------------------------------------
# COLUMNS
# --------------------------------------------------------

def get_columns(filters):

    filters = filters or {}

    columns = [

        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Workorder",
            "fieldname": "workorder",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Workorder Date",
            "fieldname": "wo_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "PR NO",
            "fieldname": "pr_no",
            "fieldtype": "Int",
            "width": 120
        },

        {
            "label": "PR Date",
            "fieldname": "pr_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "PO NO",
            "fieldname": "po_no",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "PO Date",
            "fieldname": "po_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "Vendor",
            "fieldname": "vendor",
            "fieldtype": "Link",
            "options" : "Supplier",
            "width": 120
        },
        
        {
            "label": "Asset",
            "fieldname": "asset_name",
            "fieldtype": "Link",
            "options" : "Asset",
            "width": 220
        },
        {
            "label": "Asset Category",
            "fieldname": "asset_category",
            "fieldtype": "Link",
            "options": "Asset Category",
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

    ]
    if filters.get("maintenance_category") == "Breakdown":

        columns.extend([
            {
                  "label": "Breakdown Start",
                  "fieldname": "breakdown_start",
                  "fieldtype": "Datetime",
                  "width": 170
            },
            {
                  "label": "Breakdown End",
                  "fieldname": "breakdown_end",
                  "fieldtype": "Datetime",
                  "width": 170
            },
            {
                  "label": "Non Working Hours",
                  "fieldname": "non_working_hours",
                  "fieldtype": "Float",
                  "width": 150
            }
        ])

    else:

        columns.extend([
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
                }
        ])

    columns.extend([

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
            "label": "HSN Code",
            "fieldname": "hsn_code",
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
    ])

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

    if filters.get("asset_category"):
        conditions += " AND mm.asset_category = %(asset_category)s "

    if filters.get("maintenance_category"):
        conditions += " AND mm.maintenance_category = %(maintenance_category)s "

    if filters.get("maintenance_type"):
        conditions += " AND mmi.maintenance_type = %(maintenance_type)s "

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
            mm.asset_category,
            mm.maintenance_category,
            mm.next_service_due,
            mm.next_lubricant_due,
            mm.breakdown_start,
            mm.breakdown_end,
            mm.non_working_hours,
            mm.maintenance_category,
            mmi.maintenance_type,
            mmi.vendor,
            mmi.workorder,
            mmi.wo_date,
            mmi.pr_no,
            mmi.pr_date,
            mmi.po_no,
            mmi.po_date,
            mmi.item_code,
            mmi.uom,
            mmi.hsn_code,
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
                AND mm.asset_category = %s
                AND mm.maintenance_category = %s
                AND mmi.maintenance_type = %s
                AND mmi.item_code = %s
                AND mm.date < %s

            ORDER BY
                mm.date DESC

            LIMIT 1

        """, (
            
            row.asset,
            row.asset_category,
            row.maintenance_category,
            row.maintenance_type,
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
                    AND asset_category =%s
                    AND date > %s
                    AND date <= %s

            """, (
                row.asset,
                row.asset_category,
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

        row_data = {
                "date": row.date,
                "workorder": row.workorder,
                "wo_date": row.wo_date,
                "pr_no": row.pr_no,
                "pr_date": row.pr_date,
                "po_no": row.po_no,
                "po_date": row.po_date,
                "vendor": row.vendor,
                "asset_name": row.asset_name,
                "asset_category": row.asset_category,
                "engine_hrs": engine_hrs,
                "pump_hrs": pump_hrs,
                "maintenance_type": row.maintenance_type,
                "item_code": row.item_code,
                "uom": row.uom,
                "hsn_code": row.hsn_code,
                "qty": row.qty,
                "rate": row.rate,
                "amount": row.amount,
               "remarks": row.remarks
            }

        if row.maintenance_category == "Breakdown":
            row_data.update({
                "breakdown_start": row.breakdown_start,
                "breakdown_end": row.breakdown_end,
                "non_working_hours": row.non_working_hours
            })
        else:
            row_data.update({
                "next_service_due": row.next_service_due,
                "next_lubricant_due": row.next_lubricant_due
            })

        data.append(row_data)
        total_amount += (row.amount or 0)
    # --------------------------------------------------------
    # TOTAL ROW
    # --------------------------------------------------------

    data.append({
    "asset_name": "TOTAL",
    "amount": total_amount
    })
    return data
