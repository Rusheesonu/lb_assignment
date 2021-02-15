from lxml import html
import string
import time
import json
import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pymongo
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("logger")


class Crawler(object):

    def run(self):
        company_index_data = self.fetch_company_index()
        log.info("Company index has been fetched successfully")
        
        with open("company_index.json", "w") as f:
            json.dump(company_index_data, f)
            log.info("Company index file written successfully")
        company_profiles_data = self.fetch_company_details_url_reponse()

        with open("company_profiles.json", "w") as f:
            json.dump(company_profiles_data, f)
            log.info("Company profile data file written successfully")






    def fetch_company_index(self):
        alphabet_string = string.ascii_uppercase
        # Creating a list with all the alphabets from A - Z
        alphabets_list = list(alphabet_string)
        company_dict_list = []
        for i in range(0, len(alphabets_list)):
            ## We are initialising page number to 1 , because everypage starts from 1.
            page_number = 1
            ## We have this intialised to Next , because when there are no pages left we need to change the alphabet.
            alphabet_change_id = "Next"
            while alphabet_change_id == "Next":
                listing_url = f"https://www.adapt.io/directory/industry/telecommunications/{alphabets_list[i]}-{page_number}"
                s = requests.Session()
                ## if they block or refuse connection we wait and retry for 5 times.
                retries = Retry(total=5, backoff_factor=1, status_forcelist=[503, 404])
                s.mount(listing_url, HTTPAdapter(max_retries=retries))
                r = s.get(listing_url)
                root = html.fromstring(r.text)
                company_name = root.xpath('//a[@class="list-link"]/text()')
                company_url = root.xpath('//a[@class="list-link"]/@href')
                ## This try expect block is to check if we still have anymore pages left for the alphabet or should we change the alphabet.
                try:
                    alphabet_change_id = root.xpath('//a[@class="pg-next"]/text()')[0]
                    alphabet_change_id = alphabet_change_id.replace(" >", "")
                ## we would need an except block because, when there are no more records present for the alphabet the xpath raises an exception because there is no data.
                except IndexError:
                    ## we return NA, when the page is empty so we could come out of the while loop and change the alphabet.
                    alphabet_change_id = "NA"
                ## since we have many company records for each page we iterate over records and append them to the list.
                for x in range(0, len(company_name)):
                    company_dict = {}
                    company_dict["company_name"] = company_name[x]
                    company_dict["source_url"] = company_url[x]
                    company_dict_list.append((company_dict))
                print(alphabet_change_id)
                ## if we are in the loop we keep incrementing page number till we fetch the complete data.
                page_number = page_number + 1
            ## we are incrementing i , when we come out of the while loop so we go to the next alphabet.
            i = i + 1

        return company_dict_list


    # # we take the file generated above and start crawling each record for the company data.
    # # product_crawling from the site map file generated above


    def fetch_company_details_url_reponse(self):
        company_profiles_list = []
        ## opening the listing data file generated above.
        with open("company_index.json") as f:
            ## we iterate through each record and request the url from the record and parse it.
            json_data = f.read()
            each = json.loads(json_data)
            for data in each:
                company_extract_data = dict()
                company_url = data.get("source_url")
                company_url = "https://www.adapt.io" + company_url
                company_name = data.get("company_name")
                s = requests.Session()
                retries = Retry(total=5, backoff_factor=1, status_forcelist=[503])
                s.mount(company_url, HTTPAdapter(max_retries=retries))
                ## Requesting product url here to get the data.
                r = s.get(company_url)
                root = html.fromstring(r.text)
                company_data = root.xpath("//script[@type='application/json']/text()")[0]   
                companies_data = json.loads(company_data)
                ## we call extraction function below.
                company_extract_data = self.fetch_company_details_extraction(company_name,company_url,companies_data)
                company_profiles_list.append(company_extract_data)
                ## We have a json in the page backend with all the data required, we are capturing the json here.
                
        return company_profiles_list


    ## Mongo Db Table creations
    ##creating DB , collections and Adding data
    def fetch_company_details_extraction(self,company_name,company_url,companies_data):
        company_data = companies_data
        company_profiles_dict = dict()
        try:
            company_location = company_data.get("props").get("pageProps").get("seoCompanyData").get("seoLocation")
        except:
            company_location = ""
        try:
            company_website = company_data.get("props").get("pageProps").get("seoCompanyData").get("website")
        except:
            company_website = ""
        try:
            company_webdomain = company_website.replace("http://www.","")
        except:
            company_webdomain = ""
        try:    
            company_industry = company_data.get("props").get("pageProps").get("seoCompanyData").get("industry")
        except:
            company_industry = ""
        try:
            company_employee_size = company_data.get("props").get("pageProps").get("seoCompanyData").get("headCount")
        except:
            company_employee_size = ""
        try:
            company_revenue = company_data.get("props").get("pageProps").get("seoCompanyData").get("revenue")
        except:
            company_revenue = ""
        try:            
            company_person_details = company_data.get("props").get("pageProps").get("topContacts")
        except:
            company_person_details = ""
        try:
            company_description = company_data.get("props").get("pageProps").get("seoCompanyData").get("description")
        except:
            company_description = "" 
        try:           
            similar_companies = company_data.get("props").get("pageProps").get("similarCompanies")
        except:
            similar_companies = []
        similar_companies_list = []
        ## iterating over all similar companies available and adding them to a list.|            
        try:
            for company in similar_companies:
                similar_companies_list.append(company.get("name"))
            ## Returning string if there are no similar companies available.    
            if similar_companies_list == []:
                similar_companies_list = "No similar companies available"
            contact_details_list = []
            ## Because we have more than one people records for each company we iterate them and write to a list.
            for i in company_person_details:    
                contact_details = {}
                contact_details['contact_name'] = i.get("name")
                contact_details['contact_jobtitle'] = i.get("title")
                contact_details['contact_email_domain'] = i.get("email")
                contact_details['contact_email_domain'] = contact_details['contact_email_domain'].split("@")[-1]
                contact_details_list.append((contact_details))
            company_profiles_dict['company_name'] = company_name
            company_profiles_dict['company_location'] = company_location
            company_profiles_dict['company_website'] = company_website
            company_profiles_dict['company_webdomain'] = company_webdomain
            company_profiles_dict['company_industry'] = company_industry
            company_profiles_dict['company_employee_size'] = company_employee_size
            company_profiles_dict['company_revenue'] = company_revenue
            company_profiles_dict['company_description'] = company_description
            company_profiles_dict['contact_details'] = contact_details_list
            company_profiles_dict['similar_companies'] = similar_companies_list
        except:
            log.info('Invalid json')
        return company_profiles_dict




    def write_data_to_db(self):
        myclient = MongoClient("localhost", 27017)
        ## Database creation
        db = myclient["lb_assignment"]
        ##collection 1  - company-index
        company_index_collection = db["comapany-index"]
        ##collection 2 - company-profiles
        company_profiles_collection = db["comapny-profiles"]

        with open("company_index.json") as f:
            company_index_data = json.load(f)

        # this if statement is to check if there are one or many records and write based on number of records present
        if isinstance(company_index_data, list):
            ## writing data to collection 1
            company_index_collection.insert_many(company_index_data)
        else:
            company_index_collection.insert_one(company_index_data)

        with open("company_profiles.json") as f:
            company_profiles_data = json.load(f)

        if isinstance(company_profiles_data, list):
            ## writing data to collection 2
            company_profiles_collection.insert_many(company_profiles_data)
        else:
            company_profiles_collection.insert_one(company_profiles_data)

        return True


if __name__ == "__main__":
    Crawl_obj = Crawler()
    Crawl_obj.run()
    Crawl_obj.write_data_to_db()
