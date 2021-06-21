import os
import telebot
import logging

token = os.environ['token']
bot = telebot.TeleBot(token)

user_email = os.environ['user_email']
user_password = os.environ['user_password']
user_id = int(os.environ['user_id'])
host = os.environ['host']
user = os.environ['user']
password = os.environ['password']
db_name = os.environ['db_name']

logging.basicConfig(filename="info/info.log", format = u'[%(levelname)s][%(asctime)s] (%(funcName)s:%(lineno)s): %(message)s', level='INFO')
logger = logging.getLogger()
