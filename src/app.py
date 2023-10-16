from flask import Flask
import visit
from global_variables import CHECK_INTERVAL_IN_SEC

app = Flask(__name__)
@app.route("/")
def index():
    return "hello world"

@app.route('/visit_nd')
def call_nd():
    visit.VisaAppointment()
    visit.run_function_wrapper(CHECK_INTERVAL_IN_SEC, visit.update_and_check_if_reschedule)

if __name__ == "__main__":
    app.run()

