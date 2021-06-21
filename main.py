import logging
import telebot
from config import *
from function import *
from database import *

bot = telebot.TeleBot(token)

logging.basicConfig(filename="info/info.log", format = u'[%(levelname)s][%(asctime)s] (%(funcName)s:%(lineno)s): %(message)s', level='INFO')
logger = logging.getLogger()


# Команда для вывода списка всех команд бота
@bot.message_handler(commands = ['help'])
def help(message):
	access_id = verify_id(message.from_user.id)
	if access_id == 1:
		send_mess = '<b>Вот полный список запросов:</b>\n\nНовости\nНовости и слова по которым искать\nПогода\nСтатистика по коронавирусу\nКурс валюты\nЧто ты умеешь\nСкачать аудио (и позже скинуть ссылку на видео из YouTube)\nДа или нет\nОдин или два\nЧто лучше\nЧто лучше (и дописать сразу 2 действия через или)\nРандомное число\nРандомное число от ... до ...\nСократить ссылку (и позже скинуть ссылку)\nСистема счисление\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nОтправьте голосовое сообщение, и я распознаю вашу просьбу\nКонвертировать голосовое сообщение и позже отправьте или перешлите голосовое сообщение\nПросто скиньте фотографию или аудио файл и я конвертирую их в текст\nКонвертировать видео и позже скиньте его\nКонвертировать текст и позже напишите сам текст\nНаписать отзыв (и позже написать текст)\n/settings_news для настройки вывода новостей'
		bot.send_message(message.chat.id, send_mess, parse_mode='html')
	else:
		bot.send_message(message.chat.id, access_id, parse_mode='html')
	#add_message(message, message.text)


# Команда для старта бота
@bot.message_handler(commands = ['start'])
def start(message):
	access_id = verify_id(message.from_user.id)
	if access_id == 1:
		global markup
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		item1 = types.KeyboardButton('Новости')
		item2 = types.KeyboardButton('Курс валюты')
		item3 = types.KeyboardButton('Погода')
		item4 = types.KeyboardButton('Что ты умеешь?')
		item5 = types.KeyboardButton('Статистика по коронавирусу')
		markup.add(item1, item2, item3, item4, item5)
		send_mess = f"<b>Привет {message.from_user.first_name}!</b>\nЯ твой ассистент, можешь меня спрашивать и я постараюсь ответить!\nВы можете спросить у меня: \nПогоду\nКурс валюты\nПоследние новости\nНовости по ключевым словам\nСтатистика по коронавирусу\nРадномное число\nСокращение ссылки\nПеревести числа в нужную систему счисления\n\n<b>НОВИНКА!!!</b>\nГолосовой поиск (просто отправьте голосовое сообщение)\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nСкачать аудио из видео на YouTube, скинув на него ссылку\nКонвертация голосового сообщения в текст\nКонвертация аудио файла в текст\nКонвертация фотографии в текст\nКонвертация видео в текст\nКонвертация текста в аудио\nВозможность отправить разработчику анонимный отзыв\n/settings_news для настройки вывода новостей\n\nДля полного списка команд введите /help"
		bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup = markup)
	else:
		bot.send_message(message.chat.id, access_id, parse_mode='html')

	#create_table()
	add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Письменный поиск
@bot.message_handler(content_types=["text"])
def message_text(message):
	access_id = verify_id(message.from_user.id)
	if access_id == 1:
		result_message(message.text.lower(), message.from_user.id, message.from_user.first_name, message.from_user.last_name)
	else:
		bot.send_message(message.chat.id, access_id, parse_mode='html')

	add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


if __name__ == '__main__':
	bot.polling(none_stop=True)
