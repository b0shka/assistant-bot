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
from aiogram import types
from config import logger, bot, dp
from database import Database


class Function:
    def __init__(self):
        self.db = Database('server.db')

    # Получение результата поиска
    async def result_message(self, search, message):
        if 'погода' in search or 'weather' in search:
            await self.parse_weather(message)

        elif 'курс' in search or 'валют' in search or 'доллар' in search or 'долар' in search or 'евро' in search or 'rate' in search:
            await self.parse_rate(message)

        elif 'новости' in search or'news' in search:
            text_news = search.split(' ')
            if 'новости' in search:
                text_news = text_news[text_news.index('новости')+1:]
            else:
                text_news = text_news[text_news.index('news')+1:]

            if len(text_news) > 0:
                text_news = ' '.join(text_news)
                await self.parse_news_words(message, text_news)
            else:
                await self.parse_news(message)

        elif 'статистика' in search or 'коронавирус' in search or 'covid' in search:
            await self.parse_stat_covid(message)

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
            await message.answer('Вот что я умею\nДля полного списка команд введите /help', reply_markup=markup_inline)

        elif 'скачать аудио' in search or 'скачать музыку' in search or 'музык' in search:
            send = bot.send_message(id, 'Введите url')
            bot.register_next_step_handler(send, download_audio, id, first_name, last_name)

        elif 'youtube.com' in search or 'youtu.be' in search:
            await self.download_audio(message)

        elif 'конвертировать' in search:
            if 'голосово' in search:
                send = bot.send_message(id, 'Отправьте или перешлите голосовое сообщение')
                bot.register_next_step_handler(send, convert_voice_to_text, id, first_name, last_name, 'convert_voice')

            elif 'в аудио' in search or ('текст' in search and 'аудио в' not in search):
                send = bot.send_message(message.chat.id, 'Напишите что конвертировать')
                bot.register_next_step_handler(send, convert_text_to_voice, id, first_name, last_name)

            elif 'аудио' in search or 'фото' in search or 'видео' in search:
                await message.answer('Отправьте мне аудио файл, фотографию или видео')

        elif 'отзыв' in search or 'написать разработчику' in search or 'пожелан' in search or 'списаться с разработчиком' in search:
            send = bot.send_message(id, 'Введите отзыв или пожелания')
            bot.register_next_step_handler(send, answer_user, id, first_name, last_name)

        elif 'да' in search or 'нет' in search:
            await message.answer(random.choice(('Да', 'Нет')))

        elif 'или' in search and ('один' in search or 'два' in search or '1' in search or '2' in search):
            await message.answer(random.randint(1, 2))

        elif 'лучше' in search:
            await self.what_the_best(message)

        elif 'любое число' in search or 'число от' in search or 'цифра от' in search or 'рандом' in search:
            await self.number_random(message)

        elif 'население' in search or 'сколько людей' in search:
            await self.parse_population(message)

        elif 'счислен' in search or 'систем' in search:
            send = bot.send_message(id, 'Введите два числа через пробел, само число и систему счисления в которую перевести')
            bot.register_next_step_handler(send, number_system, id, first_name, last_name)

        else:
            choice_text = ('Меня еще этому не научили', 'Я не знаю про что вы', 'У меня нет ответа', 'Я еще этого не умею', 'Беспонятия про что вы')
            await message.answer(random.choice(choice_text))


    # Проверка id на блокировку
    def verify_id(self, check_id):
        block_id = []
        if check_id in block_id:
            return 'Для вас доступ ограничен'
        else:
            return 1

    # Парсинг погоды
    async def parse_weather(self, message):
        try:
            r = requests.get('https://yandex.ru/pogoda/perm')
            html = BS(r.content, 'html.parser')

            for el in html.select('.fact__temp'):
                weather = el.select('.temp__value')[0].text
                await message.answer(f'В Перми сейчас {weather}')
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Парсинг погоды] {error}')


    # Парсинг курса валюты
    async def parse_rate(self, message):
        try:
            r = requests.get('https://www.sberometer.ru/cbr/')
            html = BS(r.content, 'html.parser')

            for el in html.select('.zebra-2'):
                dollar = el.select('.b')
                await message.answer(f'Курс доллара {dollar[0].text}')
                await message.answer(f'Курс евро {dollar[1].text}')
                break

            r = requests.get('https://www.calc.ru/Bitcoin-k-rublyu-online.html')
            html = BS(r.content, 'html.parser')

            for el in html.select('.t18'):
                btc = el.select('b')[1].text.replace(' ', '.', 2)
                await message.answer(f'Курс биткоина {btc}')
                break
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Парсинг курса валюты] {error}')


    # Парсинг новостей
    async def parse_news(self, message):
        try:
            status_news = self.db.get_settings_news(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
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
                        await message.answer(f"{news} ({link_text})")
                    else:
                        await message.answer(news)
                    count_news += 1
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Парсинг новостей] {error}')


    # Парсинг новостей по ключевым словам
    async def parse_news_words(self, message, text_news=None):
        count_news = 0
        try:
            if text_news == None:
                text_news = message.text
                add_message(f'[Новости по ключевым словам] {text_news}', id, first_name, last_name)

            status_news = self.db.get_settings_news(message.from_user.id, message.from_user.first_name, message.from_user.last_name)
            r = requests.get(f'https://newssearch.yandex.ru/news/search?from=tabbar&text={text_news}')
            html = BS(r.content, 'html.parser')
            while count_news != 15:
                try:
                    for el in html.select('.news-search-story'):
                        if count_news == 15:
                            break
                        news = el.select('.news-search-story__title')[0].text
                        if status_news == 1:
                            link = el.select('.news-search-story__title-link')[0]['href']
                            await message.answer(f"{news} ({link_text})")
                        else:
                            await message.answer(news)
                        count_news += 1
                except IndexError:
                    break

            if count_news == 0:
                await message.answer('Ничего не найдено')
        except Exception as error:
            if count_news == 0:
                await message.answer('Ошибка на стороне сервера')
                logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Парсинг новостей по ключевым словам] {error}')


    # Парсинг статистики по коронавирусу
    async def parse_stat_covid(self, message):
        try:
            # Статистика в Перми
            r = requests.get('https://permkrai.ru/antivirus/')
            html = BS(r.content, 'html.parser')
            data = []

            for el in html.select('.col-sm-3'):
                data.append(el.select('.snafu__value')[0].text)

            infected = data[0].split()[1]
            #died = data[5].split()[1]

            await message.answer(f'Статистика в Перми:\nЗараженных сегодня - {infected}')

            # Статистика в России
            r = requests.get('https://coronavirusnik.ru/')
            html = BS(r.content, 'html.parser')

            for el in html.select('.cases'):
                russia_stat_infected = el.select('.plus')[0].text.replace('(', '').replace(')', '')
                break
            for el in html.select('.deaths'):
                russia_stat_died = el.select('.plus')[0].text.replace('(', '').replace(')', '')
                break

            await message.answer( f'Статистика в России:\nЗараженных сегодня - {russia_stat_infected}\nУмерло сегодня - {russia_stat_died}')

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

            await message.answer(f'Статистика по миру:\nЗараженных сегодня - {world_stat[0]}\nУмерло сегодня - {world_stat[2]}')
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Парсинг статистики по коронавирусу] {error}')


    # Скачивание аудио
    async def downloading_audio(self, id, first_name, last_name, url):
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
            await message.answer('Отправка')
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Скачивание аудио с YouTube] {error}')

    # Скачивание и отправка аудио
    async def download_audio(self, message):
        try:
            url = message.text
            await message.answer('Скачивание началось')

            await self.downloading_audio(message.from_user.id, message.from_user.first_name, message.from_user.last_name, url)

            for i in os.listdir(os.getcwd()):
                if fnmatch.fnmatch(i, '*.mp3'):
                    await bot.send_audio(id, open(i, 'rb'), parse_mode='html')

            self.db.add_message(url, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Отправка аудио с YouTube] {error}')

        try:
            for i in os.listdir(os.getcwd()):
                if fnmatch.fnmatch(i, '*.mp3'):
                    os.remove(i)
        except:
            pass


    # Отправка отзыва пользователем
    async def answer_user(self, message):
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
            await message.answer('Сообщение отправленно, спасибо большое за отзыв!')

            logger.info(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Отправка отзыва]')
            self.db.add_message(f'[Отзыв] {message.text}', id, first_name, last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Отправка отзыва] {error}')


    # Рандомное число
    async def number_random(self, message):
        try:
            numbers = re.findall('(\d+)', message.text)

            if len(numbers) < 2:
                await message.answer('Вы ввели не все числа')
            elif len(numbers) == 2:
                if int(numbers[1]) > int(numbers[0]):
                    await message.answer(random.randint(int(numbers[0])))
                else:
                    await message.answer(random.randint(int(numbers[1])))
            elif len(numbers) == 3:
                if int(numbers[1]) > int(numbers[0]):
                    await message.answer(random.randrange(int(numbers[0]), int(numbers[1]), int(numbers[2])))
                else:
                    await message.answer(random.randrange(int(numbers[1]), int(numbers[0]), int(numbers[2])))
            else:
                await message.answer('Ошибка в записи')

            self.db.add_message(message.text, id, first_name, last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Рандомное число] {error}')


    # Парсинг населения мира
    async def parse_population(self, message):
        pass


    # Перевод в систему счисления
    async def number_system(self, message):
        try:
            search = message.text.split(' ')
            if len(search) < 2:
                await message.answer('Вы ввели не все числа')
            elif len(search) == 2:
                numbers_more_nine = {10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F'}
                number = ''

                if int(search[1]) > 16:
                    await message.answer('Вы ввели слишкон большую систему счисления (max=16)')
                else:
                    while int(search[0]) > 0:
                        x = int(search[0]) % int(search[1])
                        if x > 9:
                            number += numbers_more_nine[x]
                        else:
                            number += str(x)

                        search[0] = int(search[0]) // int(search[1])

                    await message.answer(number[::-1])
            else:
                await message.answer('Ошибка в записи')

            self.db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Системы счисления] {error}')


    # Выбор что лучше
    async def what_the_best(self, message):
        try:
            choice_text = message.text.split(' ')
            if 'лучше' in choice_text:
                choice_text = choice_text[choice_text.index('лучше')+1:]

            if 'или' in choice_text:
                choice_text = ''.join(choice_text).split('или')
                await message.answer(random.choice(choice_text))
            else:
                await message.answer('Ошибка в записи')

            self.db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Что лучше] {error}')


    # Конвертация голосового сообщения в текст
    async def convert_voice_to_text(self, message, mode):
        try:
            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open("audio.ogg", 'wb') as f:
                f.write(downloaded_file)

            convert = subprocess.run(['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y'])

            r = sr.Recognizer()
            with sr.AudioFile('audio.wav') as source:
                text_from_voice = r.recognize_google(r.listen(source), language="ru_RU").lower()

            self.db.add_message(f'[Голосовое] {text_from_voice}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)

            try:
                os.remove('audio.ogg')
                os.remove('audio.wav')
            except:
                pass

            if mode == 'convert_voice':
                await message.answer(text_from_voice)
            elif mode == 'voice_search':
                return text_from_voice
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или ваше голосовое сообщение пустое')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование аудио в текст] {error}')


    # Конвертация текста в голосовое сообщение
    async def convert_text_to_voice(self, message):
        try:
            text_for_convert = message.text

            await message.answer('Конвертация началась')
            convert_text = gTTS(text=text_for_convert, lang='ru', slow=False)
            convert_text.save("audio.mp3")

            with open("audio.mp3", 'rb') as audio:
                bot.send_audio(id, audio, parse_mode='html')

            self.db.add_message(f'[Конвертация текста] {text_for_convert}', id, first_name, last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование текста в аудио] {error}')

        try:
            os.remove('audio.mp3')
        except:
            pass


    # Скачивание и конвертация фотографии в текст
    async def convert_photo_to_text(self, message):
        try:
            await message.answer('Конвертация началась')

            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            convert_name_file = 'img.jpg'
            with open(convert_name_file, 'wb') as f:
                f.write(downloaded_file)

            try:
                os.remove(convert_name_file)
            except:
                pass
            return self.converting_photo(convert_name_file)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или фотографию неудается распознать')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование фото в текст] {error}')


    def converting_photo(self, convert_name_file):
        img = Image.open(convert_name_file)
        result_text = pytesseract.image_to_string(img, lang='rus')

        return result_text

    # Конвертация аудио в текст
    async def convert_audio_to_text(self, message):
        try:
            await message.answer('Конвертация началась')

            file_info = bot.get_file(message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            convert_name_file = 'audio.ogg'

            with open(convert_name_file, 'wb') as f:
                f.write(downloaded_file)

            self.converting_audio(convert_name_file)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или файл неудается распознать')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование аудио в текст] {error}')

        try:
            os.remove(convert_name_file)
            os.remove('audio.wav')
        except:
            pass

    async def converting_audio(self, convert_name_file):
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
                        await message.answer(result_convert)
                        result_convert = str(r.recognize_google(audio, language="ru_RU").lower())
                except sr.UnknownValueError:
                    count_long_pause += 1
                    if count_long_pause > 10:
                        break

            await message.answer(result_convert)
            self.db.add_message(f'[Конвертация аудио файла] {result_convert}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)


    # Конвертация видео в текст
    async def convert_video_to_text(self, message):
        try:
            await message.answer('Конвертация началась')

            file_info = bot.get_file(message.video.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("video.mp4", 'wb') as f:
                f.write(downloaded_file)

            audio = VideoFileClip('video.mp4').audio
            audio.write_audiofile('audio.mp3')
            convert_name_file = 'audio.mp3'

            self.converting_audio(convert_name_file)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или видео неудается распознать')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование видео в текст] {error}')

        try:
            os.remove('video.mp4')
            os.remove(convert_name_file)
            os.remove('audio.wav')
        except:
            pass


    # Конвертирование документа в текст
    async def convert_document_to_text(self, message):
        try:
            audio_name = ['ogg', 'opus', 'mp3', 'wav', 'aac']
            photo_name = ['jpeg', 'jpg', 'png']
            video_name = ['mp4', 'avi', 'mkv']

            await message.answer('Конвертация началась')

            file_name = message.document.file_name.split('.')

            if file_name[-1] in photo_name:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                convert_name_file = 'img.' + str(file_name[-1])

                with open(convert_name_file, 'wb') as f:
                    f.write(downloaded_file)

                result_convert_photo = converting_photo(convert_name_file)

                await message.answer(result_convert_photo)
                self.db.add_message(f'[Конвертация фото в текст] {result_convert_photo}', id, first_name, last_name)

            elif file_name[-1] in audio_name:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                convert_name_file = 'audio.ogg'

                with open(convert_name_file, 'wb') as f:
                    f.write(downloaded_file)

                self.converting_audio(convert_name_file)

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

                self.converting_audio(convert_name_file)

            try:
                os.remove(convert_video_file)
                os.remove('audio.wav')
            except:
                pass
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или файл неудается распознать')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование документа в текст] {error}')

        try:
            os.remove(convert_name_file)
        except:
            pass



