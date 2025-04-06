import json
from datetime import datetime
import time
import pandas as pd

from browser.scrapers.default_scraper import AbstractScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class TXSchoolsScraper(AbstractScraper):
    def __init__(self):
        super().__init__()
        try:
            self.configs = json.loads(self.get_configs('txschools'))
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception("Failed to load scraper configuration.") from e
        
        if not self.configs:
            raise Exception("Scraper configuration is empty.")
        
        self.content = []
        self.urls = []
        self.failed_urls = []

    def scrape(self):
        try:
            self.execute_before(self.configs)
            self.execute_main()
            self.execute_after()
            self.save_data(self.content_df, self.configs["storage"]["filename"], self.configs["storage"]["headers"])
            print("Data saved to file.")
        except Exception as e:
            print(f"An error occurred during scraping: {e}")

    def execute_main(self):
        try:
            time.sleep(self.configs["navigation"]["load_timeout"])
            self.browser_provider.click(self.configs["dropdown"]["input_class"])
            time.sleep(self.configs["navigation"]["pagination_timeout"]) 

            actions = ActionChains(self.browser)
            for _ in range(3): 
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(self.configs["navigation"]["pagination_timeout"])
                actions.send_keys(Keys.RETURN).perform()
                time.sleep(self.configs["navigation"]["pagination_timeout"])

            school_row_selector = self.configs["table"]["schools"]

            for _ in range(self.configs["navigation"]["pages_total"]):
                for i in range(self.configs["navigation"]["results_per_page"]):
                    row_selector = school_row_selector.format(row=i + 1)
                    element = self.browser.find_element(By.CSS_SELECTOR, row_selector)
                    # element = self.browser.find_element(By.CSS_SELECTOR, f"#app_top > div.MuiGrid-root.MuiGrid-container > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-lg-8 > div:nth-child(2) > div > div > div > table > tbody > tr:nth-child({i + 1}) > td:nth-child(1) > div > a")
                    url = element.get_attribute('href')
                    self.urls.append(url)
                
                self.browser.find_element(By.CSS_SELECTOR, self.configs["navigation"]["next_page"]).click()
                time.sleep(self.configs["navigation"]["pagination_timeout"])

            for i in range(len(self.urls)):
                try: 
                    self.access_url_and_save_content(self.urls[i])
                except Exception as e:
                    print(f"Unable to access page: {e}")
                    self.failed_urls.append(self.urls[i])
                    continue

        except Exception as e:
            raise Exception("Failed to execute main scraping logic.") from e
        finally:
            self.browser.quit()

    def access_url_and_save_content(self, url):
        try:
            self.browser.get(url)
            time.sleep(self.configs["navigation"]["load_timeout"])
            
            school_name = self.browser.find_element(By.CSS_SELECTOR, self.configs["table"]["school_name"]).text
            district_and_grades_served = self.browser.find_element(By.CSS_SELECTOR, self.configs["table"]["district_and_grades_served"]).text
            address = self.browser.find_element(By.CSS_SELECTOR, self.configs["table"]["address"]).text
            phone = self.browser.find_element(By.CSS_SELECTOR, self.configs["table"]["phone"]).text
            website = self.browser.find_element(By.CSS_SELECTOR, self.configs["table"]["website"]).get_attribute('href')
            district = district_and_grades_served.split("Grades Served")[0].strip()
            grades_served = district_and_grades_served.split("Grades Served")[1].strip()
            grades_served = grades_served.lstrip(": ").strip()
            address = address.replace("ADDRESS:\n", "").strip()
            phone = phone.replace("PHONE:\n", "").strip()
            district = district.replace("District: ", "").strip()

            self.content.append({
                "Company": school_name,
                "District": district,
                "Grades Served": grades_served,
                "Address": address,
                "Phone": phone,
                "Website": website
            })
        
        except Exception as e:
            print(f"Failed to access URL: {url}. Error: {e}")

    def execute_after(self):
        try:
            self.content_df = self.transform_to_df()
        except Exception as e:
            raise Exception("Failed to execute post-scraping logic.") from e        

    def transform_to_df(self):
        try:
            columns = self.configs["consolidation"]["columns"]
            df = pd.DataFrame(self.content, columns=columns)
            df = df.assign(execution_date=datetime.now().isoformat())
        except Exception as e:
            raise Exception("Failed to transform data into DataFrame.") from e
        return df
