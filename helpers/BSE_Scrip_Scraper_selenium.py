import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')


class SeleniumApp:
    def __init__(self):
        """
        Create driver obj and get webpage
        """
        self.driver = webdriver.Chrome('../assets/chromedriver.exe', chrome_options=options)
        self.driver.get("https://www.bseindia.com/markets/equity/EQReports/MarketWatch.html?index_code=16")

    def scrape(self):
        """
        Scrape and dump to json
        """
        # wait until contents load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ng-scope")))
        # locate elements
        table = self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[3]/table/tbody/tr[1]/td/table')
        tbody = table.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[3]/table/tbody/tr[1]/td/table/tbody')
        tr = tbody.find_elements_by_tag_name('tr')
        td = [row.find_elements_by_tag_name('td') for row in tr]
        # match regex
        scrip_mapping = {rs[1].text: rs[0].text for rs in td if re.match("^5[0-9]{5}", rs[0].text) or re.match("\w", rs[1].text)}
        # export to json
        self.dump(scrip_mapping)

    @staticmethod
    def dump(scrip):
        with open("../assets/scrip_mappings_sensex.json", "w") as f:
            json.dump(scrip, f)
            f.close()


sc = SeleniumApp()
sc.scrape()
