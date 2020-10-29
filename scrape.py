from bs4 import BeautifulSoup
from tqdm import tqdm
import multiprocessing
import pandas as pd
import requests
import time
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CHROMEDRIVER_PATH = "./chromedriver"
CHROME_PATH = ""
WINDOW_SIZE = "1920,1080"

TIMES = 15000


def scrape_urls(category: str):
    """Takes a category and scrapes all the links associated with it"""

    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.binary_location = CHROME_PATH
    options.add_argument("user-agent=This is a webscraper for a university research project. Contact: davidsmith@hamiltonfour.tech")
    prefs = {'profile.managed_default_content_settings.images':2}
    options.add_experimental_option("prefs", prefs)

    url = f"https://www.quora.com/topic/{category}/all_questions"


    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH,
        options=options
    )

    driver.get(url)

    counter = 1
    for _ in tqdm(range(0, TIMES)):
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)

        time.sleep(3)

    post_elems = driver.find_elements_by_xpath("//a[@class='question_link']")
    with open(f"{category}_link.txt", "w") as f:
        for post in post_elems:
            f.write(post.get_attribute("href") + "\n")

    driver.close()



if __name__ == "__main__":

    topics = [
            "Philosophy",
            "Mathematics",
            "Writing",
            "History",
            "Education",
            "Books",
            "Music",
            "Science",
            "Technology"
            ]

    p = multiprocessing.Pool(len(topics))
    p.map(scrape_urls, topics)

