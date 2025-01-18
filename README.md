# User DP API

This is a simple Flask App using API endpoints and Psycopg to interact with a PSQL database.  It allows for the easy CRUD'ing of users in a user database.

![User App](img/screenshot.png)

## Tech Stack

- **Flask**: Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.

- **PostgreSQL**: PSQL is a free and open-source relational database management system (RDBMS) emphasizing extensibility and SQL compliance.  It supports all major operating systems and handles a range of workloads from single machines to data warehouses, data lakes,[14] or web services with many concurrent users.

## Setup
1. Clone down this repo
2. Set up a virtual environment and install requirements

```bash
python -m venv my-venv-directory
pip install -r requirements.txt
```
3. Set up your PSQL users and db.  With PSQL service running:

```
psql -U postgres
```
In SQL terminal (password optional):
```psql
CREATE DATABASE user_db;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE user_db TO postgres;
```
4. Run the app
```
python app.py
```
