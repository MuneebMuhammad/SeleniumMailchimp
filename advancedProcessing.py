import os
from selenium import webdriver
from bs4 import BeautifulSoup, NavigableString
from ordered_set import OrderedSet
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
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service as ChromeService
# from ordered_set import OrderedSet
# from selenium.webdriver.chrome.options import Options
# from dotenv import load_dotenv
#
# load_dotenv()
#
# service = ChromeService(executable_path=ChromeDriverManager().install())
#
# chrome_options = Options()
# # chrome_options.add_argument("--headless")
# chrome_options.add_argument(f'user-agent={os.getenv("userAgent")}')
# # chrome_options.add_argument("--disable-web-security")

f = open("Release a new album - ConvertKit.html", "r")
source = f.read()
# print(source)
f.close()

mainElements = []
# print(type(source))
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

soup = BeautifulSoup(source, "html.parser")

title = soup.find('title')

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
    d = i.name + " : " + ((i.get("type").strip() if "type" in i.attrs else "No Type") + " : " + (i.get("name") if "name" in i.attrs else "No Name") if i.name == "input" else i.get_text().strip().replace("\n", " "))
    try:
        f.write('\n'+d)
    except:
        print(f"ordered element:", i)
        print("unicode not available")