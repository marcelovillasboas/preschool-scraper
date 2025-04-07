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
            if len(self.failed_urls_df) > 0: self.save_data(self.failed_urls_df, self.configs["storage"]["failed_filename"], self.configs["storage"]["failed_headers"])
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
            self.wait_for_element("css_selector", self.configs["table"]["school_name"], timeout=self.configs["navigation"]["load_timeout"])

            school_name = self._extract_school_name()
            district_and_grades_served = self._extract_district_and_grades_served()
            address = self._extract_address()
            phone = self._extract_phone()
            website = self._extract_website()
            total_students = self._extract_total_students()

            district, grades_served = self._process_district_and_grades(district_and_grades_served)
            processed_address = self._process_address(address)
            phone = self._process_phone(phone)

            self.content.append({
                "Company": school_name,
                "District": district,
                "Grades Served": grades_served,
                "Full Address": processed_address["Full Address"],
                "Street Address": processed_address["Street Address"],
                "City": processed_address["City"],
                "State": processed_address["State"],
                "ZIP Code": processed_address["ZIP Code"],
                "Phone": phone,
                "Website": website,
                "Total Students": total_students
            })

        except Exception as e:
            raise Exception(f"Failed to access URL: {url}. Error: {e}")

    def execute_after(self):
        try:
            self.content_df = self.transform_to_df(self.content, self.configs["consolidation"]["columns"], add_execution_date=True)
            self.failed_urls_df = self.transform_to_df(self.failed_urls, self.configs["storage"]["failed_headers"], add_execution_date=True)
        except Exception as e:
            raise Exception("Failed to execute post-scraping logic.") from e

    def transform_to_df(self, data, columns, add_execution_date=False):
        try:
            df = pd.DataFrame(data, columns=columns)
            if add_execution_date:
                df = df.assign(execution_date=datetime.now().isoformat())
            return df
        except Exception as e:
            raise Exception("Failed to transform data into DataFrame.") from e

    def _extract_school_name(self):
        return self.get_element_text("css_selector", self.configs["table"]["school_name"])

    def _extract_district_and_grades_served(self):
        return self.get_element_text("css_selector", self.configs["table"]["district_and_grades_served"])

    def _extract_address(self):
        return self.get_element_text("css_selector", self.configs["table"]["address"])

    def _extract_phone(self):
        return self.get_element_text("css_selector", self.configs["table"]["phone"])

    def _extract_website(self):
        return self.get_element_attribute("css_selector", self.configs["table"]["website"], "href")
    
    def _extract_total_students(self):
        return self.get_element_text("css_selector", self.configs["table"]["total_students"])

    def _process_district_and_grades(self, district_and_grades_served):
        district = district_and_grades_served.split("Grades Served")[0].strip()
        district = district.replace("District: ", "").strip()
        grades_served = district_and_grades_served.split("Grades Served")[1].strip()
        grades_served = grades_served.lstrip(": ").strip()
        return district, grades_served

    def _process_address(self, address):
        try:
            address = address.replace("ADDRESS:\n", "").strip()

            parts = address.split(", ")
            street_address = parts[0]
            city = parts[1]
            state_zip = parts[2] 

            state, zip_code = state_zip.split(" ")

            return {
                "Full Address": address,
                "Street Address": street_address,
                "City": city,
                "State": state,
                "ZIP Code": zip_code
            }
        except Exception as e:
            raise Exception(f"Failed to process address: {address}. Error: {e}")

    def _process_phone(self, phone):
        return phone.replace("PHONE:\n", "").strip()

    # def capture_screenshot(self, filename="screenshot.png"):
    #     """Saves a screenshot to the project root folder. Function used for debugging and testing."""
    #     self.browser.save_screenshot(filename)
    #     print(f"Screenshot saved as {filename}")

    # def scroll_to_bottom(self):
    #     """Scroll to the bottom of the page. Used for debugging and testing"""
    #     try:
    #         self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         logging.info("Scrolled to the bottom of the page.")
    #     except Exception as e:
    #         logging.error(f"Failed to scroll to the bottom of the page: {e}")
    #         raise
