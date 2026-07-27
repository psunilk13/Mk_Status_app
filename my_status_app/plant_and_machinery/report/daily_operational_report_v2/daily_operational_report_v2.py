from my_status_app.api import get_columns, get_daily_operational_report

def execute(filters=None):
    columns = get_columns()
    data = get_daily_operational_report(filters)
    return columns, data
