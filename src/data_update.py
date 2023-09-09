import csv
import web_api
import global_variables as GBV
data = ["jszjosh@gmail.com", ".-Bj&JZ2WZC9N#s"]

def add_user_csv(email, password) -> None:
    """
    add new user to user_data.csv file, with row email, password, current_appointment_date
    """
    new_web_client = web_api.VisaAppointment()
    recent_date_str = new_web_client.get_recent_appointment_date(email, password)
    try:
        with open(GBV.CSV_FILE_PATH, 'r', newline='') as file:
            file_exists = True
    except FileNotFoundError:
        file_exists = False
    
    with open(GBV.CSV_FILE_PATH, 'a', newline='') as file:
        if recent_date_str == None:
            return
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["email", "password", "Existing Appointment Date"])
        writer.writerow([email, password, recent_date_str])

add_user_csv(data[0], data[1])
    