# School Scraper

## Overview

The `School Scraper` project is a web scraping application built with Python. It is designed to perform the following tasks:

1. **Extract Schools Information**:

   - Scrapes school details from search pages on platforms like TX Schools.
   - Structures the data into a Pandas DataFrame and saves it to a CSV file.

2. **Handle Failed URLs**:
   - Captures failed URLs during scraping and saves them to a separate CSV file for further analysis or reprocessing.

---

## Features

- **Dynamic Web Scraping**:

  - Uses Selenium to interact with dynamic web pages and extract data.
  - Handles pagination and dropdown navigation to scrape multiple pages.

- **Error Handling**:

  - Logs errors during scraping and captures failed URLs for reprocessing.

- **Data Storage**:

  - Saves scraped data and failed URLs into separate CSV files for easy access and analysis.

- **Configurable Execution**:
  - Uses JSON configuration files to define scraping logic, making it easy to adapt to different websites.

---

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher
- Poetry (for managing dependencies)

### Installation

1. **Clone the Repository**:

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
- `failed-urls.csv`: Stores the URLs that failed during scraping for further analysis or reprocessing.

## Project Structure

- `src/`: Contains the main application code.
  - `start.py`: Entry point for the application
  - `browser/`: Contains browser provider and scraping logic.
    - `providers/`: Contains the abstract browser class and the actions dictionary.
    - `scrapers/`: Contains specific scrapers for different tasks.
      - `configs/`: Stores the .json files containing the configurations for the execution.
  - `tools/`: Contains utility modules like CSV handler.

## Future Improvements and Features

If given more time, the project could be expanded and improved in the following ways:

### 1. **Architecture**

- **Microservices Architecture**:

  - Divide the project into at least four distinct microservices:
    1. **Task Shooter**: Processes the initial input to create and dispatch events that will trigger discovery tasks. It will later perform the same for enhancement tasks.
    2. **Discovery**: Scrapes school website URLs from the filtered list.
    3. **Enhancement**: Accesses each school's website to scrape additional data (e.g., address, phone, etc.).
    4. **Data Quality**: Processes the scraped data to normalize formats, correct errors, and ensure consistency.

- **Scalability**:
  - This architecture would allow the project to scale horizontally, enabling parallel processing of tasks.

---

### 2. **Orchestration**

- **Task Management**:

  - Introduce an orchestration service (used the `Task Shooter` alias in this example) to transform each scraped URL from the `Discovery` step into tasks for the `Enhancement` step.
  - Use cloud infrastructure tools like AWS Lambda to shoot and process events and EC2 to run parallel enhancement and data quality tasks, speeding up the process.

- **Data Quality Pipeline**:
  - After the `Enhancement` step, run data quality processes to clean and normalize the data.

---

### 3. **Monitoring and Observability**

- **Processing Health Monitoring**:

  - Add a microservice to oversee the health of the scraping process.
  - Use caching tools like Redis to log processing statuses in real time, avoid unnecessary costs, and provide insights for future executions.

- **Observability Tools**:
  - Integrate observability tools to monitor the scraping process and infrastructure.
  - Use managed services from AWS or other providers to track performance, errors, and resource usage.

---

### 4. **Error Handling and Resilience**

- **Dynamic Webpage Handling**:

  - Implement mechanisms to adapt to changes in webpage structures, reducing the risk of scraping failures.

- **Anti-Bot Detection**:
  - Add features to handle anti-bot mechanisms, such as rotating proxies, user agents, and CAPTCHA solving.

---

### 5. **Cloud-Native Deployment**

- **Containerization**:

  - Package the application into Docker containers for easy deployment and scaling.

- **Serverless Execution**:
  - Use serverless platforms like AWS Lambda to run scraping tasks on demand, reducing infrastructure costs.

---

### 6. **Error Handling and Logging**

- **Error Logging**:

  - Logs errors during scraping to help identify and resolve issues.

- **Failed URLs**:
  - Captures failed URLs and saves them to a separate CSV file for reprocessing.

---

### 7. **Requests and Responses Handling**

- **Direct API Interaction**:

  - Add a class to handle HTTP requests and responses, enabling the scraper to interact directly with APIs or endpoints exposed by the sources.
  - This would allow the scraper to bypass the need for browser-based scraping, significantly reducing costs and improving performance.

- **Cost Efficiency**:

  - By leveraging API endpoints, the project could dramatically reduce infrastructure costs (e.g., browser instances, memory usage) and execution time.

- **Scalability**:

  - Direct API interaction would make the scraper more scalable, as it would no longer rely on resource-intensive browser automation.

- **Fallback Mechanism**:
  - Implement a fallback mechanism to switch between browser-based scraping and API-based scraping, depending on the availability of endpoints or anti-bot measures.

---

### 8. **Storage Service**

- **Centralized Data Storage**:

  - Introduce a storage service to register every step of the process for later use.
  - This would create a valuable warehouse of school information that can be used for further historical analytics at any time in the future.

- **Cloud Storage Solutions**:

  - Leverage services like AWS S3 to store scraped data, failed URLs, and processed results in a scalable manner.

- **Data Accessibility**:
  - Ensure that data is easily accessible for downstream processes, such as analytics, reporting, or machine learning pipelines.

---
