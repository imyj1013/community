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
# fast api
```
uvicorn backend.app.main:app --reload
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