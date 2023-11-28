from flask import Flask
import web_api
from global_variables import CHECK_INTERVAL_IN_SEC

app = Flask(__name__)
@app.route("/")
def index():
    return "hello world"

@app.route('/visit')
def call_nd():
    reschedular = web_api.VisaAppointment()
    web_api.run_function_wrapper(CHECK_INTERVAL_IN_SEC, reschedular.update_and_check_if_reschedule())

if __name__ == "__main__":
    app.run()

