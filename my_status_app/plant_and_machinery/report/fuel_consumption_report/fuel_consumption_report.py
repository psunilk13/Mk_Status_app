# Copyright (c) 2026, shiva and contributors
# For license information, please see license.txt

# import fra
import frappe
from collections import defaultdict

def execute(filters=None):

    columns = []
    data = []

    report_type = filters.get("report_type")

    conditions = ""

    if filters.get("asset"):
        conditions += " AND mdl.asset = %(asset)s "

    if filters.get("asset_category"):
        conditions += " AND mdl.asset_category = %(asset_category)s "

    if filters.get("from_date"):
        conditions += " AND mdl.date >= %(from_date)s "

    if filters.get("to_date"):
        conditions += " AND mdl.date <= %(to_date)s "

    # ------------------------
    # GET DATES
    # ------------------------

    dates = frappe.db.sql("""

    SELECT DISTINCT mdl.date

    FROM `tabMachine Daily Log` mdl

    WHERE 1=1

        {conditions}

    ORDER BY
        mdl.date

""".format(conditions=conditions), filters, as_dict=True)


    # ------------------------
    # COLUMNS
    # ------------------------

    columns.append({
    "label": "Equipment",
    "fieldname": "asset",
    "fieldtype": "Data",
    "width": 220
    })

    columns.append({
    "label": "Asset Category",
    "fieldname": "asset_category",
    "fieldtype": "Data",
    "width": 220
    })

    date_list = []

    for d in dates:

        date_str = str(d.date)

        date_list.append(date_str)

        columns.append({
            "label": date_str,
            "fieldname": date_str,
            "fieldtype": "Float",
            "width": 110
        })

    columns.extend([

        {
            "label": "Total Hrs",
            "fieldname": "total_hrs",
            "fieldtype": "Float",
            "width": 130
        },

        {
            "label": "Total Fuel",
            "fieldname": "total_fuel",
            "fieldtype": "Float",
            "width": 130
        },

        {
            "label": "Avg Con",
            "fieldname": "avg_con",
            "fieldtype": "Float",
            "width": 130
        }
    ])

    # ------------------------
    # FETCH DATA
    # ------------------------

    records = frappe.db.sql("""

    SELECT
        a.asset_name,
        mdl.asset_category,
        mdl.date,
        mdl.engine_hours,
        mdl.fuel_qty

    FROM `tabMachine Daily Log` mdl

    LEFT JOIN `tabAsset` a
        ON a.name = mdl.asset

    WHERE 1=1

        {conditions}

    ORDER BY
        a.asset_name,
        mdl.date

""".format(conditions=conditions), filters, as_dict=True)


    # ------------------------
    # GROUPING
    # ------------------------

    asset_map = defaultdict(dict)

    totals_map = defaultdict(lambda: {
        "hrs": 0,
        "fuel": 0
    })

    for row in records:

        asset_key = (
           row.asset_name,
           row.asset_category
        )

        date_str = str(row.date)

        hrs = row.engine_hours or 0
        fuel = row.fuel_qty or 0

        # FILTER DISPLAY VALUE

        if report_type == "Engine Hours":
            value = hrs
        else:
            value = fuel

        asset_map[asset_key][date_str] = value

        totals_map[asset_key]["hrs"] += hrs
        totals_map[asset_key]["fuel"] += fuel

    # ------------------------
    # ROWS
    # ------------------------

    grand_hrs = 0
    grand_fuel = 0

    for asset_key, values in asset_map.items():

        asset_name, asset_category = asset_key

        row = {
        "asset": asset_name,
        "asset_category": asset_category
        }

        for d in date_list:
            row[d] = values.get(d, 0)

        total_hrs = totals_map[asset_key]["hrs"]
        total_fuel = totals_map[asset_key]["fuel"]

        avg = 0

        if total_hrs > 0:
            avg = total_fuel / total_hrs

        row["total_hrs"] = total_hrs
        row["total_fuel"] = total_fuel
        row["avg_con"] = round(avg, 2)

        grand_hrs += total_hrs
        grand_fuel += total_fuel

        data.append(row)

    # ------------------------
    # TOTAL ROW
    # ------------------------

    total_row = {
        "asset": "TOTAL"
    }

    for d in date_list:

        day_total = 0

        for row in data:
            day_total += row.get(d, 0)

        total_row[d] = day_total

    total_row["total_hrs"] = grand_hrs
    total_row["total_fuel"] = grand_fuel

    if grand_hrs > 0:
        total_row["avg_con"] = round(
            grand_fuel / grand_hrs,
            2
        )
    else:
        total_row["avg_con"] = 0

    data.append(total_row)

    return columns, data
