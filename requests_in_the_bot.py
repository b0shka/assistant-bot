from aiogram import types
from config import bot, Form
from functions import Functions
from database import Database
from callback_and_message_handler import *
from list_requests import *
import random
import re


class Requests_bot:
    def __init__(self):
        self.func = Functions()
        self.db = Database('server.db')

    # Получение результата поиска
    async def result_message(self, search, message):
        if bool(re.search('|'.join(weather_main), search)) or bool(re.search('|'.join(weather), search)):
            try:
                city = self.db.get_city(message.from_user.id, message.from_user.first_name, message.from_user.last_name)[0]
            except TypeError:
                await self.db.add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
                city = self.db.get_city(message.from_user.id, message.from_user.first_name, message.from_user.last_name)[0]

            if city == '':
                await message.answer('Сначала укажите свой город в /settings')
            else:
                await self.func.parse_weather(message, city)

        elif bool(re.search('|'.join(rate_main), search)) or bool(re.search('|'.join(rate), search))  :
            await self.func.parse_rate(message)

        elif bool(re.search('|'.join(news_main), search)) or bool(re.search('|'.join(news), search)):
            text_news = search.split(' ')

            try:
                if 'новости' in search:
                    text_news = text_news[text_news.index('новости')+1:]
                else:
                    text_news = text_news[text_news.index('news')+1:]
            except ValueError:
                search_text = re.findall('|'.join(news), search)[0]
                text_news = text_news[text_news.index(search_text)+1:]

            if len(text_news) > 0:
                text_news = ' '.join(text_news)
                await self.func.parse_news_words(message, text_news)
            else:
                await self.func.parse_news(message)

        elif bool(re.search('|'.join(covid_main), search))  or bool(re.search('|'.join(covid), search))  :
            await self.func.parse_stat_covid(message)

        elif bool(re.search('|'.join(skills_main), search)) or bool(re.search('|'.join(skills), search)):
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text = 'Курс валюты', callback_data = 'valuta')
            item_2 = types.InlineKeyboardButton(text = 'Новости', callback_data = 'news')
            item_3 = types.InlineKeyboardButton(text = 'Коронавирус', callback_data = 'virus')
            item_4 = types.InlineKeyboardButton(text = 'Поиск новостей', callback_data='news_word')
            item_5 = types.InlineKeyboardButton(text = 'Скачать аудио с Youtube', callback_data = 'click_download_audio')
            item_6 = types.InlineKeyboardButton(text = 'Рандомное число', callback_data = 'random_number')
            item_7 = types.InlineKeyboardButton(text = 'Что лучше?', callback_data = 'what_best')
            item_8 = types.InlineKeyboardButton(text = 'Да или нет', callback_data = 'yes_or_not')
            item_9 = types.InlineKeyboardButton(text = '1 или 2', callback_data = 'one_or_two')
            item_10 = types.InlineKeyboardButton(text = 'Текст в аудио', callback_data = 'convert_text_to_audio')
            item_11 = types.InlineKeyboardButton(text = 'Системы счисления', callback_data = 'system_number')
            item_12 = types.InlineKeyboardButton(text = 'Население', callback_data = 'population_people')
            item_13 = types.InlineKeyboardButton(text = 'Население стран', callback_data = 'population_country')
            item_14 = types.InlineKeyboardButton(text = 'Голосовое сообщение в текст', callback_data = 'convert_voice_to_text')
            item_15 = types.InlineKeyboardButton(text = 'Фото/аудио/видео файл в текст', callback_data = 'convert_audio_photo_video_to_text')
            item_16 = types.InlineKeyboardButton(text = 'Отправить разработчику анонимный отзыв', callback_data = 'answer_user')

            markup_inline.add(item_1, item_2, item_3)
            markup_inline.add(item_4, item_5)
            markup_inline.add(item_6, item_7)
            markup_inline.add(item_8, item_9)
            markup_inline.add(item_10, item_11)
            markup_inline.add(item_12, item_13)
            markup_inline.add(item_14)
            markup_inline.add(item_15)
            markup_inline.add(item_16)
            await message.answer('Вот что я умею\nДля полного списка команд введите /help', reply_markup=markup_inline)

        elif bool(re.search('|'.join(download_audio_main), search)) or bool(re.search('|'.join(download_audio), search)):
            await message.answer("Введите url")
            await Form.url.set()

        elif 'youtube.com' in search or 'youtu.be' in search:
            await self.func.download_audio(message)

        elif bool(re.search('|'.join(convert_main), search)) or bool(re.search('|'.join(convert), search)):
            if bool(re.search('|'.join(vioce_to_text_main), search))  or bool(re.search('|'.join(vioce_to_text), search))  :
                await message.answer('Отправьте или перешлите голосовое сообщение')
                await Form.voice_msg.set()

            elif bool(re.search('|'.join(text_to_audio_main), search))  or bool(re.search('|'.join(text_to_audio), search))  :
                await message.answer('Напишите что конвертировать')
                await Form.text_for_convert.set()

            elif bool(re.search('|'.join(audio_photo_video_to_text_main), search))  or bool(re.search('|'.join(audio_photo_video_to_text), search))  :
                await message.answer('Отправьте мне аудио файл, фотографию или видео')

            else:
                await message.answer('Что конвертировать? (голосовое сообщение, фото, аудио, видео в текст/текст в аудио)')
                await Form.what_convert.set()

        elif bool(re.search('|'.join(feedback_main), search)) or bool(re.search('|'.join(feedback), search)):
            await message.answer('Введите отзыв или пожелания')
            await Form.feedback.set()

        elif (' да ' in search or ' нет ' in search) and 'или' in search:
            await message.answer(random.choice(('Да', 'Нет')))

        elif 'или' in search and ('один' in search or 'два' in search or '1' in search or '2' in search):
            await message.answer(random.randint(1, 2))

        elif ' лучше ' in search:
            await self.func.what_the_best(message)

        elif bool(re.search('|'.join(random_number_main), search)) or bool(re.search('|'.join(random_number), search)):
            await self.func.number_random(message)

        elif bool(re.search('|'.join(population), search)):
            if bool(re.search('|'.join(country), search)):
                await self.func.parse_population_country(message)
            else:
                await self.func.parse_population(message)

        elif bool(re.search('|'.join(system_number_main), search)) or bool(re.search('|'.join(system_number), search)):
            await message.answer('Введите два числа через пробел, само число и систему счисления в которую перевести')
            await Form.number_system.set()

        elif search == 'обычный режим' or search == 'подробный режим':
            await self.db.change_settings_news(message, search)

        elif search == 'удалить мои данные':
            await message.answer('Вы уверены? (yes/no)')
            await Form.confirmation_deletion.set()

        elif ('куб' in search or 'кости' in search) and (bool(re.search('|'.join(throw_main), search)) or bool(re.search('|'.join(throw), search))):
            await bot.send_dice(message.from_user.id)

        else:
            choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
            await message.answer(random.choice(choice_text))
