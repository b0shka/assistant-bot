from collections import Counter
from aiogram import types
from config import logger, user_id, bot
import sqlite3


class Database:
	def __init__(self, database_file):
		self.db = sqlite3.connect(f'info/{database_file}')
		self.sql = self.db.cursor()

	# Создание таблиц если их нет
	def create_table(self):
		try:
			self.sql.execute("""CREATE TABLE IF NOT EXISTS `users` (
								user_id INTEGER NOT NULL,
								name VARCHAR(50) NOT NULL,
								last_name VARCHAR(100),
								time DATETIME DEFAULT CURRENT_TIMESTAMP,
								status BOOLEAN,
								city VARCHAR(50),
								mode_news BOOLEAN,
								time_mailing VARCHAR(8));""")
			self.db.commit()

			self.sql.execute("""CREATE TABLE IF NOT EXISTS `message` (
								user_id INTEGER NOT NULL,
								name VARCHAR(50) NOT NULL,
								last_name VARCHAR(100),
								text_message TEXT NOT NULL,
								time_message DATETIME DEFAULT CURRENT_TIMESTAMP);""")
			self.db.commit()

			logger.info("Создание таблиц в БД")
		except Exception as error:
			logger.error(f'[create_table] {error}')

	# Добавление нового пользователя в БД
	async def add_new_user(self, id, first_name, last_name):
		try:
			self.sql.execute(f"SELECT COUNT(*) FROM users WHERE user_id={id};")
			
			if self.sql.fetchone()[0] == 0:
				self.sql.execute("""INSERT INTO users ( user_id, name, 
														last_name, 
														status, 
														mode_news, 
														city, 
														time_mailing) 
														VALUES (?, ?, ?, ?, ?, ?, ?)""", 
														(id, first_name, last_name, 0, 0, '', '10:00:00'))
				self.db.commit()

				logger.info(f'[{first_name} {last_name} {id}] Создан новый пользователь')

				if id != user_id:
					await bot.send_message(user_id, f'[{first_name} {last_name} {id}] Создан новый пользователь')
		except sqlite3.OperationalError:
			self.create_table()
			await self.add_new_user(id, first_name, last_name)
		except Exception as error:
			logger.error(f'[{first_name} {last_name} {id}] [add_new_user] {error}')


	# Добавление сообщения в БД
	async def add_message(self, text_message, id, first_name, last_name):
		try:
			self.sql.execute("""INSERT INTO message (user_id, 
													name, 
													last_name, 
													text_message) 
													VALUES (?, ?, ?, ?)""", 
													(id, first_name, last_name, text_message))
			self.db.commit()
			await self.add_new_user(id, first_name, last_name)
		except sqlite3.OperationalError:
			self.create_table()
			await self.add_message(text_message, id, first_name, last_name)
		except Exception as error:
			logger.error(f'[{first_name} {last_name} {id}] [add_message] {error}')


	# Получение статуса вывода новостей
	def get_settings_news(self, id, first_name, last_name):
	    try:
	        self.sql.execute(f"SELECT mode_news FROM users WHERE user_id={id};")
	        return self.sql.fetchone()
	    except Exception as error:
	        logger.error(f'[{first_name} {last_name} {id}] [get_settings_news] {error}')


	# Изменение настройки вывода новостей
	async def change_settings_news(self, message, mode):
		try:
			if mode == 'обычный режим':
				self.sql.execute(f"UPDATE users SET mode_news=0 WHERE user_id={message.from_user.id};")
			elif mode == 'подробный режим':
				self.sql.execute(f"UPDATE users SET mode_news=1 WHERE user_id={message.from_user.id};")

			self.db.commit()

			await self.open_main_menu(message, 'Режим изменен')
		except Exception as error:
			logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [change_settings_news] {error}')


	# Получение города
	def get_city(self, id, first_name=None, last_name=None):
		try:
			self.sql.execute(f"SELECT city FROM users WHERE user_id={id};")
			return self.sql.fetchone()
		except Exception as error:
			logger.error(f'[{first_name} {last_name} {id}] [get_city] {error}')


	# Изменение города
	async def change_city(self, message, city_user):
		try:
			self.get_city(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
			self.sql.execute(f"UPDATE users SET city='{city_user}' WHERE user_id={message.from_user.id};")
			self.db.commit()

			await self.open_main_menu(message, 'Город изменен')
		except Exception as error:
			logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [change_city] {error}')


	# Изменение времени рассылки в БД
	async def change_time(self, message, new_time):
		try:
			self.sql.execute(f'UPDATE users SET time_mailing="{new_time}" WHERE user_id={message.from_user.id};')
			self.db.commit()

			await message.answer('Изменения сохранены')
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [change_time] {error}')

	
	# Получение id подписанных пользователей и времени рассылки
	async def get_time_mailing_and_users(self):
		try:
			list_users_and_time = {}
			self.sql.execute('SELECT user_id, time_mailing FROM users WHERE status=1;')
			for i in self.sql.fetchall():
				list_users_and_time[i[0]] = i[1]

			return list_users_and_time
		except Exception as error:
			logger.error(f'[get_time_mailing_users] {error}')


	#Открытие главного меню
	async def open_main_menu(self, message, message_text):
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		item1 = types.KeyboardButton('Новости')
		item2 = types.KeyboardButton('Курс валюты')
		item3 = types.KeyboardButton('Погода')
		item4 = types.KeyboardButton('Что ты умеешь?')
		item5 = types.KeyboardButton('Коронавирус')
		markup.add(item1, item2, item3, item4, item5)
		await message.answer(message_text, reply_markup=markup)


	# Подписка на рассылку
	async def subscribe_to_the_mailing(self, message):
		try:
			self.sql.execute(f"SELECT status FROM users WHERE user_id={message.from_user.id};")
			status_mailing = self.sql.fetchone()

			if status_mailing[0] == 1:
				await message.answer('Вы уже подписаны')
			else:
				self.sql.execute(f"UPDATE users SET status=1 WHERE user_id={message.from_user.id}")#
				self.db.commit()
				await message.answer('Вы успешно подписаны')
		except sqlite3.OperationalError:
			self.create_table()
			await self.add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
			await self.subscribe_to_the_mailing(message)
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Подписка на рассылку] {error}')


	# Отписка от рассылки
	async def unsubscribe_from_the_mailing(self, message):
		try:
			self.sql.execute(f"SELECT status FROM users WHERE user_id={message.from_user.id};")
			status_mailing = self.sql.fetchone()

			if status_mailing[0] == 0:
				await message.answer('Вы и не подписаны')
			else:
				self.sql.execute(f"UPDATE users SET status=0 WHERE user_id={message.from_user.id}")
				self.db.commit()
				await message.answer('Вы успешно отписаны')
		except sqlite3.OperationalError:
			self.create_table()
			await self.add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
			await self.unsubscribe_from_the_mailing(message)
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Подписка на рассылку] {error}')


	# Удаление данных пользователя
	async def delete_data(self, message):
		try:
			self.sql.execute(f'DELETE FROM users WHERE user_id={message.from_user.id};')
			self.db.commit()

			self.sql.execute(f'DELETE FROM message WHERE user_id={message.from_user.id};')
			self.db.commit()

			await message.answer('Удаление завершено')
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [delete_data] {error}')


	# Получение id всех пользователей
	def get_all_users(self):
		try:
			self.sql.execute("SELECT user_id FROM users;")
			users_list = self.sql.fetchall()

			return users_list
		except Exception as error:
			logger.error(f'[get_all_users] {error}')


	# Получение статистики
	async def get_statistic(self, message):
		try:
			count_users = self.get_all_users()
			await message.answer(f'Всего пользователей - {len(count_users)}')

			self.sql.execute('SELECT user_id FROM users WHERE status=1;')
			count_subscribe_users = len(self.sql.fetchall())
			await message.answer(f'Количество подписанных на рассылку - {count_subscribe_users}')

			self.sql.execute('SELECT text_message FROM message;')
			all_messages = self.sql.fetchall()
			await message.answer(f'Всего сообщений - {len(all_messages)}')

			analyse_message = []
			for i in all_messages:
				analyse_message.append(i[0])

			analyse_message = Counter(analyse_message)
			await message.answer(f'Самое частое сообщение - {analyse_message.most_common(1)[0][0]} ({analyse_message.most_common(1)[0][1]})')
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[get_statistic] {error}')


	# Получение списка пользователей для статистики
	async def satistic_list_users(self, message):
		try:
			self.sql.execute('SELECT user_id, name, last_name FROM users;')
			list_users = self.sql.fetchall()
			await message.answer(f'Всего пользователей - {len(list_users)}')
			for i in list_users:
				await message.answer(f'{i[1]} {i[2]} {i[0]}')
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[satistic_list_users] {error}')


	# Получение списка подписанных пользователей для статистики
	async def statistic_list_subscribe_users(self, message):
		try:
			self.sql.execute(f"SELECT user_id, name, last_name FROM users WHERE status=1;")
			list_subscribe_users = self.sql.fetchall()
			await message.answer(f'Количество подписанных на рассылку - {len(list_subscribe_users)}')
			for i in list_subscribe_users:
				await message.answer(f'{i[1]} {i[2]} {i[0]}')
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[statistic_list_subscribe_users] {error}')


	# Получение списка частых сообщений для статистики
	async def statistic_list_message(self, message):
		try:
			self.sql.execute('SELECT text_message FROM message;')
			all_messages = self.sql.fetchall()
			await message.answer(f'Всего сообщений - {len(all_messages)}')

			analyse_message = []
			for i in all_messages:
				analyse_message.append(i[0])

			analyse_message = Counter(analyse_message).most_common(3)
			
			for i in analyse_message:
				await message.answer(f'{i[0]} - {i[1]}')
		except Exception as error:
			await message.answer('Ошибка на стороне сервера')
			logger.error(f'[statistic_list_message] {error}')