@dp.callback_query_handler(lambda call: call.data == 'weather')
async def callback(call: types.CallbackQuery):
    await Function().parse_weather(call.message)

@dp.callback_query_handler(lambda call: call.data == 'valuta')
async def callback(call: types.CallbackQuery):
    await Function().parse_rate(call.message)

@dp.callback_query_handler(lambda call: call.data == 'news')
async def callback(call: types.CallbackQuery):
    await Function().parse_news(call.message)

@dp.callback_query_handler(lambda call: call.data == 'news_word')
async def callback(call: types.CallbackQuery):
    await Function().parse_news_words(call.message)

@dp.callback_query_handler(lambda call: call.data == 'virus')
async def callback(call: types.CallbackQuery):
    await Function().parse_stat_covid(call.message)

@dp.callback_query_handler(lambda call: call.data == 'yes_or_not')
async def callback(call: types.CallbackQuery):
    await call.message.answer(random.choice(('Да', 'Нет')))

@dp.callback_query_handler(lambda call: call.data == 'one_or_two')
async def callback(call: types.CallbackQuery):
    await call.message.answer(random.randint(1, 2))

@dp.callback_query_handler(lambda call: call.data == 'random_number')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'what_best')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'system_number')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'click_download_audio')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'convert_audio_to_text')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'convert_text_to_audio')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'answer_user')
async def callback(call: types.CallbackQuery):
    pass

@dp.callback_query_handler(lambda call: call.data == 'convert_audio_photo_video_to_text')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Отправьте фото, аудио файл или видео')

@dp.callback_query_handler(lambda call: call.data == 'convert_video_youtube_to_text')
async def callback(call: types.CallbackQuery):
    pass
