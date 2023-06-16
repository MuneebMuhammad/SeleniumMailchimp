import os

from selenium import webdriver
from bs4 import BeautifulSoup, NavigableString
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# import time
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import os
# from dotenv import load_dotenv
# import threading
# import cv2
# import numpy as np
# import pyautogui
# import pywinctl as gw
# import sys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from ordered_set import OrderedSet
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

service = ChromeService(executable_path=ChromeDriverManager().install())

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument(f'user-agent={os.getenv("userAgent")}')
# chrome_options.add_argument("--disable-web-security")


driver = webdriver.Chrome(service=service)


url = "https://qalam.nust.edu.pk/"
driver.get(url)
input("Enter")
source = driver.page_source
soup = BeautifulSoup(source, "html.parser")

title = soup.find('title')

mainElements = []

# recursive function to get the main elements
def find_text_tags(tag):
    if isinstance(tag, NavigableString):
        if tag.strip():
            if tag.parent.name not in ['script', 'style']:
                mainElements.append(tag.parent)
    else:
        if tag.name == 'input':
            if tag.get("type") != "hidden":
                mainElements.append(tag)
        for child in tag.children:
            find_text_tags(child)

# Get the body tag
body_tag = soup.body

# Call the function on the body tag to get main elements
find_text_tags(body_tag)

# remove redundant elements
orderdElement = OrderedSet(mainElements)

# write data to file
f = open(f"DOM.txt", "w")
f.write("Title : " + title.text)
for i in orderdElement:
    # write the element name and, its type and placeholder if input field or text if not input filed
    d = i.name + " : " + (i.get("type").strip() + " : " + (i.get("name") if "name" in i.attrs else "No Name") if i.name == "input" else i.get_text().strip().replace("\n", " "))
    try:
        f.write('\n'+d)
    except:
        print("unicode not available")

# this will convert the beautiful soup tag in orderedElement[index] to interactable selenium object
# def getSeleniumElement(index):
#     attributes = orderdElement[index].attrs
#     seleniumElement = None
#     try:
#         if 'id' in attributes:
#             seleniumElement = driver.find_element(By.ID, attributes["id"])
#         elif 'class' in attributes:
#             classes = ' '.join(attributes['class'])
#             seleniumElement = driver.find_element(By.XPATH, f"//*[@class='{classes}']")
#     except:
#         print("Error: Can't get the selenium element")
#     return seleniumElement

# after element selected perform relevant action for each element
def actionHelperFunction(seleniumElement, bsElement):
    tag_name = seleniumElement.tag_name
    try:
        if tag_name == 'a' or tag_name == 'button':
            seleniumElement.click()
        elif tag_name == 'input' or tag_name == 'password':
            if (bsElement.attrs)["type"] == 'submit' or (bsElement.attrs)["type"] == 'button':
                seleniumElement.click()
            else:
                print("waiting for user to fill fields")
        else:
            print("text:", seleniumElement.text)
    except:
        print("Interaction Error. User take step")

# after element selected perform relevant action for each element
def performAction(index):
    bsElement = orderdElement[index]
    tag_name = bsElement.name
    attributes = bsElement.attrs

    if "id" in bsElement.attrs:
        seleniumElement = driver.find_element(By.ID, attributes["id"])
        actionHelperFunction(seleniumElement, bsElement)
    else:
        try:
            if tag_name == 'a':
                seleniumElement = driver.find_element(By.XPATH, f"//a[@href='{attributes['href']}']")
                seleniumElement.click()
            elif tag_name == 'button':
                seleniumElement = driver.find_element(By.XPATH, f"//button[text()='{bsElement.text}']")
                seleniumElement.click()
            elif tag_name == 'input' or tag_name == 'password':
                css_selector = tag_name
                for attr, value in (bsElement.attrs).items():
                    if attr == "class": continue
                    css_selector += '[{}="{}"]'.format(attr, value)
                seleniumElement = driver.find_element(By.CSS_SELECTOR, css_selector)

                if attributes["type"] == 'submit' or attributes["type"] == 'button':
                    seleniumElement.click()
                else:
                    print("waiting for user to fill fields")
            else:
                print("text:", bsElement.text)

        except:
            print("Error: can't find element")



d = performAction(1)

# de = getSeleniumElement(0)
#
# performElementAction(de)
driver.quit()