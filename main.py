from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()
username=os.getenv('username')
password=os.getenv('password')

profile_directory = r'/Users/muneebmuhammad/Library/Application Support/Google/Chrome/Profile 1'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'user-data-dir={profile_directory}')
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless=True")

driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()

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
    # for index, iframe in enumerate(iframes):
    #     driver.switch_to.frame(iframe)
    #     compaign = driver.find_elements(By.CSS_SELECTOR, 'li.c-campaignManager_slat')
    #     if len(compaign) >0:
    #         print("found:", index)


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
    # freePlanLink = driver.find_element(By.XPATH, "//a[@href='https://mailchimp.com/signup/?plan=free_monthly_plan_v0']")
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

login(username, password)
# goToClassicEmailCreation()
# openCompaign()
integrationWithShopify()


input("Enter:")

