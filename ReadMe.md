
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


#### Database
Each Operator, hub, spot should have exactly one Location.

If multiple spots on 1 physical location, make more locations

> E.g.:  HospitalA has 3 machines on floor1, floor2 and floor3
> - Make 3 machines
> - Make 3 spots and add each machine to each spot
> - Make 3 locations (HospitalA_floor1, HospitalA_floor2, etc)
> - Assign each spot to each location


> When adding a driver/operator
> - Add a location of the driver's home adress
> - Make a user for the driver
> - Make a driver, and assign the user and location to driver

> When adding a hub
> - Add a location of the Hub's location
> - Make the hub and assign the location to it


#### Functionality, objectives and constraints
Finding the routes with the shortest total distance while respecting
- Vehicle capacity
- Driver familarity/mandatory driver-location assignment 

Flow:
- A base route is constructed based on insertion
  - Start with mandatory locations (from OperatorLocationLink)
  - Insert non-mandatory locations until capacity constraint met
  - pass to the GA
- The Genetic Algorithm (GA)
  - Makes a population by shuffling non-mandatory non-preserved (first 2, last2, mandatory stops) stops in a route
  - For number of generations
    - Evaluates fitness (Total distance, if capacity overload -> fitness = 'inf')
    - Tournament selection to get parents
    - Keep best solutions (elitism)
    - Crossover to generate new population
      - Switching non-mandatory non-preserved stops between routes
      - Mutation based on probability
        - Removing a stop from a route and adding it to another.

### TODOS
- 