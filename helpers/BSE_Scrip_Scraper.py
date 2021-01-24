import requests
import bs4
from pprint import pprint


class Scrips:
    def __init__(self):
        self.generic_request_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "en-US,en;q=0.8",
        }
        self.aspx_fields1 = {
            "__VIEWSTATE": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATEENCRYPTED": "",
            "__EVENTTARGET": ""
        }
        self.aspx_fields2 = {
            "__VIEWSTATEGENERATOR": "",
            "__EVENTVALIDATION": ""
        }
        self.inputs = {
            "ctl00$ContentPlaceHolder1$hdnCode": "",
            "ctl00$ContentPlaceHolder1$ddSegment": "Equity",
            "ctl00$ContentPlaceHolder1$ddlStatus": "Active",
            "ctl00$ContentPlaceHolder1$getTExtData": "",
            "ctl00$ContentPlaceHolder1$ddlGroup": "Select",
            "ctl00$ContentPlaceHolder1$ddlIndustry": "Select",
            "ctl00$ContentPlaceHolder1$btnSubmit": "Submit"
        }
        self.payload = ''
        self.session = requests.Session()

    def get_payload(self):
        self.payload = "__VIEWSTATE" + '=' + self.aspx_fields1['__VIEWSTATE']
        for key in self.inputs:
            self.payload += "&" + key.replace('$', "%24") + '=' + self.inputs[key]

    def get_viewstate(self, page, params=None):
        if params is None:
            params = {}
        url = 'https://www.bseindia.com/corporates/List_Scrips.aspx'
        if not params:
            response = self.session.get(url, headers=self.generic_request_headers)
            print(response.text)
        else:
            self.get_payload()
            pprint(params)
            self.generic_request_headers['Referer'] = "https://www.bseindia.com/corporates/List_Scrips.aspx"
            response = self.session.post(url, headers={'Referer': 'https://www.bseindia.com/corporates/List_Scrips.aspx'}, data=params)
        resp = bs4.BeautifulSoup(response.text, features="html.parser")
        hidden_element = resp.findAll("div", {"class": "aspNetHidden"})
        if params:
            print(response.status_code)
            print(resp.find("table", {"class": "ContentPlaceHolder1_gvData"}))
        if page == 'home' and hidden_element:
            key = list(self.aspx_fields1.keys())[0]
            self.aspx_fields1[key] = hidden_element[0].find("input", {"id": key}).get('value', "")
            for key in self.aspx_fields2.keys():
                val = hidden_element[1].find("input", {"id": key})
                if val:
                    self.aspx_fields2[key] = val.get('value', "")

    def main(self):
        self.get_viewstate(page='home')
        self.get_viewstate(page='home', params={**self.aspx_fields1, **self.aspx_fields2, **self.inputs})


sc = Scrips()
sc.main()
