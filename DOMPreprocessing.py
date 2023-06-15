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

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


url = "https://qalam.nust.edu.pk/"
driver.get(url)
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
f = open(f"data.txt", "w")
f.write("Title : " + title.text + "\n")
for i in orderdElement:
    d = i.name + " : " + (i.get("type").strip() if i.name == "input" else i.get_text().strip().replace("\n", " "))
    f.write(d+'\n')


def getSeleniumElement(index):
    attributes = orderdElement[index].attrs
    seleniumElement = None
    if 'id' in attributes:
        seleniumElement = driver.find_element(By.ID, attributes["id"])
    elif 'class' in attributes:
        classes = ' '.join(attributes['class'])
        seleniumElement = driver.find_element(By.XPATH, f"//*[@class='{classes}']")
    return seleniumElement

def performElementAction(seleniumElement):
    print(seleniumElement)
    tag_name = seleniumElement.tag_name
    try:
        if tag_name == 'a' or tag_name == 'button':
            seleniumElement.click()
        elif tag_name == 'input' or tag_name == 'password':
            if seleniumElement.type == 'submit' or seleniumElement.type == 'button':
                seleniumElement.click()
            else:
                print("waiting for user to fill fields")
        else:
            print("text:", seleniumElement.text)
    except:
        print("Interaction Error. User take step")


de = getSeleniumElement(6)

performElementAction(de)
input("enter")
driver.quit()