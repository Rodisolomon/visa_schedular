from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test(): 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #need to install selenium and webdriver-manager
    driver.get("https://www.selenium.dev/selenium/web/inputs.html")
    title = driver.title
    print(title)
    assert title == "inputs"
    # Click on the element 
    driver.find_element(By.NAME, "color_input")
    driver.quit()

test()
