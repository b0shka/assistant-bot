#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as BS
import speech_recognition as sr
from random import randint
import telebot
from telebot import types
import requests
import random
import re
import fnmatch
import os
import sys
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import time
import youtube_dl
#import pafy
import subprocess
import pyshorteners
import logging
import pytesseract
from PIL import Image
from gtts import gTTS
from moviepy.editor import *
from threading import Thread
from config import *

bot = telebot.TeleBot(token)
global user_email
global user_password
user_email = email
user_password = password

logging.basicConfig(filename="info.log", format = u'[%(levelname)s] %(asctime)s: %(message)s', level='INFO')
global logger
logger = logging.getLogger()


# Команда для вывода списка всех команд бота
@bot.message_handler(commands = ['help'])
def help(message):
	access = verify_id(message)
	if access == 1:
		send_mess = '<b>Вот полный список запросов:</b>\n\nНовости\nНовости и слова по которым искать\nПогода\nСтатистика по коронавирусу\nКурс валюты\nЧто ты умеешь\nСкачать аудио (и позже скинуть ссылку на видео из YouTube)\nДа или нет\nОдин или два\nЧто лучше\nЧто лучше (и дописать сразу 2 действия через или)\nРандомное число\nРандомное число от ... до ...\nСократить ссылку (и позже скинуть ссылку)\nСистема счисление\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nОтправьте голосовое сообщение, и я распознаю вашу просьбу\nКонвертировать голосовое сообщение и позже отправьте или перешлите голосовое сообщение\nПросто скиньте фотографию или аудио файл и я конвертирую их в текст\nКонвертировать видео и позже скиньте его\nКонвертировать текст и позже напишите сам текст\nНаписать отзыв (и позже написать текст)'
		bot.send_message(message.chat.id, send_mess, parse_mode='html')
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')
	add_message(message, message.text)


# Команда для пописки на рассылку
@bot.message_handler(commands = ['subscribe'])
def subscribe(message):
	access = verify_id(message)
	if access == 1:
		check_subscribe(message)
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')
	add_message(message, message.text)
	logger.info('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] Подписка на рассылку')


# Команда для отписки от рассылки
@bot.message_handler(commands = ['unsubscribe'])
def unsubscribe(message):
	access = verify_id(message)
	if access == 1:
		check_unsubscribe(message)
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')
	add_message(message, message.text)
	logger.info('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] Отписка от рассылки')


# Команда для старта бота
@bot.message_handler(commands = ['start'])
def start(message):
	access = verify_id(message)
	if access == 1:
		global markup
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		item1 = types.KeyboardButton('Новости')
		item2 = types.KeyboardButton('Курс валюты')
		item3 = types.KeyboardButton('Погода')
		item4 = types.KeyboardButton('Что ты умеешь?')
		item5 = types.KeyboardButton('Статистика по коронавирусу')
		markup.add(item1, item2, item3, item4, item5)
		send_mess = f"<b>Привет {message.from_user.first_name}!</b>\nЯ твой ассистент, можешь меня спрашивать и я постараюсь ответить!\nВы можете спросить у меня: \nПогоду\nКурс валюты\nПоследние новости\nНовости по ключевым словам\nСтатистика по коронавирусу\nРадномное число\nСокращение ссылки\nПеревести числа в нужную систему счисления\n\n<b>НОВИНКА!!!</b>\nГолосовой поиск (просто отправьте голосовое сообщение)\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nСкачать аудио из видео на YouTube, скинув на него ссылку\nКонвертация голосового сообщения в текст\nКонвертация аудио файла в текст\nКонвертация фотографии в текст\nКонвертация видео в текст\nКонвертация текста в аудио\nВозможность отправить разработчику анонимный отзыв\n\nДля полного списка команд введите /help"
		bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup = markup)
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')

	create_table(message)
	add_new_user(message)


# Отправка на почту log и БД по команде
@bot.message_handler(commands = ['information'])
def send_information_users(message):
	try:
		send_email(message)
		bot.send_message(message.chat.id, 'Отправка завершена', parse_mode='html')
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[Отправка информации о пользователях] ' + str(e))


# Письменный поиск
@bot.message_handler(content_types=["text"])
def message_text(message):
	access = verify_id(message)
	if access == 1:
		result_message(message, message.text)
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')
	add_message(message, message.text)


# Голосовой поиск
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
	access = verify_id(message)
	if access == 1:
		try:
			file_info = bot.get_file(message.voice.file_id)
			downloaded_file = bot.download_file(file_info.file_path)

			with open("audio.ogg", 'wb') as f:
			    f.write(downloaded_file)

			convert = subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])

			r = sr.Recognizer()
			add_new_user(message)
			with sr.AudioFile('audio.wav') as source:
				audio = r.listen(source)
				search = r.recognize_google(audio, language="ru_RU").lower()
			result_message(message, search)
			add_message(message, '[Голосовой поиск] ' + str(search))
		except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера или ваше голосовое сообщение пустое', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование аудио в текст] ' + str(e))

		try:
			os.remove('audio.ogg')
			os.remove('audio.wav')
		except:
			pass
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')


# Конвертация фотографии в текст
@bot.message_handler(content_types=["photo"])
def convet_photo(message):
	access = verify_id(message)
	if access == 1:
		add_new_user(message)
		try:
			bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')

			file_info = bot.get_file(message.photo[-1].file_id)
			downloaded_file = bot.download_file(file_info.file_path)
			convert_name_file = 'img.jpg'
			with open(convert_name_file, 'wb') as f:
			    f.write(downloaded_file)
			
			converting_photo(message, convert_name_file)
			
			bot.send_message(message.chat.id, result_convert_photo, parse_mode='html')
			add_message(message, '[Конвертация фото в текст] ' + str(result_convert_photo))
		except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера или фотографию неудается распознать', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование фото в текст] ' + str(e))

		try:
			os.remove(convert_name_file)
		except:
			pass

	else:
		bot.send_message(message.chat.id, access, parse_mode='html')


