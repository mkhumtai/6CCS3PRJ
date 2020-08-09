# 6CCS3PRJ Final Year Project
#### Title: Examining the risk factors and patterns of Avian Influenza (HPAI H5N1) outbreaks through Cluster Analysis
#### Author: Mananchaya Khumtai
#### Supervisor: Dr. Kathleen Steinhöfel
#### Student ID: 1741542

<br />


- Dashboard developed with the help of [Flask Dashboard Now UI](https://appseed.us/admin-dashboards/flask-nowui-dashboard) (MIT License)
- All piece of code written with the help of others is stated on the header of the file
- Sample data can be found in 'sample_data_empres' folder


## Built With:

- Flask
- SQLite database
- SQLAlchemy ORM
- UI Kit: **[NowUI Dashboard](https://flask-now-ui-dashboard.appseed.us/login.html)** (Free version) provided by **Creative-Tim**

## Prerequisites:
Please ensure that all requirements are satisfied  <br>
(included in requirements.txt)
- selenium
- pytest
- wtforms
- email-validator == 1.0.5
- config
- geopy
- shapely
- numpy
- pandas
- scikit-learn
- flask
- flask_login
- flask_migrate
- flask_wtf
- flask_sqlalchemy
- flask_bcrypt
- gunicorn
- rq


## Acessing through heroku
- Dashboard can be accessed remotely through heroku at https://k1763918.herokuapp.com/<br />
- New users are required to register before accessing all pages <br /> <br />

Possible issues:
- Please note that you may experience slow access due to low traffic <br />
- https://k1763918.herokuapp.com/analysis.html may have trouble loading due to large amount of data<br>
Please try reloading the webpage
- Due to free usage of Heroku and Heroku-Redis, large amount of data cannot be added to heroku as it may cause timeout error


## Build from sources

```bash
$ cd avian
$
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv --no-site-packages env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv --no-site-packages env
$ # .\env\Scripts\activate
$ 
$ # Install requirements
$ pip3 install -r requirements.txt
$
$ # Start Redis Queue
$ redis-server
$ rq worker
$
$ # Set the FLASK_APP environment variable
$ (Unix/Mac) export FLASK_APP=run.py
$ (Windows) set FLASK_APP=run.py
$ (Powershell) $env:FLASK_APP = ".\run.py"
$
$ # Set up the DEBUG environment
$ # (Unix/Mac) export FLASK_ENV=development
$ # (Windows) set FLASK_ENV=development
$ # (Powershell) $env:FLASK_ENV = "development"
$
$ # Run the application
$ # --host=0.0.0.0 - expose the app on all network interfaces (default 127.0.0.1)
$ # --port=5000    - specify the app port (default 5000)  
$ flask run --host=0.0.0.0 --port=5000
$
$ # Access the app in browser: http://127.0.0.1:5000/
```

<br />

## Deployment

The app is provided with a basic configuration to be executed in  [Gunicorn](https://gunicorn.org/), and [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/).

<br />

### [Gunicorn](https://gunicorn.org/)
---

Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for UNIX.

> Install using pip

```bash
$ pip install gunicorn
```

> Start Redis Queue
```
$ redis-server
$ rq worker
```
> Start the app using gunicorn binary

```bash
$ gunicorn -t 90 --bind 0.0.0.0:8001 run:app
Serving on http://localhost:8001
```

Visit `http://localhost:8001` in your browser. The app should be up & running.


<br />

### [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/)
---

Waitress (Gunicorn equivalent for Windows) is meant to be a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones that live in the Python standard library.

> Install using pip

```bash
$ pip install waitress
```
> Start Redis Queue
```
$ redis-server
$ rq worker
```
> Start the app using [waitress-serve](https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html)

```bash
$ waitress-serve --port=8001 run:app
Serving on http://localhost:8001
```

Visit `http://localhost:8001` in your browser. The app should be up & running.

<br />

## Running Tests
Test files:
- test_app.py
- test_clustering.py
- test_selenium.py

Please note that test_selenium.py will require chrome to be installed in your computer<br /> <br /> 
If you encounter chromedriver error:  <br /> 
- Ensure that a chromedriver for your operating system is downloaded (Only chromedriver for mac is included)
- Ensure that the chromedriver you downloaded has the same version as your chrome browser
- If you need to check/update your chrome version: chrome://settings/help

```bash
$ pytest
```

For more information:
```bash
$ pytest -v
```

For a specific file:
```bash
$ cd tests
$ pytest [test_file.py]
```