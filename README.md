# U.S. visa interview appointment auto-scheduler
*Task yet to be done is marked as #TODO

Introduction:
    This is an automatic scheduler for US visa interview appointment. We use a separate account to check most recent available visa appointment date in certain frequency, and store user data in a separate CSV file. Once there exist appointment date earlier than user's current appointment date, we log into user's account and do the reschedule.

Module Structure:

    data_update.py:
    """
        add new user data to the csv file by following below command:
        add_user_csv(email_str, password_str)
    """
        This function will create a new "visa_users.csv" file one level above the github repo by default, you can also specify the directory

    # web_api.py:
        # to run the whole auto-scheduler manually, please make sure you've already created the csv file using data_update.py and import both module into a new python file.
            eg = web_api.VisaAppointment()
            eg.check_recent_available_date() 
            # then you can either
                eg.reschedule_for_users()
            # or 
                eg.reschedule_for_a_user(user_name, password, available_date)
                if you know those information of a user.

    # global_variable.py:
        # you can change city list, appointment check interval variables in this file

Initiation:
    after git pull, run pip install -r requirements.txt to install required package


How to run the script:
    in the web_script directory, run "python app.py" to start the script. It'll keep running after that.
    If you want to manually test with web_api, please follow commans under web_api.py section above.



