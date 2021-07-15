from PIL import Image, ImageDraw
from bs4 import BeautifulSoup as BS
from gtts import gTTS
from moviepy.editor import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config import logger, bot, user_email, user_password, user_id, bot_id, Form
from database import Database
import requests
import youtube_dl
import os
import fnmatch
import speech_recognition as sr
import subprocess
import re
import datetime
import random
import pytesseract
import smtplib
import asyncio
import face_recognition


class Functions:
    def __init__(self):
        self.db = Database('server.db')

    # Проверка id на блокировку
    async def verify_id(self, check_id):
        block_id = []
        if check_id in block_id:
            return await 'Для вас доступ ограничен'
        else:
            return await 1

    # Парсинг погоды
    async def parse_weather(self, message, city):
        try:
            r = requests.get(f'https://yandex.ru/pogoda/{city}')
            html = BS(r.content, 'html.parser')

            for el in html.select('.header-title'):
                parse_city = el.select('.title_level_1')[0].text

            if parse_city == 'Такой страницы не существует':
                await message.answer('Вы указали /settings не существующий город или ввели его на русском')
            else:
                for el in html.select('.fact__temp'):
                    temp = el.select('.temp__value')[0].text
                    await message.answer(f'{parse_city} {temp}')
                    break
                
                for el in html.select('.fact__feelings'):
                    temp_feel = el.select('.temp__value_with-unit')[0].text
                    await message.answer(f'Ощущается как {temp_feel}')

                    weather = el.select('.link__condition')[0].text
                    await message.answer(f'{weather}')
                    break

                for el in html.select('.term_orient_v'):
                    wind = el.select('.term__value')[0].text
                    await message.answer(f'Ветер {wind}')
                    break

                for el in html.select('.title-icon'):
                    icon_text = el.select('.title-icon__text')[0].text
                    await message.answer(icon_text)
                    break

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
            status_news = self.db.get_settings_news(message.from_user.id, message.from_user.first_name, message.from_user.last_name)[0]
            r = requests.get('https://yandex.ru/news/')
            html = BS(r.content, 'html.parser')
            count_news = 0
            while count_news != 10:
                for el in html.select('.mg-card'):
                    if count_news == 10:
                        break
                    news = el.select('.mg-card__title')[0].text
                    if status_news == 1:
                        link = el.select('.mg-card__link')[0]['href']
                        await message.answer(f"{news} ({link})")
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

            status_news = self.db.get_settings_news(message.from_user.id, message.from_user.first_name, message.from_user.last_name)[0]
            r = requests.get(f'https://newssearch.yandex.ru/news/search?from=tabbar&text={text_news}')
            html = BS(r.content, 'html.parser')
            while count_news != 10:
                try:
                    for el in html.select('.news-search-story'):
                        if count_news == 10:
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

            self.db.add_message(f'[Новости по ключевым словам] {text_news}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)
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

            for el in html.select('.col-sm-3'):
                infected = el.select('.snafu__value')[0].text.split()[1]
                break

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
    async def downloading_audio(self, message, url):
        try:
            file_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with youtube_dl.YoutubeDL(file_opts) as file:
                file.download([url])
        except Exception as error:
            await message.answer('Ошибка при скачивании файла')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Скачивание аудио с YouTube] {error}')

    # Скачивание и отправка аудио
    async def download_audio(self, message, url=None):
        try:
            if url == None:
                url = message.text

                if '&list' in url:
                    url = url.split('&list')
                    url = url[0]

            await message.answer('Скачивание началось')
            await self.downloading_audio(message, url)
            await message.answer('Отправка')

            for i in os.listdir(os.getcwd()):
                if fnmatch.fnmatch(i, '*.mp3') or fnmatch.fnmatch(i, '*.m4a'):
                    await bot.send_audio(message.from_user.id, open(i, 'rb'))
                    os.remove(i)

            self.db.add_message(url, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Отправка аудио с YouTube] {error}')


    # Отправка отзыва пользователем
    async def answer_user(self, message, get_text):
        # https://accounts.google.com/DisplayUnlockCaptcha
        try:
            msg = MIMEMultipart()
            msg['Subject'] = 'Отзыв'
            body = get_text
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(user_email, user_password)
            server.sendmail(user_email, user_email, msg.as_string())
            server.quit()
            await message.answer('Сообщение отправленно, спасибо большое за отзыв!')

            logger.info(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Отправка отзыва]')
            self.db.add_message(f'[Отзыв] {get_text}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Отправка отзыва] {error}')


    # Рандомное число
    async def number_random(self, message, get_number=None):
        try:
            if get_number == None:
                numbers = re.findall('(\d+)', message.text)
            else:
                numbers = re.findall('(\d+)', get_number)

            if len(numbers) == 0:
                await message.answer('Введите промежуток через пробел')
                await Form.number_random.set()
            else:
                if len(numbers) == 1:
                    if get_number == None:
                        if ' до ' in message.text or message.text.split(' ')[0] == 'до':
                            await message.answer(random.randint(0, int(numbers[0])))
                        elif ' от ' in message.text or message.text.split(' ')[0] == 'от':
                            await message.answer(random.randint(int(numbers[0]), 1000000))
                        else:
                            await message.answer('Вы ввели не все числа')
                    else:
                        if ' до ' in get_number or get_number.split(' ')[0] == 'до':
                            await message.answer(random.randint(0, int(numbers[0])))
                        elif ' от ' in get_number or get_number.split(' ')[0] == 'от':
                            await message.answer(random.randint(int(numbers[0]), 1000000))
                        else:
                            await message.answer('Вы ввели не все числа')
                elif len(numbers) == 2:
                    if int(numbers[1]) > int(numbers[0]):
                        await message.answer(random.randint(int(numbers[0]), int(numbers[1])))
                    else:
                        await message.answer(random.randint(int(numbers[1]), int(numbers[0])))
                elif len(numbers) == 3:
                    if int(numbers[1]) > int(numbers[0]):
                        await message.answer(random.randrange(int(numbers[0]), int(numbers[1]), int(numbers[2])))
                    else:
                        await message.answer(random.randrange(int(numbers[1]), int(numbers[0]), int(numbers[2])))
                else:
                    await message.answer('Ошибка в записи')

                if get_number == None:
                    self.db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
                else:
                    self.db.add_message(get_number, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Рандомное число] {error}')


    # Парсинг населения мира
    async def parse_population(self, message):
        r = requests.get('https://countrymeters.info/ru/World')
        html = BS(r.content, 'html.parser')
        count = 0

        for el in html.select('#population_clock'):
            count_people = el.select('.counter')
            count += 1
            if count == 6:
                break

        await message.answer(f'Население мира {count_people[0].text}')
        await message.answer(f'Всего мужчин {count_people[1].text}')
        await message.answer(f'Всего женщин {count_people[2].text}')
        await message.answer(f'Рождено в этом году {count_people[3].text}')
        await message.answer(f'Рождено сегодня {count_people[4].text}')
        await message.answer(f'Умерло в этом году {count_people[5].text}')
        await message.answer(f'Умерло сегодня {count_people[6].text}')

    import chardet

    # Парсинг населения стран
    async def parse_population_country(self, message):
        r = requests.get('https://countrymeters.info/ru/World')
        r.encoding = 'utf8'

        soup = BS(r.text, 'lxml')
        block = soup.find('table', class_='facts')


        count_country = block.find_all('td')
        info_population = []

        for i in count_country:
            if i.text != '' and '%' not in i.text:
                info_population.append(i.text)

        for i in range(0, len(info_population), 3):
            text_message = ''
            for j in range(1, 3):
                text_message += info_population[i+j] + ' '
            await message.answer(text_message)
            
            if info_population[i] == '10':
                break


    # Перевод в систему счисления
    async def number_system(self, message, get_text):
        try:
            search = get_text.split(' ')
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
    async def what_the_best(self, message, get_text=None):
        try:
            if get_text == None:
                choice_text = message.text.split(' ')
            else:
                choice_text = get_text.split(' ')

            if 'лучше' in choice_text:
                choice_text = choice_text[choice_text.index('лучше')+1:]

            if len(choice_text) == 0:
                await message.answer('Введите два действия через или')
                await Form.what_the_best.set()
            else:
                if 'или' in choice_text:
                    choice_text = ' '.join(choice_text).split('или')
                    await message.answer(random.choice(choice_text))
                else:
                    await message.answer('Ошибка в записи')

                self.db.add_message(message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Что лучше] {error}')


    # Конвертация голосового сообщения в текст
    async def convert_voice_to_text(self, message, mode, file_get=None):
        try:
            await message.answer('Конвертация началась')

            if file_get == None:
                file_info = await bot.get_file(message.voice.file_id)
            else:
                file_info = await bot.get_file(file_get)

            downloaded_file = await bot.download_file(file_info.file_path, "audio.ogg")

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
    async def convert_text_to_voice(self, message, text_for_convert):
        try:
            await message.answer('Конвертация началась')
            convert_text = gTTS(text=text_for_convert, lang='ru', slow=False)
            convert_text.save("audio.mp3")

            with open("audio.mp3", 'rb') as audio:
                await bot.send_audio(message.from_user.id, audio)

            self.db.add_message(f'[Конвертация текста] {text_for_convert}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)
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

            convert_name_file = 'img.jpg'
            file_info = await bot.get_file(message.photo[-1].file_id)
            await bot.download_file(file_info.file_path, convert_name_file)

            await self.converting_photo(convert_name_file, message)

            try:
                os.remove(convert_name_file)
            except:
                pass
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или фотографию неудается распознать')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование фото в текст] {error}')


    async def converting_photo(self, convert_name_file, message):
        img = Image.open(convert_name_file)
        result_text = pytesseract.image_to_string(img, lang='rus')

        await message.answer(result_text)
        self.db.add_message(f'[Конвертация фотографии в текст] {result_text}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)

    # Конвертация аудио в текст
    async def convert_audio_to_text(self, message):
        try:
            await message.answer('Конвертация началась')

            convert_name_file = 'audio.ogg'
            file_info = await bot.get_file(message.audio.file_id)
            await bot.download_file(file_info.file_path, convert_name_file)

            await self.converting_audio(convert_name_file, message)
        except Exception as error:
            await message.answer('Ошибка на стороне сервера или файл неудается распознать')
            logger.error(f'[{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}] [Конвертирование аудио в текст] {error}')

        try:
            os.remove(convert_name_file)
            os.remove('audio.wav')
        except:
            pass

    async def converting_audio(self, convert_name_file, message):
        subprocess.run(['ffmpeg', '-i', convert_name_file, 'audio.wav', '-y'])

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
                        self.db.add_message(f'[Конвертация аудио файла] {result_convert}', message.from_user.id, message.from_user.first_name, message.from_user.last_name)
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

            file_info = await bot.get_file(message.video.file_id)
            await bot.download_file(file_info.file_path, "video.mp4")

            audio = VideoFileClip('video.mp4').audio
            audio.write_audiofile('audio.mp3')
            convert_name_file = 'audio.mp3'

            await self.converting_audio(convert_name_file, message)
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
                convert_name_file = 'img.' + str(file_name[-1])
                file_info = await bot.get_file(message.document.file_id)
                await bot.download_file(file_info.file_path, convert_name_file)

                await self.converting_photo(convert_name_file, message)

            elif file_name[-1] in audio_name:
                convert_name_file = 'audio.ogg'
                file_info = await bot.get_file(message.document.file_id)
                await bot.download_file(file_info.file_path, convert_name_file)

                await self.converting_audio(convert_name_file, message)

                try:
                    os.remove('audio.wav')
                except:
                    pass

            elif file_name[-1] in video_name:
                convert_video_file = 'video.' + str(file_name[-1])
                file_info = await bot.get_file(message.document.file_id)
                await bot.download_file(file_info.file_path, convert_video_file)

                audio = VideoFileClip(convert_video_file).audio
                audio.write_audiofile('audio.mp3')
                convert_name_file = 'audio.mp3'

                await self.converting_audio(convert_name_file, message)

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


    # Отправка информации на почту
    async def send_information_to_email(self, message=None):
        try:
            msg = MIMEMultipart()
            msg['Subject'] = 'Данные'
            body = 'Отправка log/db'
            msg.attach(MIMEText(body, 'plain'))

            try:
                part = MIMEApplication(open('info/info.log', 'rb').read())
                part.add_header('Content-Disposition', 'attachment', filename = 'info.log')
                msg.attach(part)

                part = MIMEApplication(open('info/server.db', 'rb').read())
                part.add_header('Content-Disposition', 'attachment', filename = 'server.db')
                msg.attach(part)
            except:
                pass

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(user_email, user_password)
            server.sendmail(user_email, user_email, msg.as_string())
            server.quit()

            if message != None:
                await message.answer('Отправка завершена')
        except Exception as error:
            logger.error(f'[send_email] {error}')


    # Парсинг погоды
    def message_mailig(self):
        try:
            mailing_text = 'Новости:\n'

            # News
            r = requests.get('https://yandex.ru/news/')
            html = BS(r.content, 'html.parser')
            count_news = 0
            while count_news != 10:
                for el in html.select('.mg-card'):
                    if count_news == 10:
                        break
                    news = el.select('.mg-card__title')[0].text
                    mailing_text += news + '\n'
                    count_news += 1

            # Rate
            mailing_text += '\nКурс валюты\n'

            r = requests.get('https://www.sberometer.ru/cbr/')
            html = BS(r.content, 'html.parser')

            for el in html.select('.zebra-2'):
                dollar = el.select('.b')
                mailing_text += f'Курс доллара {dollar[0].text}\n'
                mailing_text += f'Курс евро {dollar[1].text}\n'
                break

            r = requests.get('https://www.calc.ru/Bitcoin-k-rublyu-online.html')
            html = BS(r.content, 'html.parser')

            for el in html.select('.t18'):
                btc = el.select('b')[1].text.replace(' ', '.', 2)
                mailing_text += f'Курс биткоина {btc}\n'
                break

            # Covid
            mailing_text += '\nСтатистика по коронавирусу\n'

            # Статистика в Перми
            r = requests.get('https://permkrai.ru/antivirus/')
            html = BS(r.content, 'html.parser')

            for el in html.select('.col-sm-3'):
                infected = el.select('.snafu__value')[0].text.split()[1]
                break

            mailing_text += f'Статистика в Перми:\nЗараженных сегодня - {infected}\n'

            # Статистика в России
            r = requests.get('https://coronavirusnik.ru/')
            html = BS(r.content, 'html.parser')

            for el in html.select('.cases'):
                russia_stat_infected = el.select('.plus')[0].text.replace('(', '').replace(')', '')
                break
            for el in html.select('.deaths'):
                russia_stat_died = el.select('.plus')[0].text.replace('(', '').replace(')', '')
                break

            mailing_text += f'Статистика в России:\nЗараженных сегодня - {russia_stat_infected}\nУмерло сегодня - {russia_stat_died}\n'

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

            mailing_text += f'Статистика по миру:\nЗараженных сегодня - {world_stat[0]}\nУмерло сегодня - {world_stat[2]}\n'


            return mailing_text

        except Exception as error:
            logger.error(f'[message_mailig] {error}')


    # Отправка рассылки по времени
    async def mailing_subscribe_users(self, sleep_for):
        try:
            while True:
                await asyncio.sleep(sleep_for)
                list_time_mailing = await Database('server.db').get_time_mailing_and_users()

                for i in list_time_mailing.keys():
                    time_mailing = list_time_mailing[i].split(':')

                    if len(time_mailing) == 3:
                        for j in time_mailing:
                            if j[0] == '0':
                                new_j = j.replace('0', '', 1)
                                time_mailing[time_mailing.index(j)] = new_j

                    time_mailing = [int(num) for num in time_mailing]

                    if datetime.datetime.now().hour == time_mailing[0] and datetime.datetime.now().minute == time_mailing[1] and (datetime.datetime.now().second >= time_mailing[2] and (datetime.datetime.now().second - sleep_for) <= time_mailing[2]):
                        text_mailing = self.message_mailig()

                        await bot.send_message(i, text_mailing)
                        await self.send_information_to_email()
        except Exception as error:
            logger.error(f'[mailing_subscribe_users] {error}')


    # Принудительная отправка сообщений всем пользователям
    async def forced_mailing(self, mailing_text):
        try:
            subscribe_users_list = Database('server.db').get_all_users()

            for i in subscribe_users_list:
                if i[0] != bot_id and i[0] != user_id:
                    await bot.send_message(i[0], mailing_text)

            await bot.send_message(user_id, 'Отправка завершена')
        except Exception as error:
            await bot.send_message(user_id, 'Ошибка на стороне сервера')
            logger.error(f'[forced_mailing] {error}')


    # Отправка файла с базой данных
    async def send_db(self, message):
        try:
            await bot.send_document(user_id, open('info/server.db', 'rb'))
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[send_db] {error}')


    # Отправка файла с log
    async def send_log(self, message):
        try:
            await bot.send_document(user_id, open('info/info.log', 'rb'))
        except Exception as error:
            await message.answer('Ошибка на стороне сервера')
            logger.error(f'[send_log] {error}')


    # Определение лиц на фотографии
    async def recognition_faces(self, message, photo_name):
        try:
            image = face_recognition.load_image_file(photo_name)
            locations = face_recognition.face_locations(image)

            pil_image = Image.fromarray(image)
            pil_draw = ImageDraw.Draw(pil_image)

            for (top, right, bottom, left) in locations:
                pil_draw.rectangle(((left, top), (right, bottom)), outline=(255, 255, 0), width=4)

            del pil_draw
            pil_image.save(f"new_{photo_name}")

            await bot.send_photo(message.from_user.id, open(f"new_{photo_name}", 'rb'))
        except Exception as error:
            await bot.send_message(user_id, 'Ошибка на стороне сервера')
            logger.error(f'[recognition_faces] {error}')

        try:
            os.remove(photo_name)
            os.remove(f'new_{photo_name}')
        except:
            pass