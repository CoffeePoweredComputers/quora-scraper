from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import requests
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CHROMEDRIVER_PATH = "./chromedriver"
CHROME_PATH = ""
WINDOW_SIZE = "1920,1080"


links = []
with open("./Books_link.txt") as f:
    while line := f.readline():
        links.append(line.replace("\n", ""))



options = Options()
#options.add_argument("--headless")  
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.binary_location = CHROME_PATH
prefs = {'profile.managed_default_content_settings.images':2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=options
)


for link in links:
    link = "https://www.quora.com/What-are-the-most-viewed-questions-on-Quora"
    driver.get(link)

    #Scroll to the end of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        new_height = driver.execute_script("return document.body.scrollHeight")
        html = driver.find_element_by_tag_name('html')
        for i in range(10): html.send_keys(Keys.END)
        time.sleep(2)
        if new_height == last_height:
            break
        last_height = new_height
   
    time.sleep(3)
    #Click all the buttons
    expand_buttons = driver.find_elements_by_class_name("q-click-wrapper")

    for expand_button in tqdm(expand_buttons):
        if expand_button.text == "Continue Reading":
            try:
                expand_button.click()
            except:
                continue



    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")



    question = soup.find('title').getText()
    answer_blocks = soup.find_all('div', class_='q-box qu-pb--small qu-borderBottom')

    for answer in answer_blocks:

        try:
            author_block = answer.find('a', class_="q-box qu-color--gray_dark qu-cursor--pointer qu-hover--textDecoration--underline")
            author = {
                    "name" : author_block.find("span").getText(),
                    "href" : author_block["href"]
                    }

            answer_components = answer.find("span", class_="q-box qu-userSelect--text")
            print(answer_components)
        except:
            continue


    break



    time.sleep(3)
