import json
from datetime import datetime
import time
import pandas as pd

from browser.scrapers.default_scraper import AbstractScraper


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
            self.wait_and_click("xpath", self.configs["dropdown"]["input_class"])
            time.sleep(self.configs["navigation"]["pagination_timeout"])

            for _ in range(3):
                self.press_key("ARROW_DOWN")
                time.sleep(self.configs["navigation"]["pagination_timeout"])
                self.press_key("RETURN")
                time.sleep(self.configs["navigation"]["pagination_timeout"])

            school_row_selector = self.configs["table"]["schools"]

            for _ in range(self.configs["navigation"]["pages_total"]):
                for i in range(self.configs["navigation"]["results_per_page"]):
                    row_selector = school_row_selector.format(row=i + 1)
                    url = self.get_element_attribute("css_selector", row_selector, "href")
                    self.urls.append(url)

                self.wait_and_click("css_selector", self.configs["navigation"]["next_page"])
                time.sleep(self.configs["navigation"]["pagination_timeout"])

            for url in self.urls:
                try:
                    self.access_url_and_save_content(url)
                except Exception as e:
                    print(f"Unable to access page: {e}")
                    self.failed_urls.append(url)
                    continue

        except Exception as e:
            raise Exception("Failed to execute main scraping logic.") from e
        finally:
            self.browser.quit()

    def access_url_and_save_content(self, url):
        try:
            self.navigate_to_url(url)
            time.sleep(self.configs["navigation"]["load_timeout"])

            school_name = self.get_element_text("css_selector", self.configs["table"]["school_name"])
            district_and_grades_served = self.get_element_text("css_selector", self.configs["table"]["district_and_grades_served"])
            address = self.get_element_text("css_selector", self.configs["table"]["address"])
            phone = self.get_element_text("css_selector", self.configs["table"]["phone"])
            website = self.get_element_attribute("css_selector", self.configs["table"]["website"], "href")

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
