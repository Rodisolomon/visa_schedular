from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import re
import time, sched
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict
import global_variables as GBV




def nextdoor():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #need to install selenium and webdriver-manager
    driver.get("https://www.nextdoor.com/")  

    #login
    account = driver.find_element(By.XPATH, '//input[@type="email"]')
    account.send_keys("thzhelen@gmail.com")
    password = driver.find_element(By.XPATH, '//input[@type="password"]')
    password.send_keys("thz1123helenTG!")
    continue_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    continue_button.submit()
    time.sleep(3)

    #publish post
    driver.get("https://nextdoor.com/news_feed/#navigation")
    post = driver.find_element(By.XPATH, '//button[contains(.,"Post")]')
    post.click()
    input_box = driver.find_element(By.XPATH, '//textarea[@class="postbox-field-textarea-with-tags-input postbox-field-textarea _icIOf5X"]')
    input_box.send_keys("try to publish this post")
    time.sleep(1) #there's a change in postion if button, have to sleep
    post_publish = driver.find_element(By.XPATH, '//button[contains(@aria-label, "composer submit button")]')
    post_publish.click()
    time.sleep(3)

    driver.quit()  





def run_scheduled_function(scheduler:Callable, interval_in_sec:int, callable:Callable) -> None:
    scheduler.enter(interval_in_sec, 1, run_scheduled_function, (scheduler, interval_in_sec, callable))
    callable()

def run_function_wrapper(interval_in_sec:int, callable:Callable) -> None:
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(interval_in_sec, 1, run_scheduled_function, (scheduler, interval_in_sec, callable))
    scheduler.run()

class VisaAppointment():
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #need to install selenium and webdriver-manager
        self.driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_in")  
        self.logged_in: bool = False
        self.last_check_time: Optional[datetime] = None
        self.recent_available_dates: Dict[str, Optional[datetime]] = {city: None for city in GBV.CANADA_CITY_LIST}


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
    def datetime_to_str(self, date: datetime) -> str:
        """
        return in the structure of date, Month, Year (eg. 8 February, 2024)
        """
        format_string = "%d %B, %Y"
        formatted_datetime = date.strftime(format_string)
        return formatted_datetime
    
    def get_recent_appointment_date(self, email_str: str, password_str: str) -> Optional[str]:
        """
        get recent appointment date of the user the structure of date, Month, Year
        used when 
        1. new user been added into local csv file
        2. before reschedule, assert that current available date is earlier than user's appointment's
        """
        try:
            if self.logged_in:
                self.logout()
            self.login(email_str, password_str)
            apt_info = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//p[@class='consular-appt']"))
            )
            raw_str = apt_info.text
            date_pattern = r"\d{1,2}\s\w+,\s\d{4}"
            matched = re.search(date_pattern, raw_str)
            self.logout()
            if matched:
                return matched.group(0)
            else:
                return None           
        except:
            return None

    
    def check_recent_available_date(self) -> None:
        """
        update recent available dates dict every 10 mins, stored value will be None if there's no available appointment 
        """
        current_datetime = datetime.now()
        if self.last_check_time and self.last_check_time + timedelta(minutes=10) > current_datetime:
            return
        self.last_check_time = current_datetime
        self.login(GBV.TIME_CHECK_EMAIL, GBV.TIME_CHECK_PASSWORD)
        if not self.logged_in:
            return
        
        time.sleep(1)
        continue_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Continue")
        continue_button.click()

        base_url, _ = self.driver.current_url.rsplit('/', 1)
        self.driver.get(base_url + "/payment")

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
                        date_obj = datetime.strptime(date_text, '%d %B, %Y')
                        self.recent_available_dates[city_name] = date_obj
                    except ValueError:
                        pass
        self.logout()


    def login(self, email_str: str, password_str: str) -> None:
        """
        the function log into user account given password and user email into AIS system
        """
        #account
        account = self.driver.find_element(By.XPATH, '//input[@type="email"]')
        account.send_keys(email_str)
        #password
        password = self.driver.find_element(By.XPATH, '//input[@type="password"]')
        password.send_keys(password_str)
        #checkbox
        checkbox = self.driver.find_element(By.ID, "policy_confirmed")
        actions = ActionChains(self.driver)
        actions.move_to_element(checkbox).click().perform()
        #submit
        continue_button = self.driver.find_element(By.XPATH, '//input[@type="submit" and @name="commit"]')
        continue_button.submit()
        self.logged_in = True

    def logout(self) -> None:
        self.driver.get("https://ais.usvisa-info.com/en-ca/niv/users/sign_out")
        self.logged_in = False

    def navigate_to_scheduler(self) -> None:
        """
        navigate from front page to reschedule page
        """
        if not self.logged_in:
            return
        continue_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Continue")
        continue_button.click()

        base_url, _ = self.driver.current_url.rsplit('/', 1)
        self.driver.get(base_url + "/appointment")
        time.sleep(5)
        self.driver.quit()
        
    def reschedule(self) -> None:
        if not self.logged_in or "appointment" not in self.driver.current_url:
            return
        
        
