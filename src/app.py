from flask import Flask
import visit

app = Flask(__name__)
@app.route("/")
def index():
    return "hello world"

@app.route('/visit_nd')
def call_nd():
    visit.run_function_wrapper(60, visit.nextdoor)

if __name__ == "__main__":
    app.run()

