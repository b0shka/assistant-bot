import random
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, Form
from functions import Functions
from database import Database

func = Functions()
db = Database('server.db')


@dp.message_handler(state=Form.url)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.download_audio(message, get_text)
    await state.finish()

@dp.message_handler(content_types=['voice'], state=Form.voice_msg)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.voice.file_id
    await func.convert_voice_to_text(message, 'convert_voice', get_text)
    await state.finish()

@dp.message_handler(state=Form.text_for_convert)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.convert_text_to_voice(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.feedback)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.answer_user(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.number_system)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.number_system(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.number_random)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.number_random(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.what_the_best)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.what_the_best(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.mailing)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.forced_mailing(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.search_news)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await func.parse_news_words(message, get_text)
    await state.finish()



@dp.callback_query_handler(lambda call: True)
async def callback(call):
    if call.data == 'weather':
        await func.parse_weather(call.message)

    elif call.data == 'valuta':
        await func.parse_rate(call.message)

    elif call.data == 'news':
        await func.parse_news(call.message)

    elif call.data == 'news_word':
        await call.message.answer('Введите по каким словам искать')
        await Form.search_news.set()

    elif call.data == 'virus':
        await func.parse_stat_covid(call.message)

    elif call.data == 'yes_or_not':
        await call.message.answer(random.choice(('Да', 'Нет')))

    elif call.data == 'one_or_two':
        await call.message.answer(random.randint(1, 2))

    elif call.data == 'random_number':
        await call.message.answer('Введите промежуток через пробел')
        await Form.number_random.set()

    elif call.data == 'what_best':
        await call.message.answer('Введите два действия через или')
        await Form.what_the_best.set()

    elif call.data == 'system_number':
        await call.message.answer('Введите два числа через пробел, само число и систему счисления в которую перевести')
        await Form.number_system.set()

    elif call.data == 'click_download_audio':
        await call.message.answer("Введите url")
        await Form.url.set()

    elif call.data == 'convert_voice_to_text':
        await call.message.answer('Отправьте или перешлите голосовое сообщение')
        await Form.voice_msg.set()

    elif call.data == 'convert_text_to_audio':
        await call.message.answer('Напишите что конвертировать')
        await Form.text_for_convert.set()

    elif call.data == 'answer_user':
        await call.message.answer('Введите отзыв или пожелания')
        await Form.feedback.set()

    elif call.data == 'convert_audio_photo_video_to_text':
        await call.message.answer('Отправьте фото, аудио файл или видео')

    elif call.data == 'population_people':
        await func.parse_population(call.message)

    db.add_message(call.data, call.message.from_user.id, call.message.from_user.first_name, call.message.from_user.last_name)
