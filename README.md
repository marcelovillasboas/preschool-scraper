# School Scraper

## Overview

The `school scraper` project is a web scraping application built with Python. It is designed to perform the following task:

**Extract Schools Information:**

- Scrapes schools details from search pages on platforms like TX Schools. (in this example)
- Structures the data into a Pandas DataFrame and saves it to a CSV file.
- Includes insights on the number of schools found in the search. // TODO

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher
- Poetry (for managing dependencies)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/marcelovillasboas/preschool-scraper.git

   cd preschool-scraper
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment:**

   ```bash
   poetry shell
   ```

### Configuration

1. **Environment Variables:**

   Set the following environment variables as needed:

   - 'HEADLESS': 'True'

   Example:

   ```bash
   export HEADLESS=True
   ```

### Running the Project

1. **Start the Application:**

   Run the application using Poetry

   ```bash
   poetry run python src/start.py
   ```

### Results

The results of an execution will be saved in files at the root of the project:

- `txschools-data.csv`: Stores the result found in the search pages;
- `insights.csv`: Stores the information on the schools execution volumetry after it's finished;

## Project Structure

- `src/`: Contains the main application code.
  - `start.py`: Entry point for the application
  - `browser/`: Contains browser provider and scraping logic.
    - `providers/`: Contains the abstract browser class and the actions dictionary.
    - `scrapers/`: Contains specific scrapers for different tasks.
      - `configs/`: Stores the .json files containing the configurations for the execution.
  - `tools/`: Contains utility modules like CSV handler.

## Error Handling and Logging

- Common errors include failures loading the schools individual pages.
