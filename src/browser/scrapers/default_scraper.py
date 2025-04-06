import os
import logging
from abc import ABC, abstractmethod
from browser.provider.generic_browser_provider import GenericBrowserProvider
from tools.csv_handler import CsvHandler
from browser.provider.actions.dict import action_dict
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AbstractScraper(ABC):
    def __init__(self):
        self.browser_provider = GenericBrowserProvider()
        self.browser = self.browser_provider.browser
        self.base_dir = self._get_base_dir()

    @staticmethod
    def _get_base_dir() -> str:
        """Get the base directory of the project."""
        try:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        except Exception as e:
            logging.error(f"Failed to get base directory: {e}")
            raise

    @abstractmethod
    def scrape(self):
        """Abstract method to scrape data. To be implemented in subclasses."""
        pass

    @abstractmethod
    def execute_main(self):
        """Abstract method to execute main scraping tasks. To be implemented in subclasses."""
        pass

    def execute_before(self, configs):
        """Execute actions defined in the 'before' script configuration."""
        before = configs["script"]["before"]
        if before:
            for action in before:
                if action_dict[action] is None:
                    logging.error(f"Action '{action}' is not defined.")
                    raise ValueError(f"Action '{action}' is not defined.")
                try:
                    action_dict[action](self.browser, before[action])
                except Exception as e:
                    logging.error(f"Failed to execute 'after' action '{action}': {e}")
                    raise
            return

    def execute_after(self, configs):
        """Execute actions defined in the 'after' script configuration."""
        after = configs["script"]["after"]
        if after:
            for action in after:
                if action_dict[action] is None:
                    logging.error(f"Action '{action}' is not defined.")
                    raise ValueError(f"Action '{action}' is not defined.")
                try:
                    action_dict[action](self.browser, after[action])
                except Exception as e:
                    logging.error(f"Failed to execute 'after' action '{action}': {e}")
                    raise
            return

    def get_configs(self, config_type: str) -> str:
        """Load and return configuration data from a JSON file."""
        config_path = os.path.join(self.base_dir, 'src', 'browser', 'scrapers', 'configs', f'{config_type}.json')
        try:
            with open(config_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"Configuration file '{config_path}' not found.")
            raise
        except IOError as e:
            logging.error(f"Error reading configuration file '{config_path}': {e}")
            raise

    def save_data(self, data: list, filename: str, headers: list) -> None:
        """Save data to a CSV file."""
        try:
            self.storage = CsvHandler(filename, headers)
            self.storage.save_data(data)
            logging.info(f"Data successfully saved to '{filename}'.csv.")
        except Exception as e:
            logging.error(f"Unable to save data to '{filename}': {e}")
            raise

    def read_data(self, filename: str, headers: list) -> pd.DataFrame:
        """Read data from a CSV file."""
        try:
            self.storage = CsvHandler(filename, headers)
            df = self.storage.read_data()
            return df
        except Exception as e:
            logging.error(f"Data successfully read from '{filename}'.csv.")
            raise

    def wait_and_click(self, by: By, identifier: str, timeout: int = 10):
        """
        Wait for an element to be clickable and click it.

        :param by: The method to locate the element (e.g., By.ID, By.CLASS_NAME).
        :param identifier: The identifier of the element (e.g., ID or class name).
        :param timeout: The maximum time to wait for the element to be clickable.
        """
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((by, identifier))
            )
            element.click()
        except Exception as e:
            logging.error(f"Failed to click element with {by}='{identifier}': {e}")
            raise
