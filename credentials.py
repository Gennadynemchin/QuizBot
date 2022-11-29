import os
from dotenv import load_dotenv


load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')
redis_login = os.getenv('REDIS_LOGIN')
redis_password = os.getenv('REDIS_PASSWORD')
redis_host = os.getenv('REDIS_HOST')
