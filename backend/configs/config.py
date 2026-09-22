import os
from pathlib import Path
from dotenv import load_dotenv

# Get backend directory -> go up one level to root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print (BASE_DIR)
env_path = BASE_DIR / "backend/.env"
load_dotenv(dotenv_path=env_path)


SECRET_KEY= os.getenv('SECRET_KEY')
DB_URI=os.getenv('POSTGRES_DB_URI')


COMPANY_NAME= os.getenv('COMPANY_NAME')
COMPANY_ADDRESS= os.getenv('COMPANY_ADDRESS')
COMPANY_PHONE=os.getenv("COMPANY_PHONE")
COMPANY_WEBSITE= os.getenv('COMPANY_WEBSITE')
COMPANY_LOGO_URL=os.getenv('COMPANY_LOGO_URL')
