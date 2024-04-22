import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import pandas as pd
import re
import numpy as np
import os
from dotenv import load_dotenv

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/94.0.4606.81 Safari/537.36')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
main = 'https://www.ebay.com/deals'
driver.get(main)
wait = WebDriverWait(driver, 2)
action = ActionChains(driver)
prods = []

def delay():
    time.sleep(random.randint(5, 10))

def load_more():
    while True:
        try:
            more = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Show more']")))
            action.move_to_element(more).click().perform()
            delay()
        except TimeoutException:
            break

def get_product_details(url):
    try:
        driver.get(url)
        prod = {'url': url}
    except Exception:
        return

    check = ('Brand', 'Type', 'Material', 'Color')
    dim =  ('Item Height', 'Item Depth', 'Item Width', 'Item Weight')
    try:
        specifics = driver.find_elements(By.CLASS_NAME, 'ux-layout-section-evo__col')
        for specific in specifics:
            key, tmp = specific.text.split('\n', 1)
            val = re.sub('[^\d\.]', '', tmp)
            if key in check or key in dim:
                prod[key] = val     
    except Exception:
        pass
    
    for key in check:
        if key not in prod:
            prod[key] = 'n/a'
    for key in dim:
        if key not in prod:
            prod[key] = -1
    
    try: 
        prod['condition']  = driver.find_element(By.CLASS_NAME, 'x-item-condition-text').text
    except Exception:
        prod['condition'] = 'n/a'

    try: 
        tmp = driver.find_element(By.CLASS_NAME, 'x-price-primary').text
        prod['price'] = float(re.sub('[^\d\.]', '', tmp))
    except Exception:
        prod['price'] = -1

    try: 
        prod['seller'] = driver.find_element(By.CLASS_NAME, 'x-sellercard-atf__info__about-seller').get_attribute('title')
    except Exception:
        prod['seller'] = 'n/a'

    try: 
        prod['numsold'] = int(driver.find_element(By.CLASS_NAME, 'd-quantity__availability').text.split(' / ')[1].split(' ')[0].replace(',', ''))
    except Exception:
        prod['numsold'] = -1
    
    try: 
        prod['rating'] = float(driver.find_element(By.CLASS_NAME, 'ux-summary__start--rating').text)
    except Exception:
        prod['rating'] = -1
    
    prods.append(prod)

def find_product_links():
    boxes = driver.find_elements(By.XPATH, ".//a[@itemprop = 'url']")
    links = [box.get_attribute('href') for box in boxes]
    for link in links:
        get_product_details(link)
        delay()

def extract_deals():
    header = driver.find_elements(By.CLASS_NAME, "navigation-desktop-with-flyout")[3]
    elmnts = header.find_elements(By.CLASS_NAME, "navigation-desktop-flyout-link")[:-1]
    urls = [elmnt.get_attribute('href') for elmnt in elmnts]

    for url in urls:
        driver.get(url)
        load_more()
        find_product_links()

    return pd.DataFrame(prods)

def transform():
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(parent_dir + '/.env')
    filename=os.getenv('FILENAME')
    path = parent_dir + '/' + filename
    df = extract_deals()
    df.columns.str.lower()
    df.rename(columns={'item weight':'item_weight','item depth':'item_depth','item height':'item_height','item width':'item_width'}, inplace=True)
    df.to_csv(path, index=False)