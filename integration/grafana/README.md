# Introduction

The goal of this PoC is to explore data integration with Grafana in order to identify interesting data for users. 

# Installation

For testing purposes, I advise to use MySql in a docker:

```bash
$ docker network create --subnet=172.20.0.0/16 mysql_net

$ docker run --name grafana_mysql --network mysql_net --ip 172.20.0.100 -e MYSQL_ROOT_PASSWORD=password -d mysql:latest

```
For grafana, I used a VM.

Please follow official documentation.

# Create tables in MySql

Use the ``create_tables.py`` to create the SQL tables. One can also extract get the tables architecture from the file.

If you don't use the default values for your database defined in the Installation part, please change the content of the variables ``DB_IP``, ``DB_USER``, ``DB_PASSWORD`` in the ``database.py`` file.

# The script `fill_grafana.py`
## Requirements
To create a python virtual env to install requirements:
```bash
$ python3 -m venv grafana_venv
$ source grafana_venv/bin/activate
```
To install the requirements:
```bash
$ pip install -r requirements.txt
```

Get your token for Rudder's API
```bash
$ echo "API_TOKEN=<your_token>" > .env
```

Modify RUDDER_ENDPOINT in the script according your needs

## Scripts's documentation
The ``database.py`` contains one class **Database**. It connects to MySql db and manipulate the db. The ``update_table`` function can be used to insert a row or update an existing one. In this file, one should modify the variables ``DB_IP``, ``DB_USER``, ``DB_PASSWORD`` according the needs.

The ``fill_grafana.py`` contains one class **RudderAPI** that connects to Rudder's API and fetches data. One must add his API token. The IP given in the variable ``RUDDER_ENDPOINT`` belongs to the Rudder lab and should be changed.

# Grafana's dashboard configuration
This dashboard gives examples of what can be done with the data extrated from Rudder.

Please use the ``grafana_dashboard_jsonmodel.json`` to import the full dashboard into Grafana.

You can also extract the SQL queries from the file.

![alt text](image.png)

# Crontab 
Add an executable file in /etc/crontab.daily to execute ``fill_grafana.py``. For example:
```bash
#!/bin/bash

cd /home/vagrant
source grafana_venv/bin/activate
python3 fill_grafana.py >> /tmp/grafana_log.log
```