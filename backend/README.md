## Setup
# (optional) create a virtual env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install tools
pip install -r requirements.txt

# fast api
uvicorn backend.app.main:app --reload