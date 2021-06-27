import os
import logging
from aiogram import Bot, Dispatcher

token = os.environ['token']
bot = Bot(token=token)
dp = Dispatcher(bot)

user_email = os.environ['user_email']
user_password = os.environ['user_password']
user_id = int(os.environ['user_id'])

logging.basicConfig(filename="info/info.log", format = u'[%(levelname)s][%(asctime)s] %(funcName)s:%(lineno)s: %(message)s', level='INFO')
logger = logging.getLogger()
