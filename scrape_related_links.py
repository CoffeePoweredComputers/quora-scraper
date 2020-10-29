import requests
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CHROMEDRIVER_PATH = "./chromedriver"
CHROME_PATH = ""
WINDOW_SIZE = "1920,1080"

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


def scrape_links(url):

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    links_strucs = soup.find_all(name="a",class_="q-box qu-display--block qu-cursor--pointer qu-hover--textDecoration--none")
    links = ["https://www.quora.com/" + link["href"] for link in links_strucs]
    return links

for f in listdir("."):
    if ".txt" in f:
        links = []
        with open(f,"r") as infile:
            for link in tqdm(infile.readlines()):
                links.extend(scrape_links(link))
            print(links)

        with open(f, "a") as outfile:
            for link in links:
                outfile.write(link + "\n")
