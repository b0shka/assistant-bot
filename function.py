import requests
import youtube_dl
import os
import fnmatch
import speech_recognition as sr
import subprocess
import re
import random
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup as BS
from gtts import gTTS
from database import get_settings_news, add_message, send_information_to_email
from config import bot, logger, user_email, user_password


# Проверка id на блокировку
def verify_id(check_id):
    block_id = []
    if check_id in block_id:
        return 'Для вас доступ ограничен'
    else:
        return 1

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
def parse_news_words(message, id, first_name, last_name, text_news=None):
    try:
        if text_news == None:
            text_news = message.text
            add_message(f'[Новости по ключевым словам] {text_news}', id, first_name, last_name)

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


# Скачивание аудио
def downloading_audio(id, first_name, last_name, url):
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
    except Exception as error:
        bot.send_message(message.chat.id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Скачивание аудио с YouTube] {error}')

# Скачивание и отправка аудио
def download_audio(message, id, first_name, last_name):
    try:
        url = message.text
        bot.send_message(id, 'Скачивание началось', parse_mode='html')

        downloading_audio(id, first_name, last_name, url)

        bot.send_message(id, 'Отправка', parse_mode='html')

        for i in os.listdir(os.getcwd()):
            if fnmatch.fnmatch(i, '*.mp3'):
                bot.send_audio(id, open(i, 'rb'), parse_mode='html')

        add_message(url, id, first_name, last_name)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Отправка аудио с YouTube] {error}')

    try:
        for i in os.listdir(os.getcwd()):
            if fnmatch.fnmatch(i, '*.mp3'):
                os.remove(i)
    except:
        pass


# Отправка отзыва пользователем
def answer_user(message, id, first_name, last_name):
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
        bot.send_message(id, 'Сообщение отправленно, спасибо большое за отзыв!', parse_mode='html')

        logger.info(f'[{first_name} {last_name} {id}] [Отправка отзыва]')
        add_message(f'[Отзыв] {message.text}', id, first_name, last_name)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера ', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Отправка отзыва] {error}')


# Рандомное число
def number_random(message, id, first_name, last_name):
    try:
        numbers = re.findall('(\d+)', message.text)

        if len(numbers) < 2:
            bot.send_message(id, 'Вы ввели не все числа', parse_mode='html')
        elif len(numbers) == 2:
            if int(numbers[1]) > int(numbers[0]):
                bot.send_message(id, random.randint(int(numbers[0]), int(numbers[1])), parse_mode='html')
            else:
                bot.send_message(id, random.randint(int(numbers[1]), int(numbers[0])), parse_mode='html')

            add_message(message.text, id, first_name, last_name)
        elif len(numbers) == 3:
            if int(numbers[1]) > int(numbers[0]):
                bot.send_message(id, random.randrange(int(numbers[0]), int(numbers[1]), int(numbers[2])), parse_mode='html')
            else:
                bot.send_message(id, random.randrange(int(numbers[1]), int(numbers[0]), int(numbers[2])), parse_mode='html')
        else:
            bot.send_message(id, 'Ошибка в записи', parse_mode='html')

        add_message(message.text, id, first_name, last_name)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Рандомное число] {error}')


# Парсинг населения мира
def parse_population(id, first_name, last_name):
    pass


# Перевод в систему счисления
def number_system(message, id, first_name, last_name):
    try:
        search = message.text.split(' ')
        if len(search) < 2:
            bot.send_message(id, 'Вы ввели не все числа', parse_mode='html')
        elif len(search) == 2:
            numbers_more_nine = {10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F'}
            number = ''

            if int(search[1]) > 16:
                bot.send_message(id, 'Вы ввели слишкон большую систему счисления (max=16)', parse_mode='html')
            else:
                while int(search[0]) > 0:
                    x = int(search[0]) % int(search[1])
                    if x > 9:
                        number += numbers_more_nine[x]
                    else:
                        number += str(x)

                    search[0] = int(search[0]) // int(search[1])

                bot.send_message(id, number[::-1], parse_mode='html')
        else:
            bot.send_message(id, 'Ошибка в записи', parse_mode='html')

        add_message(message.text, id, first_name, last_name)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Системы счисления] {error}')


# Выбор что лучше
def what_the_best(message, id, first_name, last_name):
    try:
        choice_text = message.text.split(' ')
        if 'лучше' in choice_text:
            choice_text = choice_text[choice_text.index('лучше')+1:]

        if 'или' in choice_text:
            choice_text = ''.join(choice_text).split('или')
            bot.send_message(id, random.choice(choice_text), parse_mode='html')
        else:
            bot.send_message(id, 'Ошибка в записи', parse_mode='html')

        add_message(message.text, id, first_name, last_name)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Что лучше] {error}')


# Конвертация голосового сообщения в текст
def convert_voice_to_text(message, id, first_name, last_name, mode):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("audio.ogg", 'wb') as f:
            f.write(downloaded_file)

        convert = subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])

        r = sr.Recognizer()
        with sr.AudioFile('audio.wav') as source:
            text_from_voice = r.recognize_google(r.listen(source), language="ru_RU").lower()

        add_message(f'[Голосовое] {text_from_voice}', id, first_name, last_name)

        try:
            os.remove('audio.ogg')
            os.remove('audio.wav')
        except:
            pass

        if mode == 'convert_voice':
            bot.send_message(id, text_from_voice, parse_mode='html')
        elif mode == 'voice_search':
            return text_from_voice
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера или ваше голосовое сообщение пустое', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Конвертирование аудио в текст] {error}')


