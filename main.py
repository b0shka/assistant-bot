from threading import Thread
from aiogram import executor, types
from function import Function
from database import Database
from config import *

db = Database('server.db')
func = Function()

# Команда для старта бота
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton('Новости')
	item2 = types.KeyboardButton('Курс валюты')
	item3 = types.KeyboardButton('Погода')
	item4 = types.KeyboardButton('Что ты умеешь?')
	item5 = types.KeyboardButton('Статистика по коронавирусу')
	markup.add(item1, item2, item3, item4, item5)
	send_mess = f"Привет {message.from_user.first_name}!\nЯ твой ассистент, можешь меня спрашивать и я постараюсь ответить!\nВы можете спросить у меня: \nПогоду\nКурс валюты\nПоследние новости\nНовости по ключевым словам\nСтатистика по коронавирусу\nРадномное число\nСокращение ссылки\nПеревести числа в нужную систему счисления\nГолосовой поиск (просто отправьте голосовое сообщение)\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nСкачать аудио из видео на YouTube, скинув на него ссылку\nКонвертация голосового сообщения в текст\nКонвертация аудио файла в текст\nКонвертация фотографии в текст\nКонвертация видео в текст\nКонвертация текста в аудио\nВозможность отправить разработчику анонимный отзыв\n/settings_news для настройки вывода новостей\n\nДля полного списка команд введите /help"
	await message.answer(send_mess, reply_markup = markup)

	db.create_table()
	db.add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для вывода списка всех команд бота
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
	send_mess = 'Вот полный список запросов:\n\nНовости\nНовости и слова по которым искать\nПогода\nСтатистика по коронавирусу\nКурс валюты\nЧто ты умеешь\nСкачать аудио (и позже скинуть ссылку на видео из YouTube)\nДа или нет\nОдин или два\nЧто лучше\nЧто лучше (и дописать сразу 2 действия через или)\nРандомное число\nРандомное число от ... до ...\nСократить ссылку (и позже скинуть ссылку)\nСистема счисление\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nОтправьте голосовое сообщение, и я распознаю вашу просьбу\nКонвертировать голосовое сообщение и позже отправьте или перешлите голосовое сообщение\nПросто скиньте фотографию или аудио файл и я конвертирую их в текст\nКонвертировать видео и позже скиньте его\nКонвертировать текст и позже напишите сам текст\nНаписать отзыв (и позже написать текст)\n/settings_news для настройки вывода новостей'
	await message.answer(send_mess)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


@dp.message_handler(content_types=["text"])
async def echo(message: types.Message):
	await func.result_message(message.text.lower(), message)

	db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
