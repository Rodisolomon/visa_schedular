from selenium import webdriver
from selenium.webdriver.common.by import By
def test(): 
    driver = webdriver.Chrome()
    driver.get("https://www.selenium.dev/selenium/web/inputs.html")
    title = driver.title
    assert title == "Web form"
    # Click on the element 
    driver.find_element(By.NAME, "color_input")
    driver.quit()

test()