# Конвертация аудио в текст
@bot.message_handler(content_types=['audio'])
def convert_audio_file(message):
	access = verify_id(message)
	if access == 1:
		add_new_user(message)
		try:
			bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')

			file_info = bot.get_file(message.audio.file_id)
			downloaded_file = bot.download_file(file_info.file_path)
			convert_name_file = 'audio.ogg'
			with open(convert_name_file, 'wb') as f:
			    f.write(downloaded_file)

			convert_audio(message, convert_name_file)
		except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера или файл неудается распознать', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование аудио в текст] ' + str(e))

		try:
			os.remove(convert_name_file)
			os.remove('audio.wav')
		except:
			pass
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')


# Конвертация документа в текст
@bot.message_handler(content_types=['document'])
def convert_document(message):
	access = verify_id(message)
	if access == 1:
		add_new_user(message)
		audio_name = ['ogg', 'opus', 'mp3', 'wav', 'aac']
		photo_name = ['jpeg', 'jpg', 'png']
		video_name = ['mp4', 'avi', 'mkv']

		bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')

		try:
			file_name = message.document.file_name.split('.')

			if file_name[-1] in photo_name:
				file_info = bot.get_file(message.document.file_id)
				downloaded_file = bot.download_file(file_info.file_path)
				convert_name_file = 'img.' + str(file_name[-1])
				with open(convert_name_file, 'wb') as f:
					f.write(downloaded_file)
				
				converting_photo(message, convert_name_file)

				bot.send_message(message.chat.id, result_convert_photo, parse_mode='html')
				add_message(message, '[Конвертация фото в текст] ' + str(result_convert_photo))

			elif file_name[-1] in audio_name:
				file_info = bot.get_file(message.document.file_id)
				downloaded_file = bot.download_file(file_info.file_path)
				convert_name_file = 'audio.ogg'
				with open(convert_name_file, 'wb') as f:
					f.write(downloaded_file)

				convert_audio(message, convert_name_file)

				try:
					os.remove('audio.wav')
				except:
					pass

			elif file_name[-1] in video_name:
				file_info = bot.get_file(message.document.file_id)
				downloaded_file = bot.download_file(file_info.file_path)
				convert_video_file = 'video.' + str(file_name[-1])
				with open(convert_video_file, 'wb') as f:
					f.write(downloaded_file)

				video = VideoFileClip(convert_video_file)
				audio = video.audio
				audio.write_audiofile('audio.mp3')
				convert_name_file = 'audio.mp3'

				convert_audio(message, convert_name_file)

				try:
					os.remove(convert_video_file)
					os.remove('audio.wav')
				except:
					pass
		except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера или файл неудается распознать', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование документа в текст] ' + str(e))

		try:
			os.remove(convert_name_file)
		except:
			pass
	else:
		bot.send_message(message.chat.id, access, parse_mode='html')

# Конвертация видео в текст
@bot.message_handler(content_types=['video'])
def convert_video(message):
	try:
		bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')

		file_info = bot.get_file(message.video.file_id)
		downloaded_file = bot.download_file(file_info.file_path)
		with open("video.mp4", 'wb') as f:
		    f.write(downloaded_file)

		video = VideoFileClip('video.mp4')
		audio = video.audio
		audio.write_audiofile('audio.mp3')
		convert_name_file = 'audio.mp3'

		convert_audio(message, convert_name_file)		

	except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера или видео неудается распознать', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование видео в текст] ' + str(e))

	try:
		os.remove('video.mp4')
		os.remove(convert_name_file)
		os.remove('audio.wav')
	except:
		pass


# Обработка нажатой кнопки в что ты умеешь и их функции
@bot.callback_query_handler(func = lambda call: True)
def answer(call):
	if call.data == 'weather':
		parse_weather(call.message)
		add_message(call.message, call.data)

	elif call.data == 'valuta':
		parse_valuta(call.message)
		add_message(call.message, call.data)

	elif call.data == 'news':
		parse_news(call.message)
		add_message(call.message, call.data)

	elif call.data == 'news_word':
		send = bot.send_message(call.message.chat.id, 'Введите ключевые слова')
		bot.register_next_step_handler(send, get_word_news)
		add_message(call.message, call.data)

	elif call.data == 'virus':
		parse_stat_covid(call.message)
		add_message(call.message, call.data)

	elif call.data == 'yes_or_not':
		text = ('Да', 'Нет')
		answer = random.choice(text)
		bot.send_message(call.message.chat.id, answer, parse_mode='html')
		add_message(call.message, call.data)

	elif call.data == 'one_or_two':
		answer = randint(1, 2)
		bot.send_message(call.message.chat.id, answer, parse_mode='html')
		add_message(call.message, call.data)

	elif call.data == 'random_number':
		send = bot.send_message(call.message.chat.id, 'Введите диапазон чисел через пробел (3 45)')
		bot.register_next_step_handler(send, number_random)
		add_message(call.message, call.data)

	elif call.data == 'what_best':
		send = bot.send_message(call.message.chat.id, 'Введите 2 действия через или (поесть или поспать)')
		bot.register_next_step_handler(send, what_the_best)
		add_message(call.message, call.data)

	elif call.data == 'system_number':
		send = bot.send_message(call.message.chat.id, 'Введите два числа через пробел, само число и систему счисления в которую перевести')
		bot.register_next_step_handler(send, number_system)
		add_message(call.message, call.data)

	#elif call.data == 'click_download_video':
		#send = bot.send_message(call.message.chat.id, 'Введите url')
		#bot.register_next_step_handler(send, download_video)
		#add_message(call.message, call.data)

	elif call.data == 'click_download_audio':
		send = bot.send_message(call.message.chat.id, 'Введите url')
		bot.register_next_step_handler(send, download_audio)
		add_message(call.message, call.data)

	elif call.data == 'small_link':
		send = bot.send_message(call.message.chat.id, 'Введите ссылку')
		bot.register_next_step_handler(send, small_link)
		add_message(call.message, call.data)

	elif call.data == 'convert_audio_to_text':
		send = bot.send_message(call.message.chat.id, 'Отправьте или перешлите голосовое сообщение')
		bot.register_next_step_handler(send, convert_voice_text)
		add_message(call.message, call.data)

	elif call.data == 'convert_text_to_audio':
		send = bot.send_message(call.message.chat.id, 'Напишите что конвертировать')
		bot.register_next_step_handler(send, convert_text_voice)
		add_message(call.message, call.data)

	elif call.data == 'answer_user':
		send = bot.send_message(call.message.chat.id, 'Введите отзыв или пожелания')
		bot.register_next_step_handler(send, answer_user)
		add_message(call.message, call.data)

	elif call.data == 'convert_audio_photo_video_to_text':
		bot.send_message(call.message.chat.id, 'Отправьте фото, аудио файл или видео')
		add_message(call.message, call.data)

	elif call.data == 'convert_video_youtube_to_text':
		send = bot.send_message(call.message.chat.id, 'Введите url')
		bot.register_next_step_handler(send, convert_video_youtube_to_text)
		add_message(call.message, call.data)


