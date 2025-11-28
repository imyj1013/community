## Setup
# (optional) create a virtual env
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
# install tools
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
# download model
```
python download_model.py
```
# DB Mysql
```
mysql -u root -p
CREATE DATABASE community CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
python create_table.py
```
# fast api
```
uvicorn app.main:app --reload
```