# Конвертация текста в голосовое сообщение
def convert_text_to_voice(message, id, first_name, last_name):
    try:
        text_for_convert = message.text

        bot.send_message(id, 'Конвертация началась', parse_mode='html')
        convert_text = gTTS(text=text_for_convert, lang='ru', slow=False)
        convert_text.save("audio.mp3")

        with open("audio.mp3", 'rb') as audio:
            bot.send_audio(id, audio, parse_mode='html')

        add_message(f'[Конвертация текста] {text_for_convert}', id, first_name, last_name)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Конвертирование текста в аудио] {error}')

    try:
        os.remove('audio.mp3')
    except:
        pass


# Скачивание и конвертация фотографии в текст
def convert_photo_to_text(message, id, first_name, last_name):
    try:
        bot.send_message(id, 'Конвертация началась', parse_mode='html')

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        convert_name_file = 'img.jpg'
        with open(convert_name_file, 'wb') as f:
            f.write(downloaded_file)

        try:
            os.remove(convert_name_file)
        except:
            pass
        return converting_photo(convert_name_file)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера или фотографию неудается распознать', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Конвертирование фото в текст] {error}')


def converting_photo(convert_name_file):
    img = Image.open(convert_name_file)
    result_text = pytesseract.image_to_string(img, lang='rus')

    return result_text

# Конвертация аудио в текст
def convert_audio_to_text(message, id, first_name, last_name):
    try:
        bot.send_message(id, 'Конвертация началась', parse_mode='html')

        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        convert_name_file = 'audio.ogg'

        with open(convert_name_file, 'wb') as f:
            f.write(downloaded_file)

        converting_audio(convert_name_file)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера или файл неудается распознать', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Конвертирование аудио в текст] {error}')

    try:
        os.remove(convert_name_file)
        os.remove('audio.wav')
    except:
        pass

def converting_audio(convert_name_file):
    convert = subprocess.run(['ffmpeg', '-i', convert_name_file, 'audio.wav', '-y'])

    r = sr.Recognizer()
    result_convert = ''
    count_long_pause = 0
    with sr.AudioFile('audio.wav') as source:
        while True:
            try:
                audio = r.listen(source)
                if len(result_convert + str(r.recognize_google(audio, language="ru_RU").lower())) < 4096:
                    result_convert += str(r.recognize_google(audio, language="ru_RU").lower())
                else:
                    bot.send_message(id, result_convert, parse_mode='html')
                    result_convert = str(r.recognize_google(audio, language="ru_RU").lower())
            except sr.UnknownValueError:
                count_long_pause += 1
                if count_long_pause > 10:
                    break

        bot.send_message(id, result_convert, parse_mode='html')
        add_message(f'[Конвертация аудио файла] {result_convert}', id, first_name, last_name)


# Конвертация видео в текст
def convert_video_to_text(message, id, first_name, last_name):
    try:
        bot.send_message(message.chat.id, 'Конвертация началась', parse_mode='html')

        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("video.mp4", 'wb') as f:
            f.write(downloaded_file)

        audio = VideoFileClip('video.mp4').audio
        audio.write_audiofile('audio.mp3')
        convert_name_file = 'audio.mp3'

        converting_audio(convert_name_file)
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера или видео неудается распознать', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Конвертирование видео в текст] {error}')

    try:
        os.remove('video.mp4')
        os.remove(convert_name_file)
        os.remove('audio.wav')
    except:
        pass


# Конвертирование документа в текст
def convert_document_to_text(message, id, first_name, last_name):
    try:
        audio_name = ['ogg', 'opus', 'mp3', 'wav', 'aac']
        photo_name = ['jpeg', 'jpg', 'png']
        video_name = ['mp4', 'avi', 'mkv']

        bot.send_message(id, 'Конвертация началась', parse_mode='html')

        file_name = message.document.file_name.split('.')

        if file_name[-1] in photo_name:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            convert_name_file = 'img.' + str(file_name[-1])

            with open(convert_name_file, 'wb') as f:
                f.write(downloaded_file)

            result_convert_photo = converting_photo(convert_name_file)

            bot.send_message(id, result_convert_photo, parse_mode='html')
            add_message(f'[Конвертация фото в текст] {result_convert_photo}', id, first_name, last_name)

        elif file_name[-1] in audio_name:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            convert_name_file = 'audio.ogg'

            with open(convert_name_file, 'wb') as f:
                f.write(downloaded_file)

            converting_audio(convert_name_file)

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

            audio = VideoFileClip(convert_video_file).audio
            audio.write_audiofile('audio.mp3')
            convert_name_file = 'audio.mp3'

            converting_audio(convert_name_file)

        try:
            os.remove(convert_video_file)
            os.remove('audio.wav')
        except:
            pass
    except Exception as error:
        bot.send_message(id, 'Ошибка на стороне сервера или файл неудается распознать', parse_mode='html')
        logger.error(f'[{first_name} {last_name} {id}] [Конвертирование документа в текст] {error}')

    try:
        os.remove(convert_name_file)
    except:
        pass