# Функции
# Результаты поиска
def result_message(message, text_message):
	search = text_message.lower()

	if 'курс' in search or 'валют' in search or 'доллар' in search or 'долар' in search or 'евро' in search or 'rate' in search:
		parse_valuta(message)

	elif search == 'новости' or search == 'new':
		parse_news(message)

	elif 'новости' in search or 'new' in search:
		if 'новости' in search:
			text_news = search.split('новости')
		elif 'news' in search:
			text_news = search.split('news')
		news_words(message, text_news[1])

	elif 'погода' in search or 'weather' in search:
		parse_weather(message)

	elif 'статистика' in search or 'коронавирус' in search or 'covid' in search:
		parse_stat_covid(message)

	elif 'что ты' in search or 'умеешь' in search:
		markup_inline = types.InlineKeyboardMarkup()
		item_1 = types.InlineKeyboardButton(text = 'Погода', callback_data = 'weather')
		item_2 = types.InlineKeyboardButton(text = 'Курс валюты', callback_data = 'valuta')
		item_3 = types.InlineKeyboardButton(text = 'Новости', callback_data = 'news')
		item_4 = types.InlineKeyboardButton(text = 'Коронавирус', callback_data = 'virus')
		item_5 = types.InlineKeyboardButton(text = 'Да или нет', callback_data = 'yes_or_not')
		item_6 = types.InlineKeyboardButton(text = '1 или 2', callback_data = 'one_or_two')
		item_7 = types.InlineKeyboardButton(text = 'Любое число', callback_data = 'random_number')
		item_8 = types.InlineKeyboardButton(text = 'Что лучше?', callback_data = 'what_best')
		item_9 = types.InlineKeyboardButton(text = 'Сократить ссылку', callback_data = 'small_link')
		item_10 = types.InlineKeyboardButton(text = 'Системы счисления', callback_data = 'system_number')
		item_11 = types.InlineKeyboardButton(text = 'Новости по ключевым словам', callback_data='news_word')
		#item_12 = types.InlineKeyboardButton(text = 'Скачать видео с Youtube', callback_data = 'click_download_video')
		item_12 = types.InlineKeyboardButton(text = 'Скачать аудио с Youtube', callback_data = 'click_download_audio')
		item_13 = types.InlineKeyboardButton(text = 'Конвертация голосового сообщения с текст', callback_data = 'convert_audio_to_text')
		item_14 = types.InlineKeyboardButton(text = 'Конвертация теста в аудио', callback_data = 'convert_text_to_audio')
		item_15 = types.InlineKeyboardButton(text = 'Отправить разработчику анонимный отзыв', callback_data = 'answer_user')
		item_16 = types.InlineKeyboardButton(text = 'Конвертировать фото/аудио/видео файл в текст', callback_data = 'convert_audio_photo_video_to_text')
		#item_19 = types.InlineKeyboardButton(text = 'Получить текстовую версию видео на Youtube', callback_data = 'convert_video_youtube_to_text')

		markup_inline.add(item_1, item_2, item_3)
		markup_inline.add(item_4, item_5, item_6)
		markup_inline.add(item_7, item_8,item_9)
		markup_inline.add(item_10, item_11)
		markup_inline.add(item_12, item_13)
		markup_inline.add(item_14, item_15)
		markup_inline.add(item_16)
		#markup_inline.add(item_19)
		bot.send_message(message.chat.id, 'Вот что я умею\nДля полного списка команд введите /help', reply_markup = markup_inline)

	#elif 'скачать видео' in search or 'видео' in search:
		#send = bot.send_message(message.chat.id, 'Введите url')
		#bot.register_next_step_handler(send, download_video(message.chat.id))

	elif 'скачать аудио' in search or 'скачать музыку' in search or 'музык' in search:
		send = bot.send_message(message.chat.id, 'Введите url')
		bot.register_next_step_handler(send, download_audio)

	elif 'youtube.com' in search or 'youtu.be' in search: 
		download_audio(message)

	elif 'ссылку' in search or 'ссылку' in search or 'сократить' in search:
		send = bot.send_message(message.chat.id, 'Введите ссылку')
		bot.register_next_step_handler(send, small_link)

	elif 'конвертировать в текст' in search or 'голосово' in search:
		send = bot.send_message(message.chat.id, 'Отправьте или перешлите голосовое сообщение')
		bot.register_next_step_handler(send, convert_voice_text)

	elif 'конвертировать в аудио' in search or 'конвертировать текст' in search:
		send = bot.send_message(message.chat.id, 'Напишите что хотите конвертировать')
		bot.register_next_step_handler(send, convert_text_voice)

	elif 'аудио файл' in search or 'фото' in search or 'видео' in search:
		bot.send_message(message.chat.id, 'Отправьте мне аудио файл,  фотографию или видео')

	elif 'отзыв' in search or 'написать разработчику' in search or 'пожелания' in search or 'оставить' in search or 'отправить' in search:
		send = bot.send_message(message.chat.id, 'Введите отзыв или пожелания')
		bot.register_next_step_handler(send, answer_user)

	elif 'да' in search or 'нет' in search:
		text = ('Да', 'Нет')
		answer = random.choice(text)
		bot.send_message(message.chat.id, answer, parse_mode='html')

	elif 'один' in search or 'два' in search or '1' in search or '2' in search:
		answer = randint(1, 2)
		bot.send_message(message.chat.id, answer, parse_mode='html')

	elif 'лучше' in search:
		try:
			text = search[10:]
			if text == '':
				send = bot.send_message(message.chat.id, 'Введите два действия через или (поесть или поспать)', parse_mode='html')
				bot.register_next_step_handler(send, what_the_best)
			else:
				text = text.split(' ')
				if len(text) == 3:
					test = randint(1, 2)
					if test == int('1'):
						bot.send_message(message.chat.id, text[0], parse_mode='html')
					elif test == int('2'):
						bot.send_message(message.chat.id, text[2], parse_mode='html')
				elif len(text) == 2:
					test = randint(1, 2)
					if test == int('1'):
						bot.send_message(message.chat.id, text[0], parse_mode='html')
					elif test == int('2'):
						bot.send_message(message.chat.id, text[1], parse_mode='html')
				else:
					bot.send_message(message.chat.id, 'Ошибка в записи', parse_mode='html')
		except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Что лучше] ' + str(e))

	elif 'любое число' in search or 'число от' in search or 'цифра от' in search or 'рандом' in search:
		try:
			l = len(search)
			integ = []
			i = 0
			while i < l:
				search_int = ''
				a = search[i]
				while '0' <= a <= '9':
					search_int += a
					i +=1
					if i < l:
						a = search[i]
					else:
						break
				i += 1
				if search_int != '':
					integ.append(int(search_int))
			if len(integ) == 0:
				send = bot.send_message(message.chat.id, 'Введите диапазон чисел через пробел (3 45)')
				bot.register_next_step_handler(send, number_random)
			else:
				number = randint(int(integ[0]), int(integ[1]))
				bot.send_message(message.chat.id, number, parse_mode='html')
		except Exception as e:
			bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
			logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Рандомное число] ' + str(e))

	elif 'население' in search or 'сколько людей' in search:
		parse_how_much_people(message)

	elif 'счисления' in search or 'систем' in search:
		send = bot.send_message(message.chat.id, 'Введите два числа через пробел, само число и систему счисления в которую перевести')
		bot.register_next_step_handler(send, number_system)

	else:
		text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею')
		answer = random.choice(text)
		bot.send_message(message.chat.id, answer, parse_mode='html')


