from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys  
import time, sched
from typing import Callable


def google():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #need to install selenium and webdriver-manager
    driver.get("https://www.google.com/")  
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("helen tan")
    time.sleep(3)
    search_box.submit()
    time.sleep(3)
    driver.quit()

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

 