# # Copyright (c) 2026, shiva and contributors
# # For license information, please see license.txt

# # import frappe

# import frappe

# def execute(filters=None):

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def get_columns():

#     columns = [

#         {
#             "label": "SL.NO",
#             "fieldname": "sr_no",
#             "fieldtype": "Int",
#             "width": 70
#         },

#         {
#             "label": "Date",
#             "fieldname": "date",
#             "fieldtype": "Date",
#             "width": 100
#         },

#         {
#             "label": "Equipment",
#             "fieldname": "asset",
#             "fieldtype": "Data",
#             "width": 220
#         },

#         {
#             "label": "Asset Category",
#             "fieldname": "asset_category",
#             "fieldtype": "Data",
#             "width": 220
#         },

#         {
#             "label": "Engine Start",
#             "fieldname": "engine_start",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Engine End",
#             "fieldname": "engine_end",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Engine Hrs",
#             "fieldname": "engine_hours",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Pump Start",
#             "fieldname": "pump_start",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Pump End",
#             "fieldname": "pump_end",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Pump Hrs",
#             "fieldname": "pump_hours",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Concrete Qty",
#             "fieldname": "concrete_qty",
#             "fieldtype": "Float",
#             "width": 130
#         },
#         {
#             "label": "Last Odometer Value",
#             "fieldname": "last_odometer_value",
#             "fieldtype": "Int",
#             "width" : 120
#         },
#         {
#             "label": "Current Odometer value",
#             "fieldname": "current_odometer_value",
#             "fieldtype": "Int",
#             "width" : 120
#         },
#         {
#             "label": "Distance Travelled",
#             "fieldname": "distance_travelled",
#             "fieldtype": "Int",
#             "width" : 120
#         },
#         {
#             "label": "Total Working Hours",
#             "fieldname": "total_working_hours",
#             "fieldtype": "Float",
#             "width" : 120
#         },

#         {
#             "label": "Fuel Qty",
#             "fieldname": "fuel_qty",
#             "fieldtype": "Float",
#             "width": 120
#         },

#         {
#             "label": "Fuel Avg/Hr",
#             "fieldname": "fuel_avg",
#             "fieldtype": "Float",
#             "width": 130
#         },

#         {
#             "label": "Remarks",
#             "fieldname": "remarks",
#             "fieldtype": "Data",
#             "width": 200
#         }
#     ]

#     return columns

# def get_data(filters):

#     filters = filters or {}

#     conditions = ""

#     if filters.get("asset"):
#         conditions += " AND mdl.asset = %(asset)s "

#     if filters.get("from_date"):
#         conditions += " AND mdl.date >= %(from_date)s "

#     if filters.get("to_date"):
#         conditions += " AND mdl.date <= %(to_date)s "

#     if filters.get("asset_category"):
#         conditions += " AND mdl.asset_category = %(asset_category)s "

#     records = frappe.db.sql("""

#         SELECT
#             a.asset_name,
#             mdl.asset_category,
#             mdl.date,
#             mdl.engine_start,
#             mdl.engine_end,
#             mdl.engine_hours,
#             mdl.pump_start,
#             mdl.pump_end,
#             mdl.pump_hours,
#             mdl.concrete_qty,
#             mdl.last_odometer_value,
#             mdl.current_odometer_value,
#             mdl.distance_travelled,
#             mdl.total_working_hours,
#             mdl.fuel_qty,
#             mdl.remarks

#         FROM `tabMachine Daily Log` mdl

#         LEFT JOIN `tabAsset` a
#             ON a.name = mdl.asset

#         WHERE 1=1

#             {conditions}

#         ORDER BY
#             mdl.date ASC

#     """.format(conditions=conditions), filters, as_dict=True)

#     data = []

#     total_engine_hrs = 0
#     total_pump_hrs = 0
#     total_concrete = 0
#     total_distance_travelled = 0
#     total_total_working_hours = 0
#     total_fuel = 0

#     for i, row in enumerate(records, start=1):

#         fuel_avg = 0

#         if row.engine_hours and row.engine_hours > 0:
#             fuel_avg = row.fuel_qty / row.engine_hours

#         data.append({

#             "sr_no": i,

#             "date": row.date,

#             "asset": row.asset_name,

#             "asset_category": row.asset_category,

#             "engine_start": row.engine_start,

#             "engine_end": row.engine_end,

#             "engine_hours": row.engine_hours,

#             "pump_start": row.pump_start,

#             "pump_end": row.pump_end,

#             "pump_hours": row.pump_hours,

#             "concrete_qty": row.concrete_qty,

#             "last_odometer_value": row.last_odometer_value,

#             "current_odometer_value" : row.current_odometer_value,

#             "distance_travelled" : row.distance_travelled,

#             "total_working_hours" : row.total_working_hours,

#             "fuel_qty": row.fuel_qty,

#             "fuel_avg": round(fuel_avg, 2),

#             "remarks": row.remarks
#         })

#         total_engine_hrs += row.engine_hours or 0
#         total_pump_hrs += row.pump_hours or 0
#         total_concrete += row.concrete_qty or 0
#         total_distance_travelled += row.distance_travelled or 0
#         total_total_working_hours += row.total_working_hours or 0
#         total_fuel += row.fuel_qty or 0

#     total_avg = 0

#     if total_engine_hrs > 0:
#         total_avg = total_fuel / total_engine_hrs