# Создание таблиц если их нет
def create_table(type_message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()

			sql.execute("""CREATE TABLE IF NOT EXISTS users (
				user_id INTEGER NOT NULL,
				name VARCHAR(50) NOT NULL,
				last_name VARCHAR(100),
				time_message DATETIME DEFAULT CURRENT_TIMESTAMP,
				status BOOLEAN);""")
			db.commit()

			sql.execute("""CREATE TABLE IF NOT EXISTS message (
				user_id INTEGER NOT NULL,
				name VARCHAR(50) NOT NULL,
				last_name VARCHAR(100),
				text_message TEXT NOT NULL,
				time_message DATETIME DEFAULT CURRENT_TIMESTAMP);""")
			db.commit()
	except Exception as e:
		logger.error('[' + str(type_message.from_user.first_name) + ' ' + str(type_message.from_user.last_name) + ' ' + str(type_message.from_user.id) + '] [create_table] ' + str(e))


# Оправка на почту файлов с информацией
def send_email(message):
	try:
		msg = MIMEMultipart()
		msg['Subject'] = 'Данные'
		body = 'Отправка log и базы данных'
		msg.attach(MIMEText(body, 'plain'))
		try:
			part = MIMEApplication(open('info.log', 'rb').read())
			part.add_header('Content-Disposition', 'attachment', filename = 'info.log')
			msg.attach(part)
		except:
			pass
		try:
			part = MIMEApplication(open('server.db', 'rb').read())
			part.add_header('Content-Disposition', 'attachment', filename = 'server.db')
			msg.attach(part)
		except:
			pass
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(user_email, user_password)
		server.sendmail(user_email, user_email, msg.as_string())
		server.quit()
		file_log = open("info.log", "w")
		file_log.close()
	except Exception as e:
		logger.error('[send_email] ' + str(e))


# Добавление нового пользователя в БД
def add_new_user(message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()
			result = 0
			for i in sql.execute("SELECT user_id FROM users;"):
				if message.from_user.id == i[0]:
					result += 1
				else:
					result += 0

			if result == 0:
				sql.execute(f"INSERT INTO users (user_id, name, last_name, status) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, message.from_user.last_name, 0))
				db.commit()
				logger.info('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] Создан новый пользователь')
	except sqlite3.OperationalError:
		create_table(message)
		add_new_user(message)
	except Exception as e:
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [add_new_user] ' + str(e))


# Добавление сообщения в БД
def add_message(message, text_message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()
			sql.execute(f"INSERT INTO message (user_id, name, last_name, text_message) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, message.from_user.last_name, text_message))
			db.commit()
	except sqlite3.OperationalError:
		create_table(message)
		add_new_user(message)
		add_message(message, text_message)
	except Exception as e:
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [add_message] ' + str(e))


# Проверка на подписку при подписке
def check_subscribe(message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()
			sql.execute(f"SELECT status FROM users WHERE user_id = '{message.from_user.id}'")
			user_status = sql.fetchone()

		if user_status[0] == 1:
			bot.send_message(message.chat.id, 'Вы уже подписаны', parse_mode='html')
		else:
			subscribe_mailing(message)
	except sqlite3.OperationalError:
		create_table(message)
		add_new_user(message)
		add_message(message, message.text)
		check_subscribe(message)
	except TypeError:
		create_table(message)
		add_new_user(message)
		add_message(message, message.text)
		check_subscribe(message)
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Проверка на не подписку] ' + str(e))


# Проверка на подписку при отписке
def check_unsubscribe(message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()
			sql.execute(f"SELECT status FROM users WHERE user_id = '{message.from_user.id}'")
			user_status = sql.fetchone()

		if user_status[0] == 0:
			bot.send_message(message.chat.id, 'Вы и не подписаны', parse_mode='html')
		else:
			unsubscribe_mailing(message)
	except sqlite3.OperationalError:
		create_table()
		add_new_user(message)
		add_message(message, message.text)
		check_unsubscribe(message)
	except TypeError:
		create_table(message)
		add_new_user(message)
		add_message(message, message.text)
		check_subscribe(message)
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Проверка на подписку] ' + str(e))


# Подписка на рассылку
def subscribe_mailing(message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()

			sql.execute(f"UPDATE users SET status = 1 WHERE user_id = '{message.from_user.id}'")
			db.commit()

		bot.send_message(message.chat.id, 'Вы успешно подписаны', parse_mode='html')
		mailing = Thread(target=mailing_subscribe_users, args=(message,))
		mailing.start()
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Подписка на рассылку] ' + str(e))


# Отписка от рассылки
def unsubscribe_mailing(message):
	try:
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()

			sql.execute(f"UPDATE users SET status = 0 WHERE user_id = '{message.from_user.id}'")
			db.commit()

		bot.send_message(message.chat.id, 'Вы успешно отписаны', parse_mode='html')
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Отписка от рассылки] ' + str(e))


# Получение списка подписанных пользователей
def get_subscribe_user():
	try:
		global subscribe_users
		subscribe_users = []
		people = []
		with sqlite3.connect('server.db') as db:
			sql = db.cursor()

			for i in sql.execute(f"SELECT user_id FROM users WHERE status = 1"):
				subscribe_users.append(i[0])
	except Exception as e:
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [get_subscribe_user] ' + str(e))


# Отправка рассылки по времени
def mailing_subscribe_users(message):
	try:
		while True:
			get_subscribe_user()
			if str(time.strftime("%H:%M:%S")) == str("18:00:00"):
				try:
					for i in subscribe_users:
						mailing_message(message, i)
					send_email(message)
				except Exception as e:
					logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + '] [Отправка log и БД] ' + str(e))
	except Exception as e:
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [mailing_subscribe_users] ' + str(e))


# Сообщение рассылки
def mailing_message(message, id_user):
	try:
		mailing_text = '<b>Новости:</b>\n'
		# Новости
		r = requests.get('https://yandex.ru/news/')
		html = BS(r.content, 'html.parser')
		i = 0
		while i != 15:
			for el in html.select('.mg-card'):
				if i == 15:
					break
				title = el.select('.mg-card__title')
				news = title[0].text
				mailing_text += str(news) + '\n'
				i += 1

		mailing_text += '\n<b>Курс валюты:</b>\n'

		# Курс валюты
		r = requests.get('https://www.sberometer.ru/cbr/')
		html = BS(r.content, 'html.parser')

		for el in html.select('.zebra-2'):
			title = el.select('.b')
			mailing_text +=  'Курс доллара ' + str(title[0].text) + '\n'
			mailing_text +=  'Курс евро ' + str(title[1].text) + '\n'
			break

		r = requests.get('https://www.calc.ru/Bitcoin-k-rublyu-online.html')
		html = BS(r.content, 'html.parser')

		for el in html.select('.t18'):
			title = el.select('b')[1].text.replace(' ', '.', 2)
			mailing_text += 'Курс биткоина ' + str(title) + '\n'
			break

		mailing_text += '\n<b>Статистика коронавируса:</b>\n'

		# Статистика коронавируса
		# Статистика в Перми
		r = requests.get('https://permkrai.ru/antivirus/')
		html = BS(r.content, 'html.parser')
		data = []

		for el in html.select('.col-sm-3'):
			number = el.select('.snafu__value')
			data.append(number[0].text)

		infected = data[0].split()[1]
		try:
			died = data[5].split()[1]
		except IndexError:
			died = 0

		mailing_text += '<b>Статистика в Перми:</b>\nЗараженных сегодня - ' + str(infected) + '\nУмерло сегодня - ' + str(died) + '\n'

		# Статистика в России
		r = requests.get('https://coronavirusnik.ru/')
		html = BS(r.content, 'html.parser')
		mailing_text += '<b>Статистика в России:</b>\n'

		for el in html.select('.cases'):
			number = el.select('.plus')
			edit_stat = number[0].text.replace('(', '').replace(')', '')
			mailing_text += 'Зараженных сегодня - ' + str(edit_stat) + '\n'
			break
		for el in html.select('.deaths'):
			number = el.select('.plus')
			edit_stat = number[0].text.replace('(', '').replace(')', '')
			mailing_text += 'Умерло сегодня - ' + str(edit_stat) + '\n'
			break

		# Статистика по миру
		r = requests.get('https://coronavirus-monitor.info/')
		html = BS(r.content, 'html.parser')
		world_stat = []
		x = 0

		for el in html.select('.info_blk'):
			number = el.select('sup')
			edit_stat = number[0].text.replace(' ', '')
			world_stat.append(edit_stat)
			x += 1
			if x == 3:
				break

		mailing_text += '<b>Статистика по миру:</b>\nЗараженных сегодня - ' + str(world_stat[0] + '\nУмерло сегодня - ' + str(world_stat[2]))

		bot.send_message(id_user, mailing_text, parse_mode='html')
	except Exception as e:
		bot.send_message(id_user, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Сообщение с рассылкой] ' + str(e))


# Парсинг новостей
def parse_news(type_message):
	try:
		r = requests.get('https://yandex.ru/news/')
		html = BS(r.content, 'html.parser')
		i = 0
		while i != 15:
			for el in html.select('.mg-card'):
				if i == 15:
					break
				title = el.select('.mg-card__title')
				link = el.select('.mg-card__link')
				news = title[0].text
				link_text = link[0]['href']
				bot.send_message(type_message.chat.id, news + ' (' + link_text + ')', parse_mode='html')
				i += 1
	except Exception as e:
		bot.send_message(type_message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(type_message.from_user.first_name) + ' ' + str(type_message.from_user.last_name) + ' ' + str(type_message.from_user.id) + '] [Парсинг новостей] ' + str(e))

def news_words(message, text_news):
	try:
		r = requests.get(f'https://newssearch.yandex.ru/news/search?from=tabbar&text={text_news}')
		html = BS(r.content, 'html.parser')
		i = 0
		while i != 15:
			try:
				for el in html.select('.news-search-story'):
					if i == 15:
						break
					title = el.select('.news-search-story__title')
					news = title[0].text
					bot.send_message(message.chat.id, news, parse_mode='html')
					i += 1
			except IndexError:
				break
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Парсинг новостей по ключевым словам] ' + str(e))


# получение ключевых слов для поиска новостей
def get_word_news(message):
	words = message.text
	news_words(message, words)


# Парсинг курса валюты
def parse_valuta(type_message):
	try:
		r = requests.get('https://www.sberometer.ru/cbr/')
		html = BS(r.content, 'html.parser')

		for el in html.select('.zebra-2'):
			title = el.select('.b')
			bot.send_message(type_message.chat.id, 'Курс доллара ' + str(title[0].text), parse_mode='html')
			bot.send_message(type_message.chat.id, 'Курс евро ' + str(title[1].text), parse_mode='html')
			break
	except Exception as e:
		bot.send_message(type_message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(type_message.from_user.first_name) + ' ' + str(type_message.from_user.last_name) + ' ' + str(type_message.from_user.id) + '] [Парсинг курса валюты] ' + str(e))

	try:
		r = requests.get('https://www.calc.ru/Bitcoin-k-rublyu-online.html')
		html = BS(r.content, 'html.parser')

		for el in html.select('.t18'):
			title = el.select('b')[1].text.replace(' ', '.', 2)
			bot.send_message(type_message.chat.id, 'Курс биткоина ' + str(title), parse_mode='html')
			break
	except Exception as e:
		bot.send_message(type_message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(type_message.from_user.first_name) + ' ' + str(type_message.from_user.last_name) + ' ' + str(type_message.from_user.id) + '] [Парсинг курса валюты] ' + str(e))


# Парсинг погоды
def parse_weather(type_message):
	try:
		r = requests.get('https://yandex.ru/pogoda/perm')
		html = BS(r.content, 'html.parser')

		for el in html.select('.fact__temp'):
			title = el.select('.temp__value')
			bot.send_message(type_message.chat.id, 'В Перми сейчас ' + str(title[0].text) + ' градусов по Цельсию', parse_mode='html')
			break
	except Exception as e:
		bot.send_message(type_message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(type_message.from_user.first_name) + ' ' + str(type_message.from_user.last_name) + ' ' + str(type_message.from_user.id) + '] [Парсинг погоды] ' + str(e))


# Парсинг статистики по коронавирусу
def parse_stat_covid(type_message):
	try:
		# Статистика в Перми
		r = requests.get('https://permkrai.ru/antivirus/')
		html = BS(r.content, 'html.parser')
		data = []

		for el in html.select('.col-sm-3'):
			number = el.select('.snafu__value')
			data.append(number[0].text)

		infected = data[0].split()[1]
		try:
			died = data[5].split()[1]
		except IndexError:
			died = 0

		bot.send_message(type_message.chat.id, 'Статистика в Перми:\nЗараженных сегодня - ' + str(infected) + '\nУмерло сегодня - ' + str(died), parse_mode='html')

		# Статистика в России
		r = requests.get('https://coronavirusnik.ru/')
		html = BS(r.content, 'html.parser')
		russia_stat = 'Статистика в России:\n'

		for el in html.select('.cases'):
			number = el.select('.plus')
			edit_stat = number[0].text.replace('(', '').replace(')', '')
			russia_stat += 'Зараженных сегодня - ' + str(edit_stat) + '\n'
			break
		for el in html.select('.deaths'):
			number = el.select('.plus')
			edit_stat = number[0].text.replace('(', '').replace(')', '')
			russia_stat += 'Умерло сегодня - ' + str(edit_stat)
			break

		bot.send_message(type_message.chat.id, russia_stat, parse_mode='html')

		# Статистика по миру
		r = requests.get('https://coronavirus-monitor.info/')
		html = BS(r.content, 'html.parser')
		world_stat = []
		x = 0

		for el in html.select('.info_blk'):
			number = el.select('sup')
			edit_stat = number[0].text.replace(' ', '')
			world_stat.append(edit_stat)
			x += 1
			if x == 3:
				break

		bot.send_message(type_message.chat.id, 'Статистика по миру:\nЗараженных сегодня - ' + str(world_stat[0] + '\nУмерло сегодня - ' + str(world_stat[2])), parse_mode='html')
	except Exception as e:
		bot.send_message(type_message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(type_message.from_user.first_name) + ' ' + str(type_message.from_user.last_name) + ' ' + str(type_message.from_user.id) + '] [Парсинг статистики по коронавирусу] ' + str(e))


# Скачивание видео с YouTube
'''def download_video(message):
	try:
		url = message.text
		video = pafy.new(url)
		streams = video.streams
		best = video.getbest()
		bot.send_message(message.chat.id, 'Скачивание началось', parse_mode='html')
		best.download()

		bot.send_message(message.chat.id, 'Скачивание завершено', parse_mode='html')
		bot.send_message(message.chat.id, 'Отправка', parse_mode='html')

		download_dir = (os.path.abspath(__file__)).split('/')
		download_dir.pop(-1)
		place_download = ''
		for i in download_dir:
			place_download += i + '/'

		for i in os.listdir(place_download):
			if fnmatch.fnmatch(i, '*.mp4'):
				os.rename(i, 'video.mp4')

		video = open('video.mp4', 'rb')
		bot.send_video(message.chat.id, video)
		add_message(message, message.text)
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Скачивание видео с YouTube] ' + str(e))
	os.remove('video.mp4')'''


# Само скачивание аудио с видео на YouTube
def downloading_audio(message):
	try:
		ydl_opts = {
		    'format': 'bestaudio/best',
		    'postprocessors': [{
		        'key': 'FFmpegExtractAudio',
		        'preferredcodec': 'mp3',
		        'preferredquality': '192',
		    }],
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		    ydl.download([url])
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Скачивание аудио с YouTube] ' + str(e))


# Скачивание аудио с YouTube
def download_audio(message):
	try:
		global url
		url = message.text
		bot.send_message(message.chat.id, 'Скачивание началось', parse_mode='html')

		downloading_audio(message)

		bot.send_message(message.chat.id, 'Скачивание завершено', parse_mode='html')

		bot.send_message(message.chat.id, 'Отправка', parse_mode='html')

		download_dir = (os.path.abspath(__file__)).split('/')
		download_dir.pop(-1)
		place_download = ''
		for i in download_dir:
			place_download += i + '/'

		for i in os.listdir(place_download):
			if fnmatch.fnmatch(i, '*.mp3'):
				audio = open(f'{i}', 'rb')
				bot.send_audio(message.chat.id, audio)

		add_message(message, message.text)
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Отправка аудио с YouTube] ' + str(e))

	try:
		for i in os.listdir(place_download):
			if fnmatch.fnmatch(i, '*.mp3'):
				os.remove(i)
	except:
		pass


# Получение текстовой версии видео с YouTube
'''def convert_video_youtube_to_text(message):
	global url
	url = message.text

	try:
		bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')

		downloading_audio(message)

		download_dir = (os.path.abspath(__file__)).split('/')
		download_dir.pop(-1)
		place_download = ''
		for i in download_dir:
			place_download += i + '/'

		for i in os.listdir(place_download):
			if fnmatch.fnmatch(i, '*.mp3'):
				global convert_name_file
				convert_name_file = i
				break

		convert = subprocess.run(['ffmpeg', '-i', convert_name_file, 'audio.wav', '-y'])

		r = sr.Recognizer()
		global result_convert
		result_convert = ''
		i = 0
		with sr.AudioFile('audio.wav') as source:
			while True:
				try:
					audio = r.listen(source)
					if len(result_convert + str(r.recognize_google(audio, language="ru_RU").lower())) < 4096:
						result_convert += str(r.recognize_google(audio, language="ru_RU").lower())
					else:
						bot.send_message(message.chat.id, result_convert, parse_mode='html')
						result_convert = ''
						result_convert += str(r.recognize_google(audio, language="ru_RU").lower())
				except sr.UnknownValueError:
					i += 1
					if i > 10:
						break

			bot.send_message(message.chat.id, result_convert, parse_mode='html')
			add_message(message, '[Конветрирование видео с YouTube в текст] ' + str(result_convert))

	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера или неудается распознать видео', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конветрирование видео с YouTube в текст] ' + str(e))

	try:
		os.remove('audio.wav')
		os.remove(convert_name_file)
	except:
		pass'''


# Сокращение ссылки
def small_link(message):
	try:
		link = message.text
		s = pyshorteners.Shortener()
		bot.send_message(message.chat.id, s.tinyurl.short(link))
		add_message(message, message.text)
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Сокращение ссылки] ' + str(e))


