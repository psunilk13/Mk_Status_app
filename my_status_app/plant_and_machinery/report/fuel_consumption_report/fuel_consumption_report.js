// Copyright (c) 2026, shiva and contributors
// For license information, please see license.txt


frappe.query_reports["Fuel Consumption Report"] = {

    filters: [

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 0
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 0
        },
        {
            fieldname: "asset",
            label: "Asset",
            fieldtype: "Link",
            options: "Asset"
        },
        {
            fieldname: "asset_category",
            label: "Asset Category",
            fieldtype: "Link",
            options: "Asset Category"
        },

        {
            fieldname: "report_type",
            label: "Report Type",
            fieldtype: "Select",
            options: "\nEngine Hours\nFuel Qty",
            default: "Fuel Qty",
            reqd: 1
        }
    ]
};
