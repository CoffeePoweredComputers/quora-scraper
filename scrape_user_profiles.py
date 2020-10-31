from bs4 import BeautifulSoup
from html.parser import HTMLParser
from tqdm import tqdm
import os
import json
import multiprocessing
import re
import requests
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_PATH = "./chromedriver"
CHROME_PATH = ""
WINDOW_SIZE = "1920,1080"

REDOWNLOAD_ALL = False


def scroll_to_bottom_of_upvoter_box(driver):

    last_height, curr_height = 0, driver.execute_script("return document.getElementsByClassName(\"q-box qu-overflowY--auto\")[0].scrollHeight")

    while last_height != curr_height:
        driver.execute_script("document.getElementsByClassName(\"q-box qu-overflowY--auto\")[0].scrollTo(0,document.getElementsByClassName(\"q-box qu-overflowY--auto\")[0].scrollHeight)")
        time.sleep(0.5)
        last_height = curr_height
        curr_height = driver.execute_script("return document.getElementsByClassName(\"q-box qu-overflowY--auto\")[0].scrollHeight")
 



def scrape(link_path):

    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.add_argument("user-agent=This is a webscraper for a university research project. Contact: davidsmith@hamiltonfour.tech")
    options.binary_location = CHROME_PATH
    prefs = {'profile.managed_default_content_settings.images':2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH,
        options=options
    )

    links = []
    with open(link_path) as f:
        while line := f.readline():
            links.append(line.replace("\n", ""))


    users_data = []

    for link in links:

        driver.get(link)
        soup = BeautifulSoup(driver.page_source, "html.parser")


        activity_fields = soup.find_all("div", class_="q-click-wrapper qu-display--inline-block qu-tapHighlight--white qu-textAlign--left qu-cursor--pointer")[:6]

        user_data = {
                "link" : link,
                "answers" : activity_fields[0].get_text(),#soup.find(""),
                "questjions" : activity_fields[1].get_text(),
                "shares" : activity_fields[2].get_text(),
                "posts" : activity_fields[3].get_text(),
                "followers" :  activity_fields[4].get_text(),
                "following" : activity_fields[5].get_text() 
                }

        users_data.append(user_data)

    return users_data


if __name__ == "__main__":
    link_files = [fp for fp in os.listdir("./")  if ".txt" in fp]
    p = multiprocessing.Pool(len(link_files))
    p.map(scrape, link_files)
