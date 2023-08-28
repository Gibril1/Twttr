# Twttr

Welcome to Twttr, a minimalistic replication of Twitter's (now X) backend using Django and GraphQL. This documentation will guide you through setting up and running Twttr on your local environment.

## Getting Started
1. ### Clone the Repository
To get started, clone the Twttr repository to your local machine using the following command:
 ```git clone https://github.com/Gibril1/Twttr.git```

2. ### Create your virtual environment
Create a virtual environment to isolate the project's dependencies. Use the following commands to create and activate the virtual environment:
``` python -m venv .venv ``` 

* On Windows: Activate by running  ```.venv/scripts/activate```
* On MacOS and Linux: Activate by running  ```source .venv/bin/activate```

3. ### Install Dependencies
Install the required dependencies for Twttr using pip. Navigate to the project directory and run:
```pip install -r requirements.txt```

4. ### Run Migrations 
Apply the database migrations to set up the database schema. Run the following commands:
```python manage.py makemigrations accounts group posts``` and then
```python manage.py migrate```

5. ###  Start the local development server
Launch the local development server to run Twttr. Execute the following command:
```python manage.py runserver```
You should now have Twttr up and running on your local machine. You can access it at http://localhost:8000/.



## Documentation
For detailed information on Twttr's API endpoints, we have prepared comprehensive documentation using Postman. You can access the documentation by following this link: [Twttr API Documentation](https://documenter.getpostman.com/view/22678038/2s9Y5YSi2U).

If you encounter any issues or have questions, please refer to the documentation or reach out to our support team for assistance. Happy tweeting with Twttr!