# Перевод систем счисления
def number_system(message):
	search = message.text
	try:
		number = search.split(' ')
		b = ''
		while int(number[0]) > 0:
			if (int(number[0]) % int(number[1])) > 9:
				if (int(number[0]) % int(number[1])) == 10:
					b += 'A'
				elif (int(number[0]) % int(number[1])) == 11:
					b += 'B'
				elif (int(number[0]) % int(number[1])) == 12:
					b += 'C'
				elif (int(number[0]) % int(number[1])) == 13:
					b += 'D'
				elif (int(number[0]) % int(number[1])) == 14:
					b += 'E'
				elif (int(number[0]) % int(number[1])) == 15:
					b += 'F'
			else:
				b += str(int(number[0]) % int(number[1]))
			
			number[0] = int(number[0]) // int(number[1])
		bot.send_message(message.chat.id, b[::-1], parse_mode='html')
		add_message(message, message.text)
	except ValueError:
		bot.send_message(message.chat.id, 'Вы ввели буквы вместо чисел', parse_mode='html')
	except IndexError:
		bot.send_message(message.chat.id, 'Вы ввели не все числа', parse_mode='html')
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Системы счисления] ' + str(e))


# Рандомное число
def number_random(message):
	search = message.text
	try:
		number = search.split(' ')
		if int(number[0]) > int(number[1]):
			answer = randint(int(number[1]), int(number[0]))
		else:
			answer = randint(int(number[0]), int(number[1]))

		bot.send_message(message.chat.id, answer, parse_mode='html')
		add_message(message, message.text)
	except ValueError:
		bot.send_message(message.chat.id, 'Вы ввели буквы вместо чисел', parse_mode='html')
	except IndexError:
		bot.send_message(message.chat.id, 'Вы ввели не все числа', parse_mode='html')
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Рандомное число] ' + str(e))


