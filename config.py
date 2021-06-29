import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    url = State()
    voice_msg = State()
    text_for_convert = State()
    feedback = State()
    number_system = State()
    number_random = State()
    what_the_best = State()
    mailing = State()
    search_news = State()


token = os.environ['token']
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

user_email = os.environ['user_email']
user_password = os.environ['user_password']
user_id = int(os.environ['user_id'])
bot_id = int(os.environ['bot_id'])

logging.basicConfig(filename="info/info.log", format = u'[%(levelname)s][%(asctime)s] %(funcName)s:%(lineno)s: %(message)s', level='INFO')
logger = logging.getLogger()
