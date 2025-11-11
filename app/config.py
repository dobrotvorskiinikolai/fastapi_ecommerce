import os
from dotenv import load_dotenv


load_dotenv()
DATABASE = os.getenv("DATABASE")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"