// Copyright (c) 2026, shiva and contributors
// For license information, please see license.txt

frappe.query_reports["Maintenance Report"] = {

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
            fieldname: "item_code",
            label: "Item Code",
            fieldtype: "Link",
            options: "Item"
        }
    ]
};
