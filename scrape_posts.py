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

    dir_name = link_path.replace("_link.txt","")
    os.makedirs(dir_name,exist_ok=True)

    links = []
    with open(link_path) as f:
        while line := f.readline():
            links.append(line.replace("\n", ""))

    for link in links:

        try:
            driver.get(link)

            #Get the title and see if the page has
            title_soup = BeautifulSoup(driver.page_source, "html.parser")
            question_title = title_soup.find('title').getText()

            #if the file is already there then skip it
            if os.path.isfile(f"{dir_name}/{question_title}.json") and REDOWNLOAD_ALL == False:
                print(f"FILE {dir_name}/{question_title}.json ALREADY EXISTS")
                time.sleep(0.75)

            #Scroll to the end of the page
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                html = driver.find_element_by_tag_name('html')
                for i in range(25): html.send_keys(Keys.END)
                new_height = driver.execute_script("return document.body.scrollHeight")
                time.sleep(0.1)
                if new_height == last_height:
                    break
                last_height = new_height
           
            time.sleep(0.5)

            #Click all the expand buttons
            expand_buttons = driver.find_elements_by_class_name("q-click-wrapper")

            for expand_button in expand_buttons:
                try:
                    if "Continue Reading" in expand_button.text:
                        expand_button.click()
                except:
                    continue

            #Get all of the upvote buttons
            upvote_buttons = [button for button in driver.find_elements_by_class_name("q-click-wrapper") if "Upvote" in button.text]


            #Start the page scraping process
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            question_title = soup.find('title').getText()

            answer_blocks = soup.find_all('div', class_='q-box qu-pb--small qu-borderBottom')

            thread_data = {}
            thread_data["title"] = question_title
            thread_data["tags"] = [tag.get_text() for tag in soup.find_all("div", class_="q-box qu-mr--tiny qu-mb--tiny")]
            thread_data["response"] = []

            i = 0
            for answer in answer_blocks:

                answer_block = {}
                author = {}

                author_block = answer.find('a', class_="q-box qu-color--gray_dark qu-cursor--pointer qu-hover--textDecoration--underline")
                if author_block == None:
                    continue
                author["name"] = author_block.find("span").get_text()

                try:
                    author["href"] = author_block["href"]
                except:
                    author["href"] = None 

                answer_block["author_info"] = author
                answer_block["answer_text"] = answer.find("span", class_="q-box qu-userSelect--text").get_text()
                stats = answer.find("div", class_="q-text qu-mt--small qu-color--gray_light qu-fontSize--small qu-passColorToLinks")
                
                answer_block["date"] = answer.find("a", class_="q-box qu-cursor--pointer qu-hover--textDecoration--underline").get_text()
                
                if stats != None:

                    stats = stats.get_text().split("·")[0:2]

                    answer_block["views"] = re.sub("\D", "", stats[0]) if len(stats) >= 1  else "0"
                    answer_block["upvotes"] = stats[1] if len(stats) > 1 else "0"
                else:
                    answer_block["views"] = "0"
                    answer_block["upvotes"] = "0"

                #click on the upvote button to get the number of upvoters
                if answer_block["upvotes"] != "0" and i < len(upvote_buttons):
                    if button := upvote_buttons[i]:
                        driver.execute_script("arguments[0].click()", button)
                        i+=1

                    time.sleep(1)
                    scroll_to_bottom_of_upvoter_box(driver)
                    time.sleep(0.2)
                    upvoter_page_soup = BeautifulSoup(driver.page_source, "html.parser")
                    answer_block["upvoters"] = []
                    upvote_block = upvoter_page_soup.find("div", class_="q-flex modal_content_inner qu-flexDirection--column qu-bg--white qu-overflowY--auto qu-borderAll qu-alignSelf--center")
                    for upvoter in upvote_block.find_all("a", class_="q-box qu-color--gray_dark qu-cursor--pointer qu-hover--textDecoration--underline"):
                       answer_block["upvoters"].append({
                           "user_id": upvoter.get_text(),
                           "user_href": upvoter["href"]
                           }) 

                    if button := driver.find_element_by_id("close"):
                        button.click()
                
                thread_data["response"].append(answer_block)

                
            with open(f"{dir_name}/{question_title}.json","w") as outfile:
                json.dump(thread_data, outfile,indent=4)
            print(f"{dir_name}/{question_title}.json")

            time.sleep(0.5)
        except:
            print(f"FAILED TO DOWNLOAD {link}")
            continue


if __name__ == "__main__":

    link_files = [fp for fp in os.listdir("./")  if ".txt" in fp]
    p = multiprocessing.Pool(len(link_files))
    p.map(scrape, link_files)
