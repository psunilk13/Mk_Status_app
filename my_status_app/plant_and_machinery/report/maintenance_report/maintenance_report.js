// Copyright (c) 2026, shiva and contributors
// For license information, please see license.txt

frappe.query_reports["Maintenance Report"] = {
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
        },
        {
            fieldname: "maintenance_category",
            label: "Maintenance Category",
            fieldtype: "Select",
            options: "\nPeriodical\nPredictive\nBreakdown",

            on_change: function () {

                let category = frappe.query_report.get_filter_value(
                    "maintenance_category"
                );

                let options = "";

                switch (category) {

                    case "Periodical":
                        options = "\nService\nLubricants";
                        break;

                    case "Predictive":
                        options = "\nSpares";
                        break;

                    case "Breakdown":
                        options = "\nBreakdown";
                        break;

                    default:
                        options = "\nService\nSpares\nLubricants\nBreakdown";
                }

                let maintenance_type =
                    frappe.query_report.get_filter(
                        "maintenance_type"
                    );

                maintenance_type.df.options = options;
                maintenance_type.set_input("");
                maintenance_type.refresh();

                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "maintenance_type",
            label: "Maintenance Type",
            fieldtype: "Select",
            options: "\nService\nSpares\nLubricants\nBreakdown"
        },
        {
            fieldname: "item_code",
            label: "Item Code",
            fieldtype: "Link",
            options: "Item"
        }
    ]
};
