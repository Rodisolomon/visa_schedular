import csv
import web_api
import os
data = ["jszjosh@gmail.com", ".-Bj&JZ2WZC9N#s"]

def add_user_csv(email, password, file_path = None) -> None:
    """
    add new user to user_data.csv file, with row email, password, current_appointment_date
    """
    if not file_path:
        current_directory = os.getcwd()
        # Get the parent directory
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        grandparent_directory = os.path.abspath(os.path.join(parent_directory, os.pardir))
        file_path = grandparent_directory + "/visa_users.csv"
    else:
        file_path += "/visa_users.csv"
    new_web_client = web_api.VisaAppointment()
    new_web_client.login(email, password)
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

def delete_user_csv(email, password, file_path) -> None:
    pass
    # TODO: delete user from database


    