import pymysql.cursors
from config import *

db = pymysql.connect(host=host,
					port = 3306,
					user=user,
					password=password,
					db=db_name,
					cursorclass=pymysql.cursors.DictCursor)
sql = db.cursor()
sql.execute('USE telegram_bot_data')

# Создание таблиц если их нет
def create_table():
	try:
		sql.execute("SHOW TABLES;")
		count_tables = sql.fetchall()

		if len(count_tables) == 0:
			sql.execute("""CREATE TABLE IF NOT EXISTS `users` (
				user_id INTEGER NOT NULL,
				name VARCHAR(50) NOT NULL,
				last_name VARCHAR(100),
				time_message DATETIME DEFAULT CURRENT_TIMESTAMP,
				status BOOLEAN,
				settings_news BOOLEAN);""")
			db.commit()

			sql.execute("""CREATE TABLE IF NOT EXISTS `message` (
				user_id INTEGER NOT NULL,
				name VARCHAR(50) NOT NULL,
				last_name VARCHAR(100),
				text_message TEXT NOT NULL,
				time_message DATETIME DEFAULT CURRENT_TIMESTAMP);""")
			db.commit()

			logger.info("Создание таблиц в БД")
	except Exception as error:
		logger.error(f'[create_table] {error}')


# Добавление нового пользователя в БД
def add_new_user(id, first_name, last_name):
	try:
		check_count_id = 0
		sql.execute("SELECT user_id FROM users;")

		for i in sql.fetchall():
			if id == i['user_id']:
				check_count_id += 1

		if check_count_id == 0:
			sql.execute("INSERT INTO users (user_id, name, last_name, status, settings_news) VALUES (%s, %s, %s, %s, %s)", (id, str(first_name), str(last_name), 0, 0))
			db.commit()

			logger.info(f'[{first_name} {last_name} {id}] Создан новый пользователь')
	except pymysql.err.ProgrammingError:
		create_table()
		add_new_user(id, first_name, last_name)
	except Exception as error:
		logger.error(f'[{first_name} {last_name} {id}] [add_new_user] {error}')


# Добавление сообщения в БД
def add_message(text_message, id, first_name, last_name):
	try:
		sql.execute("INSERT INTO message (user_id, name, last_name, text_message) VALUES (%s, %s, %s, %s)", (id, str(first_name), str(last_name), str(text_message)))
		db.commit()
		add_new_user(id, first_name, last_name)
	except pymysql.err.ProgrammingError:
		create_table()
		add_new_user(id, first_name, last_name)
		add_message(text_message, id, first_name, last_name)
	except Exception as error:
		logger.error(f'[{first_name} {last_name} {id}] [add_message] {error}')


# Получение статуса вывода новостей
def get_settings_news(id, first_name, last_name):
    try:
        sql.execute(f"SELECT settings_news FROM users WHERE user_id = {id};")
        return sql.fetchone()
    except Exception as error:
        logger.error(f'[{first_name} {last_name} {id}] [get_settings_news] {error}')
