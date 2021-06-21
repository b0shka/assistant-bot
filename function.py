import requests
from telebot import types
from bs4 import BeautifulSoup as BS
from database import logger, get_settings_news
from main import bot


# Проверка id на блокировку
def verify_id(check_id):
    block_id = []
    if check_id in block_id:
        return 'Для вас доступ ограничен'
    else:
        return 1

# Получение результата поиска
def result_message(search, id, first_name, last_name):
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
            parse_news_words(id, first_name, last_name, text_news)
        else:
            parse_news(id, first_name, last_name)

    elif 'статистика' in search or 'коронавирус' in search or 'covid' in search:
            parse_stat_covid(id, first_name, last_name)

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
        bot.send_message(id, 'Вот что я умею\nДля полного списка команд введите /help', reply_markup = markup_inline)


# Парсинг погоды
def parse_weather(id, first_name, last_name):
    try:
        r = requests.get('https://yandex.ru/pogoda/perm')
        html = BS(r.content, 'html.parser')

        for el in html.select('.fact__temp'):
            weather = el.select('.temp__value')[0].text
            bot.send_message(id, f'В Перми сейчас {weather} градусов по Цельсию', parse_mode='html')
            break
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Парсинг погоды] {error}')


# Парсинг курса валюты
def parse_rate(id, first_name, last_name):
    try:
        r = requests.get('https://www.sberometer.ru/cbr/')
        html = BS(r.content, 'html.parser')

        for el in html.select('.zebra-2'):
            dollar = el.select('.b')
            bot.send_message(id, f'Курс доллара {dollar[0].text}', parse_mode='html')
            bot.send_message(id, f'Курс евро {dollar[1].text}', parse_mode='html')
            break

        r = requests.get('https://www.calc.ru/Bitcoin-k-rublyu-online.html')
        html = BS(r.content, 'html.parser')

        for el in html.select('.t18'):
            btc = el.select('b')[1].text.replace(' ', '.', 2)
            bot.send_message(id, f'Курс биткоина {btc}', parse_mode='html')
            break
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Парсинг курса валюты] {error}')


# Парсинг новостей
def parse_news(id, first_name, last_name):
    try:
        status_news = get_settings_news(id, first_name, last_name)
        r = requests.get('https://yandex.ru/news/')
        html = BS(r.content, 'html.parser')
        count_news = 0
        while count_news != 15:
            for el in html.select('.mg-card'):
                if count_news == 15:
                    break
                news = el.select('.mg-card__title')[0].text
                if status_news == 1:
                    link = el.select('.mg-card__link')[0]['href']
                    bot.send_message(id, f"{news} ({link_text})", parse_mode='html')
                else:
                    bot.send_message(id, news, parse_mode='html')
                count_news += 1
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Парсинг новостей] {error}')


# Парсинг новостей по ключевым словам
def parse_news_words(id, first_name, last_name, text_news):
    try:
        status_news = get_settings_news(id, first_name, last_name)
        r = requests.get(f'https://newssearch.yandex.ru/news/search?from=tabbar&text={text_news}')
        html = BS(r.content, 'html.parser')
        count_news = 0
        while count_news != 15:
            try:
                for el in html.select('.news-search-story'):
                    if count_news == 15:
                        break
                    news = el.select('.news-search-story__title')[0].text
                    if status_news == 1:
                        link = el.select('.news-search-story__title-link')[0]['href']
                        bot.send_message(id, f"{news} ({link_text})", parse_mode='html')
                    else:
                        bot.send_message(id, news, parse_mode='html')
                    count_news += 1
            except IndexError:
                break

        if count_news == 0:
            bot.send_message(id, 'Ничего не найдено', parse_mode='html')
    except Exception as error:
        if count_news == 0:
            bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
            logger.error(f'[{first_name} {last_name} {id}] [Парсинг новостей по ключевым словам] {error}')


# Парсинг статистики по коронавирусу
def parse_stat_covid(id, first_name, last_name):
    try:
        # Статистика в Перми
        r = requests.get('https://permkrai.ru/antivirus/')
        html = BS(r.content, 'html.parser')
        data = []

        for el in html.select('.col-sm-3'):
            data.append(el.select('.snafu__value')[0].text)

        infected = data[0].split()[1]
        #died = data[5].split()[1]

        bot.send_message(id, f'Статистика в Перми:\nЗараженных сегодня - {infected}', parse_mode='html')

        # Статистика в России
        r = requests.get('https://coronavirusnik.ru/')
        html = BS(r.content, 'html.parser')

        for el in html.select('.cases'):
            russia_stat_infected = el.select('.plus')[0].text.replace('(', '').replace(')', '')
            break
        for el in html.select('.deaths'):
            russia_stat_died = el.select('.plus')[0].text.replace('(', '').replace(')', '')
            break

        bot.send_message(id, f'Статистика в России:\nЗараженных сегодня - {russia_stat_infected}\nУмерло сегодня - {russia_stat_died}', parse_mode='html')

        # Статистика по миру
        r = requests.get('https://coronavirus-monitor.info/')
        html = BS(r.content, 'html.parser')
        world_stat = []
        x = 0

        for el in html.select('.info_blk'):
            world_stat.append(el.select('sup')[0].text.replace(' ', ''))
            x += 1
            if x == 3:
                break

        bot.send_message(id, f'Статистика по миру:\nЗараженных сегодня - {world_stat[0]}\nУмерло сегодня - {world_stat[2]}', parse_mode='html')
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Парсинг статистики по коронавирусу] {error}')
