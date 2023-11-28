import web_api
from global_variables import CHECK_INTERVAL_IN_SEC

reschedular = web_api.VisaAppointment()
reschedular.check_recent_available_date()

# reschedular.reschedule_for_users()