# Выбор что лучше
def what_the_best(message):
	try:
		search = message.text.lower().split(' ')
		if len(search) == 3:
			test = randint(1, 2)
			if test == int('1'):
				bot.send_message(message.chat.id, search[0], parse_mode='html')
			elif test == int('2'):
				bot.send_message(message.chat.id, search[2], parse_mode='html')
		elif len(search) == 2:
			test = randint(1, 2)
			if test == int('1'):
				bot.send_message(message.chat.id, search[0], parse_mode='html')
			elif test == int('2'):
				bot.send_message(message.chat.id, search[1], parse_mode='html')
		else:
			bot.send_message(message.chat.id, 'Вы допустили ошибку в заполнении', parse_mode='html')
		add_message(message, message.text)
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Что лучше] ' + str(e))


# Конвертация голосового сообщения в текст
def convert_voice_text(message):
	try:
		file_info = bot.get_file(message.voice.file_id)
		downloaded_file = bot.download_file(file_info.file_path)

		with open("audio.ogg", 'wb') as f:
		    f.write(downloaded_file)

		convert = subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])

		r = sr.Recognizer()
		with sr.AudioFile('audio.wav') as source:
			audio = r.listen(source)
			text = r.recognize_google(audio, language="ru_RU").lower()
			bot.send_message(message.chat.id, text)
			add_message(
				message, '[Голосовое] ' + str(text))
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера или ваше голосовое сообщение пустое', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование аудио в текст] ' + str(e))

	try:
		os.remove('audio.ogg')
		os.remove('audio.wav')
	except:
		pass


