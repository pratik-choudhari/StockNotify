import json
import time
import selenium
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox()
driver.get("https://www1.nseindia.com/live_market/dynaContent/live_watch/equities_stock_watch.htm")


def nifty50():
    tbody = driver.find_element_by_xpath('//*[@id="dataTable"]/tbody')
    rows = tbody.find_elements_by_tag_name("tr")
    nifty_stocks = {"stocks": []}
    for row in rows:
        try:
            nifty_stocks["stocks"].append(row.find_element_by_tag_name("td").find_element_by_tag_name("a").text)
        except selenium.common.exceptions.NoSuchElementException as e:
            print("Element not found")
    driver.close()
    return nifty_stocks


def niftynext50(nifty50_components):
    csv = pd.read_csv("https://archives.nseindia.com/content/indices/ind_niftynext50list.csv")
    return nifty50_components['stocks'].extend(csv.iloc[:, 2].to_list())


nifty_components = nifty50()
all_nifty = niftynext50(nifty_components)
json.dump(nifty_components, open("../assets/nifty_components.json", "w"))
