frappe.query_reports["Daily Operational Report V2"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
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
        }
    ]
};
