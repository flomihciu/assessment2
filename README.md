# User DP API

This is a simple Flask App using PSQL.

Setup
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
