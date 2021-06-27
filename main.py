from threading import Thread
from requests_in_the_bot import *
from database import *
import time


mailing = Thread(target=mailing_subscribe_users)
mailing.start()

# Команда для старта бота
@bot.message_handler(commands = ['start'])
def start(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton('Новости')
	item2 = types.KeyboardButton('Курс валюты')
	item3 = types.KeyboardButton('Погода')
	item4 = types.KeyboardButton('Что ты умеешь?')
	item5 = types.KeyboardButton('Статистика по коронавирусу')
	markup.add(item1, item2, item3, item4, item5)
	send_mess = f"<b>Привет {message.from_user.first_name}!</b>\nЯ твой ассистент, можешь меня спрашивать и я постараюсь ответить!\nВы можете спросить у меня: \nПогоду\nКурс валюты\nПоследние новости\nНовости по ключевым словам\nСтатистика по коронавирусу\nРадномное число\nСокращение ссылки\nПеревести числа в нужную систему счисления\n\n<b>НОВИНКА!!!</b>\nГолосовой поиск (просто отправьте голосовое сообщение)\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nСкачать аудио из видео на YouTube, скинув на него ссылку\nКонвертация голосового сообщения в текст\nКонвертация аудио файла в текст\nКонвертация фотографии в текст\nКонвертация видео в текст\nКонвертация текста в аудио\nВозможность отправить разработчику анонимный отзыв\n/settings_news для настройки вывода новостей\n\nДля полного списка команд введите /help"
	bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup = markup)

	create_table()
	add_new_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для вывода списка всех команд бота
@bot.message_handler(commands = ['help'])
def help(message):
	send_mess = '<b>Вот полный список запросов:</b>\n\nНовости\nНовости и слова по которым искать\nПогода\nСтатистика по коронавирусу\nКурс валюты\nЧто ты умеешь\nСкачать аудио (и позже скинуть ссылку на видео из YouTube)\nДа или нет\nОдин или два\nЧто лучше\nЧто лучше (и дописать сразу 2 действия через или)\nРандомное число\nРандомное число от ... до ...\nСократить ссылку (и позже скинуть ссылку)\nСистема счисление\nВозможность пописаться на рассылку основной информации дважды в день, для подписки введите /subscribe, для отписки введите /unsubscribe\nОтправьте голосовое сообщение, и я распознаю вашу просьбу\nКонвертировать голосовое сообщение и позже отправьте или перешлите голосовое сообщение\nПросто скиньте фотографию или аудио файл и я конвертирую их в текст\nКонвертировать видео и позже скиньте его\nКонвертировать текст и позже напишите сам текст\nНаписать отзыв (и позже написать текст)\n/settings_news для настройки вывода новостей'
	bot.send_message(message.chat.id, send_mess, parse_mode='html')

	add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Отправка на почту log по команде
@bot.message_handler(commands = ['information'])
def send_information_users(message):
	if message.from_user.id == user_id:
		send_information_to_email()
	else:
		bot.send_message(message.chat.id, 'Для вас доступ ограничен', parse_mode='html')


# Команда для настройки новостей
@bot.message_handler(commands = ['settings_news'])
def settings_news(message):
	markup_inline = types.InlineKeyboardMarkup()
	item_1 = types.InlineKeyboardButton(text = 'Обычный режим', callback_data = 'simple_mode')
	item_2 = types.InlineKeyboardButton(text = 'Подробный режим', callback_data = 'detailed_mode')

	markup_inline.add(item_1, item_2)
	bot.send_message(message.chat.id, 'Выберете режим', reply_markup=markup_inline)

	add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для пописки на рассылку
@bot.message_handler(commands = ['subscribe'])
def subscribe(message):
	subscribe_to_the_mailing(message.from_user.id, message.from_user.first_name, message.from_user.last_name)

	add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Команда для отписки от рассылки
@bot.message_handler(commands = ['unsubscribe'])
def unsubscribe(message):
	unsubscribe_from_the_mailing(message.from_user.id, message.from_user.first_name, message.from_user.last_name)

	add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Письменный поиск
@bot.message_handler(content_types=["text"])
def message_text(message):
	start = time.time()
	result_message(message.text.lower(), message)
	print(time.time() - start)

	add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Голосовой поиск
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
	search = convert_voice_to_text(message, message.from_user.id, message.from_user.first_name, message.from_user.last_name, 'voice_search')

	result_message(search, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message)

	add_message(f'[Голосовой поиск] {search}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Конвертация аудио в текст
@bot.message_handler(content_types=['audio'])
def convert_audio_file(message):
	convert_audio_to_text(message, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Конвертация фотографии в текст
@bot.message_handler(content_types=["photo"])
def convet_photo(message):
	result_text = convert_photo_to_text(message, message.from_user.id, message.from_user.first_name, message.from_user.last_name)

	bot.send_message(message.chat.id, result_text, parse_mode='html')

	add_message(f'[Конвертация фотографии] {result_text}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Конвертация видео в текст
@bot.message_handler(content_types=['video'])
def convert_video(message):
	convert_video_to_text(message, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


# Конвертация документа в текст
@bot.message_handler(content_types=['document'])
def convert_document(message):
	convert_video_to_text(message, message.from_user.id, message.from_user.first_name, message.from_user.last_name)


if __name__ == '__main__':
	bot.polling(none_stop=True)