#     data.append({

#         "asset": "TOTAL",

#         "engine_hours": total_engine_hrs,

#         "pump_hours": total_pump_hrs,

#         "concrete_qty": total_concrete,

#         "distance_travelled": total_distance_travelled,

#         "total_working_hours": total_total_working_hours,

#         "fuel_qty": total_fuel,

#         "fuel_avg": round(total_avg, 2)
#     })

#     return data

# Copyright (c) 2026, shiva and contributors
# For license information, please see license.txt

# import frappe

import frappe

def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    columns = [

        {
            "label": "SL.NO",
            "fieldname": "sr_no",
            "fieldtype": "Int",
            "width": 70
        },

        {
            "label": "Date Time",
            "fieldname": "date",
            "fieldtype": "Datetime",
            "width": 180
        },

        {
            "label": "Equipment",
            "fieldname": "asset",
            "fieldtype": "link",
            "options" :  "Asset",
            "width": 220
        },
        {
            "label": "Model",
            "fieldname": "model",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "Make",
            "fieldname": "make",
            "fieldtype": "Data",
            "width": 220
        },

        {
            "label": "Asset Category",
            "fieldname": "asset_category",
            "fieldtype": "Data",
            "width": 220
        },

        {
            "label": "Engine Start",
            "fieldname": "engine_start",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Engine End",
            "fieldname": "engine_end",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Engine Hrs",
            "fieldname": "engine_hours",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Pump Start",
            "fieldname": "pump_start",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Pump End",
            "fieldname": "pump_end",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Pump Hrs",
            "fieldname": "pump_hours",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Concrete Qty",
            "fieldname": "concrete_qty",
            "fieldtype": "Float",
            "width": 130
        },

        {
            "label": "Fuel Qty",
            "fieldname": "fuel_qty",
            "fieldtype": "Float",
            "width": 120
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
            "width": 120
        },


        {
            "label": "Fuel Avg/Hr",
            "fieldname": "fuel_avg",
            "fieldtype": "Float",
            "width": 130
        },

        {
            "label": "Remarks",
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 200
        }
    ]

    return columns

def get_data(filters):

    filters = filters or {}

    conditions = ""

    if filters.get("asset"):
        conditions += " AND mdl.asset = %(asset)s "

    if filters.get("from_datetime"):
        conditions += " AND mdl.date >= %(from_datetime)s "

    if filters.get("to_datetime"):
        conditions += " AND mdl.date <= %(to_datetime)s "

    if filters.get("asset_category"):
        conditions += " AND mdl.asset_category = %(asset_category)s "

    

    records = frappe.db.sql("""

        SELECT
            a.asset_name,
            mdl.model,
            mdl.make,
            mdl.asset_category,
            mdl.date,
            mdl.engine_start,
            mdl.engine_end,
            mdl.engine_hours,
            mdl.pump_start,
            mdl.pump_end,
            mdl.pump_hours,
            mdl.concrete_qty,
            mdl.rate,
            mdl.amount,
            mdl.fuel_qty,
            mdl.remarks

        FROM `tabMachine Daily Log` mdl

        LEFT JOIN `tabAsset` a
            ON a.name = mdl.asset

        WHERE 1=1

            {conditions}

        ORDER BY
            mdl.date ASC

    """.format(conditions=conditions), filters, as_dict=True)

    data = []

    total_engine_hrs = 0
    total_pump_hrs = 0
    total_concrete = 0
    total_distance_travelled = 0
    total_total_working_hours = 0
    total_fuel = 0

    for i, row in enumerate(records, start=1):

        fuel_avg = 0

        if row.engine_hours and row.engine_hours > 0:
            fuel_avg = row.fuel_qty / row.engine_hours

        data.append({

            "sr_no": i,

            "date": row.date,

            "asset": row.asset_name,

            "model": row.model,

            "make": row.make,

            "asset_category": row.asset_category,

            "engine_start": row.engine_start,

            "engine_end": row.engine_end,

            "engine_hours": row.engine_hours,

            "pump_start": row.pump_start,

            "pump_end": row.pump_end,

            "pump_hours": row.pump_hours,

            "concrete_qty": row.concrete_qty,

           # "last_odometer_value": row.last_odometer_value,

           # "current_odometer_value" : row.current_odometer_value,

           # "distance_travelled" : row.distance_travelled,

           # "total_working_hours" : row.total_working_hours,

            "rate":row.rate,

            "amount": row.amount,

            "fuel_qty": row.fuel_qty,

            "fuel_avg": round(fuel_avg, 2),

            "remarks": row.remarks
        })

        total_engine_hrs += row.engine_hours or 0
        total_pump_hrs += row.pump_hours or 0
        total_concrete += row.concrete_qty or 0
        total_distance_travelled += row.distance_travelled or 0
        total_total_working_hours += row.total_working_hours or 0
        total_fuel += row.fuel_qty or 0

    total_avg = 0

    if total_engine_hrs > 0:
        total_avg = total_fuel / total_engine_hrs

    data.append({

        "asset": "TOTAL",

        "engine_hours": total_engine_hrs,

        "pump_hours": total_pump_hrs,

        "concrete_qty": total_concrete,

        "distance_travelled": total_distance_travelled,

        "total_working_hours": total_total_working_hours,

        "fuel_qty": total_fuel,

        "fuel_avg": round(total_avg, 2)
    })

    return data