def convert_text_voice(message):
	mytext = message.text
	try:
		bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')
		convert_text = gTTS(text=mytext, lang='ru', slow=False)
		convert_text.save("audio.mp3")

		audio = open("audio.mp3", 'rb')
		bot.send_audio(message.chat.id, audio)
		audio.close()
		add_message(message, '[Конвертация текста] ' + str(mytext))
	except Exception as e:
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Конвертирование текста в аудио] ' + str(e))

	try:
		os.remove('audio.mp3')
	except:
		pass


# Отправка отзыва пользователем
def answer_user(message):
	# https://accounts.google.com/DisplayUnlockCaptcha
	try:
		msg = MIMEMultipart()
		msg['Subject'] = 'Отзыв'
		body = message.text
		msg.attach(MIMEText(body, 'plain'))
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(user_email, user_password)
		server.sendmail(user_email, user_email, msg.as_string())
		server.quit()
		bot.send_message(message.chat.id, 'Сообщение отправленно, спасибо большое за отзыв!', parse_mode='html')
		logger.info('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Отправка отзыва]')
		add_message(message, '[Отзыв] ' + str(message.text))
	except Exception as e:
		print(e)
		bot.send_message(message.chat.id, 'Ошибка на стороне сервера ', parse_mode='html')
		logger.error('[' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + ' ' + str(message.from_user.id) + '] [Отправка отзыва] ' + str(e))


