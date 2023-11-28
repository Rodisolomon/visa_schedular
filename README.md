[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Selenium](https://img.shields.io/badge/Selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/documentation/overview/)



# U.S. visa interview appointment auto-scheduler
*Task yet to be done is marked as #TODO

## Introduction:

This is an automatic scheduler for US visa interview appointment. We use a separate account to check most recent available visa appointment date in certain frequency, and store user data in a separate CSV file. Once there exist appointment date earlier than user's current appointment date, we log into user's account and do the reschedule. 
We use Selenium for the interaction with webpage.

## Module Structure:
```Python3
# data_update.py:
    # add new user data to the csv file by following below command:
    add_user_csv(email_str, password_str)
    # This function will create a new "visa_users.csv" file one level above the github repo by default, you can also specify the directory

# web_api.py:
    # to run the whole auto-scheduler manually, please make sure you've already created the csv file using data_update.py and import both module into a new python file.
    eg = web_api.VisaAppointment()
    eg.check_recent_available_date()

    # then you can either
    eg.reschedule_for_users()
    # or test it for a single user if you know those information of a user.
    eg.reschedule_for_a_user(user_name, password, available_date)
            

# global_variable.py:
    # you can change city list, appointment check interval variables in this file
```

## Initiation:

after git pull, run 
```
pip install -r requirements.txt
```
to install required package


## How to run the script:

in the web_script directory, run 
```
python app.py
```
to start the script. It'll keep running after that. Open the web address provided by flask with "/visit" to initiate the checking program
to kill the process/restart run 
```
lsof -i :5000
kill -9 <PID>
```
If you want to manually test with web_api, please follow commands under web_api.py section above.



