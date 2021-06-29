import random
from aiogram import types
from config import dp, Form
from functions import Functions
from database import Database
from callback_and_message_handler import *


class Requests_bot:
    def __init__(self):
        self.func = Functions()
        self.db = Database('server.db')

    # Получение результата поиска
    async def result_message(self, search, message):
        if 'погода' in search or 'weather' in search:
            await self.func.parse_weather(message)

        elif 'курс' in search or 'валют' in search or 'доллар' in search or 'долар' in search or 'евро' in search or 'rate' in search:
            await self.func.parse_rate(message)

        elif 'новости' in search or'news' in search:
            text_news = search.split(' ')
            if 'новости' in search:
                text_news = text_news[text_news.index('новости')+1:]
            else:
                text_news = text_news[text_news.index('news')+1:]

            if len(text_news) > 0:
                text_news = ' '.join(text_news)
                await self.func.parse_news_words(message, text_news)
            else:
                await self.func.parse_news(message)

        elif 'статистика' in search or 'коронавирус' in search or 'covid' in search:
            await self.func.parse_stat_covid(message)

        elif 'что ты' in search or 'умеешь' in search:
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text = 'Погода', callback_data = 'weather')
            item_2 = types.InlineKeyboardButton(text = 'Курс валюты', callback_data = 'valuta')
            item_3 = types.InlineKeyboardButton(text = 'Новости', callback_data = 'news')
            item_4 = types.InlineKeyboardButton(text = 'Поиск новостей', callback_data='news_word')
            item_5 = types.InlineKeyboardButton(text = 'Коронавирус', callback_data = 'virus')
            item_6 = types.InlineKeyboardButton(text = 'Скачать аудио с Youtube', callback_data = 'click_download_audio')
            item_7 = types.InlineKeyboardButton(text = 'Системы счисления', callback_data = 'system_number')
            item_8 = types.InlineKeyboardButton(text = 'Любое число', callback_data = 'random_number')
            item_9 = types.InlineKeyboardButton(text = 'Да или нет', callback_data = 'yes_or_not')
            item_10 = types.InlineKeyboardButton(text = '1 или 2', callback_data = 'one_or_two')
            item_11 = types.InlineKeyboardButton(text = 'Что лучше?', callback_data = 'what_best')
            item_12 = types.InlineKeyboardButton(text = 'Текст в аудио', callback_data = 'convert_text_to_audio')
            item_13 = types.InlineKeyboardButton(text = 'Население', callback_data = 'population_people')
            item_14 = types.InlineKeyboardButton(text = 'Голосовое сообщение в текст', callback_data = 'convert_voice_to_text')
            item_15 = types.InlineKeyboardButton(text = 'Фото/аудио/видео файл в текст', callback_data = 'convert_audio_photo_video_to_text')
            item_16 = types.InlineKeyboardButton(text = 'Отправить разработчику анонимный отзыв', callback_data = 'answer_user')

            markup_inline.add(item_1, item_2, item_3)
            markup_inline.add(item_4, item_5)
            markup_inline.add(item_6, item_7)
            markup_inline.add(item_8, item_9, item_10)
            markup_inline.add(item_11, item_12, item_13)
            markup_inline.add(item_14)
            markup_inline.add(item_15)
            markup_inline.add(item_16)
            await message.answer('Вот что я умею\nДля полного списка команд введите /help', reply_markup=markup_inline)

        elif 'скачать аудио' in search or 'скачать музыку' in search or 'музык' in search:
            await message.answer("Введите url")
            await Form.url.set()

        elif 'youtube.com' in search or 'youtu.be' in search:
            await self.func.download_audio(message)

        elif 'конвертировать' in search:
            if 'голосово' in search:
                await message.answer('Отправьте или перешлите голосовое сообщение')
                await Form.voice_msg.set()

            elif 'в аудио' in search or ('текст' in search and 'аудио в' not in search):
                await message.answer('Напишите что конвертировать')
                await Form.text_for_convert.set()

            elif 'аудио' in search or 'фото' in search or 'видео' in search:
                await message.answer('Отправьте мне аудио файл, фотографию или видео')

            else:
                await message.answer('Вы не указали что конвертировать')

        elif 'отзыв' in search or 'написать разработчику' in search or 'пожелан' in search or 'списаться с разработчиком' in search:
            await message.answer('Введите отзыв или пожелания')
            await Form.feedback.set()

        elif 'да' in search or 'нет' in search:
            await message.answer(random.choice(('Да', 'Нет')))

        elif 'или' in search and ('один' in search or 'два' in search or '1' in search or '2' in search):
            await message.answer(random.randint(1, 2))

        elif 'лучше' in search:
            await self.func.what_the_best(message)

        elif 'любое число' in search or 'число от' in search or 'цифра от' in search or 'рандом' in search:
            await self.func.number_random(message)

        elif 'население' in search or 'сколько людей' in search:
            await self.func.parse_population(message)

        elif 'счислен' in search or 'систем' in search:
            await message.answer('Введите два числа через пробел, само число и систему счисления в которую перевести')
            await Form.number_system.set()

        elif search == 'обычный режим' or search == 'подробный режим':
            await self.db.change_settings_news(message, search)

        else:
            choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
            await message.answer(random.choice(choice_text))