# Конвертация аудио
def convert_audio(message, convert_name_file):
	convert = subprocess.run(['ffmpeg', '-i', convert_name_file, 'audio.wav', '-y'])

	r = sr.Recognizer()
	global result_convert
	result_convert = ''
	i = 0
	with sr.AudioFile('audio.wav') as source:
		while True:
			try:
				audio = r.listen(source)
				if len(result_convert + str(r.recognize_google(audio, language="ru_RU").lower())) < 4096:
					result_convert += str(r.recognize_google(audio, language="ru_RU").lower())
				else:
					bot.send_message(message.chat.id, result_convert, parse_mode='html')
					result_convert = ''
					result_convert += str(r.recognize_google(audio, language="ru_RU").lower())
			except sr.UnknownValueError:
				i += 1
				if i > 10:
					break

		bot.send_message(message.chat.id, result_convert, parse_mode='html')
		add_message(message, '[Конвертация аудио файла] ' + str(result_convert))


# Конвертирование фотографии
def converting_photo(message, convert_name_file):
	img = Image.open(convert_name_file) 
	global result_convert_photo
	result_convert_photo = pytesseract.image_to_string(img, lang='rus')


# Проверка id user
def verify_id(message):
	block_id = []
	if message.from_user.id in block_id:
		return 'Для вас доступ ограничен'
	else:
		return 1


# Отправка сообщения пользователям по id
def send_message_user(message, text_message):
	user_id = []
	for i in user_id:
		bot.send_message(i, text_message, parse_mode='html')



if __name__ == '__main__':
	bot.polling(none_stop=True)
