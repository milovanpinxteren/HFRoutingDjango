
# Healthy Fridge Routing Application

## Description
Vehicle Routing of Healthy Fridge, with admin, planner, operator functionalities

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).

### Cloning the Repository
```sh
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
Setting Up a Virtual Environment
sh
Code kopiëren
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Installing Dependencies
sh
Code kopiëren
pip install -r requirements.txt
Usage
Explain how to run your project. For example:

sh
Code kopiëren
python manage.py runserver
```

### Testing
To create a dump of the database in JSON format, run the following command in the terminal:


`python manage.py dumpdata --format=json > HFRoutingApp/fixtures/db_dump.json`

Next, open the file in File Explorer and change the encoding to UTF-8:


### Configuration
#### Whitelisting IP Address for Google Maps API
To whitelist your IP address for Google Maps API, follow these steps:

- Navigate to the Google Cloud Console.
- Locate the API key and update the IP addresses as needed.

#### Environment Variables
Ensure you have a .env file set up with the necessary environment variables. Example:

`GOOGLE_MAPS_API_KEY=your_api_key`
