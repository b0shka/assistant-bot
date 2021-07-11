import asyncio
from aiogram import executor, types
from requests_in_the_bot import Requests_bot
from database import Database
from functions import Functions
from config import dp, Form, user_id

db = Database('server.db')
req_bot = Requests_bot()
func = Functions()

# Команда для старта бота
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton('Новости')
	item2 = types.KeyboardButton('Курс валюты')
	item3 = types.KeyboardButton('Погода')
	item4 = types.KeyboardButton('Что ты умеешь?')
	item5 = types.KeyboardButton('Коронавирус')
	markup.add(item1, item2, item3, item4, item5)
	send_mess = f"Привет {message.from_user.first_name}!\nЯ твой персональный ассистент\nВы можете узнать у меня: погоду (укажите ваш город в настройках /settings), курс валюты, последние новости, новости по ключевым словам, статистику по коронавирусу\nТакже имеется возможность подписаться на рассылку основной информации (/subscribe, /unsubscribe)\nКроме того у меня есть множество полезных функций, таких как: \nСкачать аудио из видео на YouTube\nКонвертация голосового сообщения, аудио файла, фотографии и видео в текст\nРаспознать лица на фотографии\nЕсли есть какие-то вопросы или пожелания, имеется возможность отправить разработчику анонимный отзыв\n\nДля полного списка команд введите /help"
	await message.answer(send_mess, reply_markup = markup)

	db.create_table()
	db.add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для вывода списка всех команд бота
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
	send_mess = 'Вот полный список запросов:\n\nНовости\nНовости (и слова по которым искать)\nПогода\nСтатистика по коронавирусу\nКурс валюты\nЧто ты умеешь\nНаселение\nСкачать аудио (и позже скинуть ссылку на видео из YouTube)\nДа или нет\nОдин или два\nЧто лучше\nЧто лучше (и дописать сразу 2 действия через или)\nРандомное число\nРандомное число от ... до ...\nРандомное число от ...\nРандомное число до ...\nБросить кубик\nСистема счисление\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nОтправьте голосовое сообщение, и я распознаю вашу просьбу\nКонвертировать голосовое сообщение (и позже отправьте или перешлите голосовое сообщение)\nПросто скиньте фотографию или аудио файл и я конвертирую их в текст\nКонвертировать видео (и позже скиньте его)\nКонвертировать текст (и позже напишите сам текст)\nРаспознать лица\nНаписать отзыв (и позже написать текст)\n/settings (для настройки вывода новостей, и указания вашего города для вывода погоды)'
	await message.answer(send_mess)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Отправка на почту log по команде
@dp.message_handler(commands=['information'])
async def send_information_users(message: types.Message):
	if message.from_user.id == user_id:
		await func.send_information_to_email(message)
	else:
		choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
		await message.answer(random.choice(choice_text))


# Получение статистики по команде
@dp.message_handler(commands=['statistic'])
async def send_information_users(message: types.Message):
	if message.from_user.id == user_id:
		await db.get_statistic(message)
	else:
		choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
		await message.answer(random.choice(choice_text))


# Получение детальной статистики по команде
@dp.message_handler(commands=['statistic_detailed'])
async def send_information_users(message: types.Message):
	if message.from_user.id == user_id:
		markup_inline = types.InlineKeyboardMarkup()
		item_1 = types.InlineKeyboardButton(text = 'Список пользователей', callback_data = 'list_users')
		item_2 = types.InlineKeyboardButton(text = 'Список подписанных пользователей', callback_data = 'list_subscribe_users')
		item_3 = types.InlineKeyboardButton(text = 'Список самых частых сообщений', callback_data = 'list_messages')
		item_4 = types.InlineKeyboardButton(text = 'Скинуть базу данных', callback_data = 'send_db')

		markup_inline.add(item_1)
		markup_inline.add(item_2)
		markup_inline.add(item_3)
		markup_inline.add(item_4)
		await message.answer('Вот что доступно', reply_markup=markup_inline)
	else:
		choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
		await message.answer(random.choice(choice_text))


# Команда для настройки
@dp.message_handler(commands=['settings'])
async def settings_news(message: types.Message):
	markup_inline = types.InlineKeyboardMarkup()
	item_1 = types.InlineKeyboardButton(text = 'Выбрать город для вывода погоды', callback_data = 'choice_city')
	item_2 = types.InlineKeyboardButton(text = 'Вывод новостей', callback_data = 'mode_news')

	markup_inline.add(item_1)
	markup_inline.add(item_2)
	await message.answer('Выберите настройку чего вы хотите произвести', reply_markup=markup_inline)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для пописки на рассылку
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
	await db.subscribe_to_the_mailing(message)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для отписки от рассылки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
	await db.unsubscribe_from_the_mailing(message)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для срочной рассылки всем пользователям
@dp.message_handler(commands=['mailing'])
async def mailing(message: types.Message):
	if message.from_user.id == user_id:
		await message.answer('Введите что разослать')
		await Form.mailing.set()
	else:
		choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
		await message.answer(random.choice(choice_text))


@dp.message_handler(content_types=["text"], state=None)
async def answer_message(message: types.Message):
	await req_bot.result_message(message.text.lower(), message)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Голосовой поиск
@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
	search = await func.convert_voice_to_text(message, 'voice_search')
	await req_bot.result_message(search, message)


# Конвертация аудио в текст
@dp.message_handler(content_types=['audio'])
async def convert_audio_file(message: types.Message):
	await func.convert_audio_to_text(message)


# Конвертация фотографии в текст
@dp.message_handler(content_types=["photo"])
async def convet_photo(message: types.Message):
	await func.convert_photo_to_text(message)


# Конвертация видео в текст
@dp.message_handler(content_types=['video'])
async def convert_video(message: types.Message):
	await func.convert_video_to_text(message)


# Конвертация документа в текст
@dp.message_handler(content_types=['document'])
async def convert_document(message: types.Message):
	await func.convert_document_to_text(message)


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.create_task(func.mailing_subscribe_users(5))
	executor.start_polling(dp, skip_updates=True, loop=loop)
