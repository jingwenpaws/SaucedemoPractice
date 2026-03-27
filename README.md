# Web UI Automation Practice Project

This is a personal practice project I built to learn and implement Web UI automation testing using Python, Selenium WebDriver, and Pytest. 

My primary goal for this project is to explore how to structure a testing framework from scratch, aiming for a design that is both scalable and maintainable as the number of test cases grows.

## Features Implemented

Through this project, I practiced several core concepts in test automation:

* Page Object Model (POM): Separating UI locators and page interactions from the actual test logic to make the code easier to maintain.
* Data-Driven Testing (DDT): Using Pytest's `parametrize` feature to feed test data from external JSON files, separating data from the scripts.
* Configuration Management: Using YAML for environment settings and `python-dotenv` to keep sensitive credentials out of version control.
* Pytest Hooks: Customizing `conftest.py` to dynamically create log directories for each session and automatically capture screenshots upon test failures.
* Test Reporting: Integrating Allure to generate clear, step-by-step visual test reports.

## Project Structure

This is the core structure of the repository. Note that local environment files (like `.env`), virtual environments (`.venv`), and dynamically generated test outputs (logs, screenshots, Allure results) are excluded via `.gitignore`.

```text
├── config/                  
│   └── config.yaml          # Environment and browser configuration
├── data/      # Test data for data-driven testing
├── src/
│   ├── constants/           # Global constants
│   ├── pages/               # Page Object classes
│   └── utils/               # Helper utilities (e.g., data loaders, config parsers)
├── tests/                   # Pytest test cases and fixtures        
├── pytest.ini               # Pytest configuration file
├── README.md                
└── requirements.txt         # Project dependencies
```

## Setup and Installation

### 1. Clone the repository
```Bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```
### 2. Create and activate a virtual environment
```Bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```
### 3. Install dependencies
```Bash
pip install -r requirements.txt
```
### 4. Set up environment variables
Create a `.env` file in the root directory and add your local testing credentials:
```.env
STANDARD_USERNAME=your_username
STANDARD_PASSWORD=your_password
```
### 5. Install Allure Commandline (For test reporting)
* macOS: `brew install allure`
* Windows: `scoop install allure`

## Running the Tests
To execute the test suite using Pytest with the default configuration:
```Bash
pytest
```
To run the tests and generate data for the Allure report:
```Bash
pytest --alluredir=./reports/allure-results
```
Once the test execution is complete, generate and open the Allure HTML report in your browser:
```Bash
allure serve ./reports/allure-results
```
prevent stale test data or removed test cases from inflating the current test report, it is highly recommended to clean the results directory before execution. Append the `--clean-alluredir` flag to your pytest command:

```bash
pytest --alluredir=./reports/allure-results --clean-alluredir