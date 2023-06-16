from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import threading
import cv2
import numpy as np
import pyautogui
import pywinctl as gw
import sys
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
from selenium.webdriver.chrome.service import Service as ChromeService
from time import sleep


load_dotenv()
username=os.getenv('userid')
password=os.getenv('password')
print(username, password)

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Setup Chrome options
# userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f'user-agent={os.getenv("userAgent")}')
chrome_options.add_argument("--disable-web-security")


service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# login to mailchimp account given username and password
def login(username, password):
    print("Logging in")
    driver.get("https://login.mailchimp.com/")

    usernameElement = driver.find_element(By.XPATH, "//input[@id='username']")
    usernameElement.clear()
    usernameElement.send_keys(username)

    passwordElement = driver.find_element(By.XPATH, "//input[@id='password']")
    passwordElement.clear()
    passwordElement.send_keys(password)

    try:
        # loginButton = driver.find_element(By.XPATH, "//button[@id='submit-btn']")
        # loginButton.click()
        loginButton = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='submit-btn']"))
        )
        driver.execute_script("arguments[0].click();", loginButton)
        WebDriverWait(driver, 2).until(EC.title_contains("Two-factor authentication | Mailchimp"))
    except:
        print("Login error")
    # driver.find_element(By.ID, "submit-btn").click()

    if driver.title  == "Two-factor authentication | Mailchimp":
        verificationButton = driver.find_element(By.XPATH, "//a[contains(text(), 'Send Verification code')]")
        verificationButton.click()

        verifyCode = input("Enter verification code:")
        textCode = driver.find_element(By.ID, "sms-code")
        textCode.send_keys(verifyCode)

        loginButton = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log in']")
        loginButton.click()

# create email
def goToClassicEmailCreation():
    print("Creating classic Email Creation")
    driver.get("https://us21.admin.mailchimp.com/#/create-campaign/explore/emailCampaign")

    compaignName = input("Enter compaign name:")
    textCompaign = driver.find_element(By.XPATH, "//input[@name='textValue']")
    textCompaign.send_keys(compaignName)

    beginButton = driver.find_element(By.XPATH, "//button[@type='submit']")
    beginButton.click()

    selectClassicBuilder = driver.find_element(By.XPATH, "//button/span[contains(text(), 'Select the Classic Builder')]")
    selectClassicBuilder.click()

    basic1Column = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@title, 'Select Sell Products')]")))
    basic1Column.click()

# from a list of compaigns select one
def openCompaign():
    print("Going to draft page")
    driver.get("https://us21.admin.mailchimp.com/campaigns/#t:campaigns-list")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    driver.switch_to.frame(iframes[0])
    compaigns = driver.find_elements(By.CSS_SELECTOR, 'li.c-campaignManager_slat')
    links =[]
    for i in compaigns:
        link = i.find_element(By.XPATH, ".//a[contains(@class, 'c-campaignManager_slat_details_link')]")
        links.append(link)

    print("List of compaigns:")
    for i, link in enumerate(links):
        print(f"{i}){link.text}")

    compaignChoice = int(input("What do you choose:"))
    driver.get(links[compaignChoice-1].get_attribute("href"))

    driver.switch_to.default_content()

# show user the pricing of mailchimp
def pricing():
    driver.get("https://mailchimp.com/")
    navLink = driver.find_element(By.XPATH, "//a[@href='/pricing/marketing/']")
    navLink.click()
    time.sleep(30)

# signup with new account using mailchimp
def signUp():
    pricing()
    WebDriverWait(driver, 10).until(EC.title_contains("Pricing Plans"))
    freePlanLink = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://mailchimp.com/signup/?plan=free_monthly_plan_v0']")))
    freePlanLink.click()

    WebDriverWait(driver, 10).until(EC.title_contains("Signup"))
    emailElement = driver.find_element(By.XPATH, "//input[@id='email']")
    emailElement.clear()
    emailElement.send_keys("newsamplemail@gmail.com")

    passwordElement = driver.find_element(By.XPATH, "//input[@id='new_password']")
    passwordElement.clear()
    passwordElement.send_keys(".yym4cAJ389bbGe")

    checkbox = driver.find_element(By.XPATH, "//input[@id='marketing_newsletter']")
    checkbox.click()

    signinButton = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[@id='create-account-enabled']"))
    )
    driver.execute_script("arguments[0].click();", signinButton)
    try:
        captchaElement = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='rc-imageselect-payload']")))
        while captchaElement:
            time.sleep(5)
    except:
        pass

    WebDriverWait(driver, 10).until(EC.title_contains("Success"))

    if driver.title  == "Success | Mailchimp":
        print("redirecting to email,")
        openMail = driver.find_element(By.XPATH, "//a[@href='https://mail.google.com/mail/u/0/']")
        openMail.click()
        time.sleep(60)

# allows the user to go to integrate mailchimp with shopify page
def integrationWithShopify():
    print("goint to integration with shopify")
    driver.get("https://us21.admin.mailchimp.com/integrations/app?name=shopify")

def script_execution():
    login(username, password)
    # goToClassicEmailCreation()
    # openCompaign()
    integrationWithShopify()
    # pricing()
    input("Enter:")

def recording():
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = 1.0
    record_seconds = 100
    out = cv2.VideoWriter("output.avi", fourcc, fps, (1280, 720))
    for i in range(int(record_seconds * fps)):
        screenshot = driver.get_screenshot_as_png()
        # Convert to OpenCV image
        image = Image.open(io.BytesIO(screenshot))
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(frame, (1280, 720))
        out.write(image_resized)
        # Pause for a while
        sleep(0.2)

        if cv2.waitKey(1) == ord("q"):
            break

        driver.save_screenshot(f"dataa/{i}.png")
    # cv2.destroyAllWindows()
    out.release()
    driver.quit()

# Create threads for script execution and recording
script_thread = threading.Thread(target=script_execution)
recording_thread = threading.Thread(target=recording)

# Start the threads
script_thread.start()
recording_thread.start()

# Wait for both threads to complete
script_thread.join()
recording_thread.join()