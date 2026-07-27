import frappe

@frappe.whitelist()
def get_columns():
    return [
        {"label": "SL.NO", "fieldname": "sr_no", "fieldtype": "Int", "width": 70},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Time", "fieldname": "time", "fieldtype": "Time", "width": 100},
        {"label": "Asset", "fieldname": "asset", "fieldtype": "Data", "width": 220},
        {"label": "Make", "fieldname": "make", "fieldtype": "Data", "width": 220},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 220},
        {"label": "Engine Start", "fieldname": "engine_start", "fieldtype": "Float", "width": 120},
        {"label": "Engine End", "fieldname": "engine_end", "fieldtype": "Float", "width": 120},
        {"label": "Engine Hrs", "fieldname": "engine_hours", "fieldtype": "Float", "width": 120},
        {"label": "Pump Start", "fieldname": "pump_start", "fieldtype": "Float", "width": 120},
        {"label": "Pump End", "fieldname": "pump_end", "fieldtype": "Float", "width": 120},
        {"label": "Pump Hrs", "fieldname": "pump_hours", "fieldtype": "Float", "width": 120},
        {"label": "Concrete Qty", "fieldname": "concrete_qty", "fieldtype": "Float", "width": 130},
        {"label": "Fuel Qty", "fieldname": "fuel_qty", "fieldtype": "Float", "width": 120},
        {"label": "HSN Code", "fieldname": "hsn_code", "fieldtype": "Data", "width": 120},
        {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "Fuel Avg/Hr", "fieldname": "fuel_avg", "fieldtype": "Float", "width": 130},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 200},
    ]
def get_daily_operational_report(filters=None):

    if isinstance(filters, str):
        filters = frappe.parse_json(filters)

    filters = filters or {}

    conditions = ""

    if filters.get("asset"):
        conditions += " AND mdl.asset = %(asset)s"

    if filters.get("asset_category"):
        conditions += " AND a.asset_category = %(asset_category)s"

    if filters.get("from_date"):
        conditions += " AND mdl.date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND mdl.date <= %(to_date)s"

    records = frappe.db.sql(f"""
        SELECT

            a.asset_name,

            mdl.date,

            mdl.time,

            mdl.make,

            mdl.model,

            mdl.engine_start,

            mdl.engine_end,

            mdl.engine_hours,

            mdl.pump_start,

            mdl.pump_end,

            mdl.pump_hours,

            mdl.concrete_qty,

            mdl.fuel_qty,

            mdl.hsn_code,

            mdl.rate,

            mdl.amount,

            mdl.remarks

        FROM `tabMachine Daily Log` mdl

        LEFT JOIN `tabAsset` a
            ON a.name = mdl.asset

        WHERE 1=1

        {conditions}

        ORDER BY mdl.date ASC

    """, filters, as_dict=True)

    data = []

    total_engine = 0
    total_pump = 0
    total_concrete = 0
    total_fuel = 0
    total_amount = 0

    for i, row in enumerate(records, start=1):

        fuel_avg = 0

        if row.engine_hours:
            fuel_avg = row.fuel_qty / row.engine_hours

        data.append({

            "sr_no": i,

            "date": row.date,

            "time": row.time,

            "asset": row.asset_name,

            "make": row.make,

            "model": row.model,

            "engine_start": row.engine_start,

            "engine_end": row.engine_end,

            "engine_hours": row.engine_hours,

            "pump_start": row.pump_start,

            "pump_end": row.pump_end,

            "pump_hours": row.pump_hours,

            "concrete_qty": row.concrete_qty,

            "fuel_qty": row.fuel_qty,

            "hsn_code": row.hsn_code,

            "rate": row.rate,

            "amount": row.amount,

            "fuel_avg": round(fuel_avg,2),

            "remarks": row.remarks
        })

        total_engine += row.engine_hours or 0
        total_pump += row.pump_hours or 0
        total_concrete += row.concrete_qty or 0
        total_fuel += row.fuel_qty or 0
        total_amount += row.amount or 0

    total_avg = round(total_fuel / total_engine,2) if total_engine else 0

    data.append({

        "asset":"TOTAL",

        "engine_hours":total_engine,

        "pump_hours":total_pump,

        "concrete_qty":total_concrete,

        "fuel_qty":total_fuel,

        "amount":total_amount,

        "fuel_avg":total_avg
    })

    return data
