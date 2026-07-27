from my_status_app.api import get_daily_operational_report

def execute(filters=None):
    return get_daily_operational_report(filters)
