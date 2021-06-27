from function import *
from database import get_settings_news, add_message, send_information_to_email
from config import bot, logger, user_email, user_password

id = None
first_name = None
last_name = None


# Получение результата поиска
def result_message(search, message):
    global id, first_name, last_name
    id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    if 'погода' in search or 'weather' in search:
        parse_weather(id, first_name, last_name)

    elif 'курс' in search or 'валют' in search or 'доллар' in search or 'долар' in search or 'евро' in search or 'rate' in search:
        parse_rate(id, first_name, last_name)

    elif 'новости' in search or'news' in search:
        text_news = search.split(' ')
        if 'новости' in search:
            text_news = text_news[text_news.index('новости')+1:]
        else:
            text_news = text_news[text_news.index('news')+1:]

        if len(text_news) > 0:
            text_news = ' '.join(text_news)
            parse_news_words(message, id, first_name, last_name, text_news)
        else:
            parse_news(id, first_name, last_name)

    elif 'статистика' in search or 'коронавирус' in search or 'covid' in search:
        parse_stat_covid(id, first_name, last_name)

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
        item_13 = types.InlineKeyboardButton(text = 'Голосовое сообщение в текст', callback_data = 'convert_audio_to_text')
        item_14 = types.InlineKeyboardButton(text = 'Фото/аудио/видео файл в текст', callback_data = 'convert_audio_photo_video_to_text')
        item_15 = types.InlineKeyboardButton(text = 'Отправить разработчику анонимный отзыв', callback_data = 'answer_user')

        markup_inline.add(item_1, item_2, item_3)
        markup_inline.add(item_4, item_5)
        markup_inline.add(item_6, item_7)
        markup_inline.add(item_8, item_9, item_10)
        markup_inline.add(item_11, item_12)
        markup_inline.add(item_13)
        markup_inline.add(item_14)
        markup_inline.add(item_15)
        bot.send_message(id, 'Вот что я умею\nДля полного списка команд введите /help', reply_markup=markup_inline)

    elif 'скачать аудио' in search or 'скачать музыку' in search or 'музык' in search:
        send = bot.send_message(id, 'Введите url')
        bot.register_next_step_handler(send, download_audio, id, first_name, last_name)

    elif 'youtube.com' in search or 'youtu.be' in search:
        download_audio(message, id, first_name, last_name)

    elif 'конвертировать' in search:
        if 'голосово' in search:
            send = bot.send_message(id, 'Отправьте или перешлите голосовое сообщение')
            bot.register_next_step_handler(send, convert_voice_to_text, id, first_name, last_name, 'convert_voice')

        elif 'в аудио' in search or ('текст' in search and 'аудио в' not in search):
            send = bot.send_message(message.chat.id, 'Напишите что конвертировать')
            bot.register_next_step_handler(send, convert_text_to_voice, id, first_name, last_name)

        elif 'аудио' in search or 'фото' in search or 'видео' in search:
            bot.send_message(id, 'Отправьте мне аудио файл, фотографию или видео')

    elif 'отзыв' in search or 'написать разработчику' in search or 'пожелан' in search or 'списаться с разработчиком' in search:
        send = bot.send_message(id, 'Введите отзыв или пожелания')
        bot.register_next_step_handler(send, answer_user, id, first_name, last_name)

    elif 'да' in search or 'нет' in search:
        bot.send_message(id, random.choice(('Да', 'Нет')), parse_mode='html')

    elif 'или' in search and ('один' in search or 'два' in search or '1' in search or '2' in search):
        bot.send_message(id, random.randint(1, 2), parse_mode='html')

    elif 'лучше' in search:
        what_the_best(message, id, first_name, last_name)

    elif 'любое число' in search or 'число от' in search or 'цифра от' in search or 'рандом' in search:
        number_random(message, id, first_name, last_name)

    elif 'население' in search or 'сколько людей' in search:
        parse_population(id, first_name, last_name)

    elif 'счислен' in search or 'систем' in search:
        send = bot.send_message(id, 'Введите два числа через пробел, само число и систему счисления в которую перевести')
        bot.register_next_step_handler(send, number_system, id, first_name, last_name)

    else:
        choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
        bot.send_message(id, random.choice(choice_text), parse_mode='html')


# Обработка нажатой кнопки в что ты умеешь и их функции
@bot.callback_query_handler(func = lambda call: True)
def answer(call):
    if call.data == 'weather':
        parse_weather(id, first_name, last_name)

    elif call.data == 'valuta':
        parse_rate(id, first_name, last_name)

    elif call.data == 'news':
        parse_news(id, first_name, last_name)

    elif call.data == 'news_word':
        send = bot.send_message(id, 'Введите ключевые слова')
        bot.register_next_step_handler(send, parse_news_words, id, first_name, last_name)

    elif call.data == 'virus':
        parse_stat_covid(id, first_name, last_name)

    elif call.data == 'yes_or_not':
        bot.send_message(id, random.choice(('Да', 'Нет')), parse_mode='html')

    elif call.data == 'one_or_two':
        bot.send_message(id, random.randint(1, 2), parse_mode='html')

    elif call.data == 'random_number':
        send = bot.send_message(id, 'Введите диапазон чисел через пробел')
        bot.register_next_step_handler(send, number_random, id, first_name, last_name)

    elif call.data == 'what_best':
        send = bot.send_message(call.message.chat.id, 'Введите 2 действия через или')
        bot.register_next_step_handler(send, what_the_best, id, first_name, last_name)

    elif call.data == 'system_number':
        send = bot.send_message(call.message.chat.id, 'Введите 2 числа через пробел, само число и систему счисления в которую перевести')
        bot.register_next_step_handler(send, number_system, id, first_name, last_name)

    elif call.data == 'click_download_audio':
        send = bot.send_message(call.message.chat.id, 'Введите url')
        bot.register_next_step_handler(send, download_audio, id, first_name, last_name)

    elif call.data == 'convert_audio_to_text':
        send = bot.send_message(call.message.chat.id, 'Отправьте или перешлите голосовое сообщение')
        bot.register_next_step_handler(send, convert_voice_to_text, id, first_name, last_name, 'convert_voice')

    elif call.data == 'convert_text_to_audio':
        send = bot.send_message(call.message.chat.id, 'Напишите что конвертировать')
        bot.register_next_step_handler(send, convert_text_to_voice, id, first_name, last_name)

    elif call.data == 'answer_user':
        send = bot.send_message(call.message.chat.id, 'Введите отзыв или пожелания')
        bot.register_next_step_handler(send, answer_user, id, first_name, last_name)

    elif call.data == 'convert_audio_photo_video_to_text':
        bot.send_message(call.message.chat.id, 'Отправьте фото, аудио файл или видео')

    elif call.data == 'convert_video_youtube_to_text':
        send = bot.send_message(call.message.chat.id, 'Введите url')
        bot.register_next_step_handler(send, answer_user, id, first_name, last_name)

    add_message(call.data, id, first_name, last_name)
