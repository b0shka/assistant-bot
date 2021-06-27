import time
import os
import sqlite3
import smtplib
import requests
from bs4 import BeautifulSoup as BS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config import logger

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
				time_message DATETIME DEFAULT CURRENT_TIMESTAMP,
				status BOOLEAN,
				settings_news BOOLEAN);""")
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
	def add_new_user(self, id, first_name, last_name):
		try:
			check_count_id = 0
			self.sql.execute("SELECT user_id FROM users;")

			for i in self.sql.fetchall():
				if id == i[0]:
					check_count_id += 1

			if check_count_id == 0:
				self.sql.execute("INSERT INTO users (user_id, name, last_name, status, settings_news) VALUES (?, ?, ?, ?, ?)", (id, first_name, last_name, 0, 0))
				self.db.commit()

				logger.info(f'[{first_name} {last_name} {id}] Создан новый пользователь')
		except sqlite3.OperationalError:
			self.create_table()
			self.add_new_user(id, first_name, last_name)
		except Exception as error:
			logger.error(f'[{first_name} {last_name} {id}] [add_new_user] {error}')


	# Добавление сообщения в БД
	def add_message(self, text_message, id, first_name, last_name):
		try:
			self.sql.execute("INSERT INTO message (user_id, name, last_name, text_message) VALUES (?, ?, ?, ?)", (id, first_name, last_name, text_message))
			self.db.commit()
			self.add_new_user(id, first_name, last_name)
		except sqlite3.OperationalError:
			self.create_table()
			self.add_message(text_message, id, first_name, last_name)
		except Exception as error:
			logger.error(f'[{first_name} {last_name} {id}] [add_message] {error}')


	# Получение статуса вывода новостей
	def get_settings_news(self, id, first_name, last_name):
	    try:
	        self.sql.execute(f"SELECT settings_news FROM users WHERE user_id = {id};")
	        return self.sql.fetchone()
	    except Exception as error:
	        logger.error(f'[{first_name} {last_name} {id}] [get_settings_news] {error}')


	# Подписка на рассылку
	def subscribe_to_the_mailing(self, id, first_name, last_name):
		try:
			self.sql.execute(f"SELECT status FROM users WHERE user_id={id};")
			status_mailing = self.sql.fetchone()

			if status_mailing['status'] == 1:
				bot.send_message(id, 'Вы уже подписаны', parse_mode='html')
			else:
				self.sql.execute(f"UPDATE users SET status=1 WHERE user_id={id}")#
				db.commit()
				bot.send_message(id, 'Вы успешно подписаны', parse_mode='html')
		except sqlite3.OperationalError:
			create_table()
			add_new_user(id, first_name, last_name)
			subscribe(id, first_name, last_name)
		except Exception as error:
			bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
			logger.error(f'[{first_name} {last_name} {id}] [Подписка на рассылку] {error}')



	# Отписка от рассылки
	def unsubscribe_from_the_mailing(self, id, first_name, last_name):
		try:
			self.sql.execute(f"SELECT status FROM users WHERE user_id={id};")
			status_mailing = self.sql.fetchone()

			if status_mailing['status'] == 0:
				bot.send_message(id, 'Вы и не подписаны', parse_mode='html')
			else:
				self.sql.execute(f"UPDATE users SET status=0 WHERE user_id={id}")#
				db.commit()
				bot.send_message(id, 'Вы успешно отписаны', parse_mode='html')
		except sqlite3.OperationalError:
			create_table()
			add_new_user(id, first_name, last_name)
			subscribe(id, first_name, last_name)
		except Exception as error:
			bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
			logger.error(f'[{first_name} {last_name} {id}] [Подписка на рассылку] {error}')


	# Отправка рассылки по времени
	def mailing_subscribe_users(self):
		try:
			while True:
				if str(time.strftime("%H:%M:%S")) == str("12:49:10"):
					self.sql.execute(f"SELECT user_id FROM users WHERE status=1;")
					subscribe_users_list = self.sql.fetchall()

					for i in subscribe_users_list:
						print('hello')
					send_information_to_email()
		except Exception as error:
			logger.error(f'[mailing_subscribe_users] {error}')


	# Отправка информации на почту
	def send_information_to_email(self):
	    try:
	        msg = MIMEMultipart()
	        msg['Subject'] = 'Данные'
	        body = 'Отправка log'
	        msg.attach(MIMEText(body, 'plain'))

	        try:
	            part = MIMEApplication(open('info/info.log', 'rb').read())
	            part.add_header('Content-Disposition', 'attachment', filename = 'info.log')
	            msg.attach(part)
	        except:
	            pass

	        server = smtplib.SMTP('smtp.gmail.com', 587)
	        server.starttls()
	        server.login(user_email, user_password)
	        server.sendmail(user_email, user_email, msg.as_string())
	        server.quit()

	        with open("info/info.log", "w") as file_log:
	            file_log.close()

	        bot.send_message(id, 'Отправка завершена', parse_mode='html')
	    except Exception as error:
	        logger.error(f'[send_email] {error}')
