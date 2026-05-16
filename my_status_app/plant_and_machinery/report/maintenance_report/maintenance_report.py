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