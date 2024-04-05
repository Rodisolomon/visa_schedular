from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

import csv
import re
import time, sched
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict
import global_variables as GBV
import os


def run_scheduled_function(scheduler:Callable, interval_in_sec:int, callable:Callable) -> None:
    scheduler.enter(interval_in_sec, 1, run_scheduled_function, (scheduler, interval_in_sec, callable))
    callable()

def run_function_wrapper(interval_in_sec:int, callable:Callable) -> None:
    """
    The function used directly by app.py
    """
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(interval_in_sec, 1, run_scheduled_function, (scheduler, interval_in_sec, callable))
    scheduler.run()



class VisaAppointment():
    def __init__(self, file_path = None):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox") # Recommended for running in CI/CD environments
        self.chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options) #need to install selenium and webdriver-manager
        self.driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in") 
        if not file_path:
            current_directory = os.getcwd()
            parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
            grandparent_directory = os.path.abspath(os.path.join(parent_directory, os.pardir))
            file_path = grandparent_directory + "/visa_users.csv"
        else:
            file_path += "/visa_users.csv"
        self.file_path = file_path
        self.logged_in: bool = False
        self.last_check_time: Optional[datetime] = None
        self.recent_available_dates: Dict[str, Optional[datetime]] = {city: None for city in GBV.CANADA_CITY_LIST}
        self.recent_available_city: Optional[str] = None #the city with most recent appointment date


    @classmethod
    def restart(self) -> None:
        "restart when session fail"
        try:
            self.driver.quit()
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #need to install selenium and webdriver-manager
            self.driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in")  
        except:
            return

    @classmethod
    def datetime_to_str(self, date: datetime, no_date:bool = False) -> str:
        """
        return in the structure of date, Month, Year (eg. 8 February, 2024)
        """
        if no_date:
            date_format = "%B %Y"
        else:
            date_format = '%d %B, %Y'
        formatted_datetime = date.strftime(date_format)
        return formatted_datetime
    
    @classmethod
    def str_to_datetime(self, date_str: str, no_date:bool = False) -> datetime:
        if no_date:
            date_format = "%B %Y"
        else:
            date_format = '%d %B, %Y'
        return datetime.strptime(date_str, date_format)

    
    def get_user_recent_appointment_date(self, email_str: str, password_str: str, log_out = True) -> Optional[str]:
        """
        get recent appointment date of the user the structure of date, Month, Year
        used when 
        1. new user been added into local csv file
        2. before reschedule, assert that current available date is earlier than user's appointment's
        """
        try:
            if not self.logged_in:
                self.login(email_str, password_str)
            apt_info = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//p[@class='consular-appt']"))
            )
            raw_str = apt_info.text
            date_pattern = r"\d{1,2}\s\w+,\s\d{4}"
            matched = re.search(date_pattern, raw_str)
            if log_out:
                self.logout()
            if matched:
                return matched.group(0)
            else:
                return None           
        except:
            return None

    
    def check_recent_available_date(self) -> None:
        """
        update recent available dates dict every certain minutes, stored value will be None if there's no available appointment 
        """
        current_datetime = datetime.now()
        # if just checked, return the stored value
        if self.last_check_time and self.last_check_time + timedelta(minutes=GBV.CHECK_INTERVAL_IN_SEC/60) > current_datetime:
            return
        #recheck and update instead
        self.last_check_time = current_datetime
        self.login(GBV.TIME_CHECK_EMAIL, GBV.TIME_CHECK_PASSWORD)
        if not self.logged_in:
            return
        
        time.sleep(5)
        continue_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Continue")
        continue_button.click()

        base_url, _ = self.driver.current_url.rsplit('/', 1)
        self.driver.get(base_url + "/payment")
        valid_city = False
        # Find all <tr> elements within the table
        table_rows = self.driver.find_elements(By.XPATH, "//table[@class='for-layout']//tr")
        # Iterate through the <tr> elements
        for row in table_rows:
            # Extract the <td> elements within the current row
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 2:
                city_name = cells[0].text.strip()  # Extract the city name
                date_text = cells[1].text.strip()   # Extract the date text
                # Check if the date text is valid
                if ',' in date_text:
                    try:
                        date_obj = self.str_to_datetime(date_text)
                        self.recent_available_dates[city_name] = date_obj
                        #compare, get the earliest one
                        if self.recent_available_city == None or self.recent_available_dates[self.recent_available_city] > date_obj:
                            self.recent_available_city = city_name
                        valid_city = True
                    except ValueError:
                        if self.recent_available_dates[city_name] != None:
                            self.recent_available_dates[city_name] = None
                        pass
        if not valid_city:
            self.recent_available_city = None
        # print(f"after the check, recent available city is {self.recent_available_city} with date {self.recent_available_dates[self.recent_available_city]}")
        self.logout()


    def login(self, email_str: str, password_str: str) -> None:
        """
        the function log into user account given password and user email into AIS system
        """
        #make sure on the right page
        try:
            self.driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in") 
            #account
            account = self.driver.find_element(By.XPATH, '//input[@type="email"]')
            account.send_keys(email_str)
            #password
            password = self.driver.find_element(By.XPATH, '//input[@type="password"]')
            password.send_keys(password_str)
            #checkbox
            checkbox = self.driver.find_element(By.ID, "policy_confirmed")
            actions = ActionChains(self.driver)
            actions.click(checkbox).perform()
            #submit
            continue_button = self.driver.find_element(By.XPATH, '//input[@type="submit" and @name="commit"]')
            continue_button.submit()
            self.logged_in = True
        except:
            print("log in not successful, please restart the process")

    def logout(self) -> None:
        self.driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_out")
        self.logged_in = False

    def navigate_to_scheduler(self) -> None:
        """
        navigate from front page to reschedule page
        """
        print("start navigate")
        if not self.logged_in:
            return
        print("keeo going")
        continue_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Continue")
        continue_button.click()
        base_url, _ = self.driver.current_url.rsplit('/', 1)
        self.driver.get(base_url + "/appointment")
        
    def reschedule_for_a_user(self, email_str: str, password_str: str, csv_cur_apt_date_str: str) -> None:
        """
        reschedule a more recent appointment for user, supposedly only been called when this user is viable but there also exist a check for safety purpose
        """
        self.login(email_str, password_str)
        if not self.logged_in:
            return
        #check if available date is same as the one in csv file
        web_cur_apt_date = self.str_to_datetime(self.get_user_recent_appointment_date(email_str, password_str, log_out=False))
        csv_cur_apt_date = self.str_to_datetime(csv_cur_apt_date_str)
        if web_cur_apt_date != csv_cur_apt_date:
            self.logout()
            return
        if not self.recent_available_city or not self.recent_available_dates[self.recent_available_city]:
            self.logout()
            return
        
        recent_available_date = self.recent_available_dates[self.recent_available_city]
        if recent_available_date < web_cur_apt_date: #double check
            #reschedule
            self.navigate_to_scheduler()

            #select city
            dropdown_element = self.driver.find_element(By.ID, "appointments_consulate_appointment_facility_id")
            dropdown = Select(dropdown_element)
            dropdown.select_by_visible_text(self.recent_available_city)

            #select right year+month+date
            time.sleep(1)
            apt_button = self.driver.find_element(By.ID, "appointments_consulate_appointment_date")
            self.driver.execute_script("arguments[0].click();", apt_button)
            time.sleep(1)
            day, month, year = recent_available_date.strftime("%d"), recent_available_date.strftime("%B"), recent_available_date.strftime("%Y")
            target_month_year = self.str_to_datetime(month + " " + year, no_date=True)
            time.sleep(1)
            group2 = self.driver.find_element(By.XPATH, "//div[@class='ui-datepicker-group ui-datepicker-group-last']")
            next_button_path = "//a[@class='ui-datepicker-next ui-corner-all']"
            next_button_selected_path = "//a[@class='ui-datepicker-next ui-corner-all ui-state-hover ui-datepicker-next-hover']"
            next_button = group2.find_element(By.XPATH, next_button_path)

            selected_year = group2.find_element(By.XPATH, "//span[@class='ui-datepicker-year']").get_attribute("innerHTML")
            selected_month = group2.find_element(By.XPATH, "//span[@class='ui-datepicker-month']").get_attribute("innerHTML")
            selected_month_year = self.str_to_datetime(selected_month + " " + selected_year, no_date=True)
            while selected_month_year < target_month_year:
                next_button.click()
                time.sleep(1) 
                group2 = self.driver.find_element(By.XPATH, "//div[@class='ui-datepicker-group ui-datepicker-group-last']")
                next_button = group2.find_element(By.XPATH, next_button_selected_path)
                selected_year = group2.find_element(By.XPATH, "//span[@class='ui-datepicker-year']").get_attribute("innerHTML")
                selected_month = group2.find_element(By.XPATH, "//span[@class='ui-datepicker-month']").get_attribute("innerHTML")
                selected_month_year = self.str_to_datetime(selected_month + " " + selected_year, no_date=True)
            
            #find date
            all = group2.find_elements(By.XPATH, "//td[@data-month='{}' and @data-year='{}']".format(target_month_year.month, year))
            for parent_element in all:
                for date_element in parent_element.find_elements(By.TAG_NAME, "a"):
                    date_text = date_element.get_attribute("innerHTML")
                    if date_text == day:
                        date_element.click()
                        break
            time.sleep(1)
            #select time of appointment
            dropdown_element = self.driver.find_element(By.ID, "appointments_consulate_appointment_time")
            dropdown = Select(dropdown_element)
            dropdown.select_by_index(1)
        self.logout()



    def send_success_email(self, email_str: str) -> None:
        """
        after succesfully scheduling, send out an email to the user
        """
        pass

    
    def reschedule_for_users(self) -> None:
        """
        wrapper function, check through all users for viability of reschedule, and call reschedule_for_a_user to update
        check_recent_available_date wil always been called before this function 
        """
        # TODO: shuffle logic to ensure fairness
        # Create an empty list to store the data
        user_data = []
        # Open the CSV file for reading
        with open(self.file_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)
            for row in csv_reader:
                user_data.append(row)
        #update most recent dates
        self.check_recent_available_date()
        for data in user_data:
            email, password, user_apt_date_str = data[0], data[1], data[2]
            user_apt_date = self.str_to_datetime(user_apt_date_str)
            recent_available_date = self.recent_available_dates[self.recent_available_city]
            if recent_available_date and recent_available_date < user_apt_date:
                #update when there're earlier available dates
                self.reschedule_for_a_user(email, password, user_apt_date_str)

    def update_and_check_if_reschedule(self) -> None:
        """
        function been called by wrapper
        """
        self.check_recent_available_date()
        self.reschedule_for_users()
        
        
