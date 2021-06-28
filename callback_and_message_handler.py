import random
from aiogram import types
from aiogram.dispatcher import FSMContext
from config import dp, Form
from functions import Functions


@dp.message_handler(state=Form.url)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await Functions().download_audio(message, get_text)
    await state.finish()

@dp.message_handler(content_types=['voice'], state=Form.voice_msg)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.voice.file_id
    await Functions().convert_voice_to_text(message, 'convert_voice', get_text)
    await state.finish()

@dp.message_handler(state=Form.text_for_convert)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await Functions().convert_text_to_voice(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.feedback)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await Functions().answer_user(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.number_system)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await Functions().number_system(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.number_random)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await Functions().number_random(message, get_text)
    await state.finish()

@dp.message_handler(state=Form.what_the_best)
async def answer_q(message: types.Message, state: FSMContext):
    get_text = message.text
    await Functions().what_the_best(message, get_text)
    await state.finish()



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
    await call.message.answer('Введите промежуток через пробел')
    await Form.number_random.set()

@dp.callback_query_handler(lambda call: call.data == 'what_best')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Введите два действия через или')
    await Form.what_the_best.set()

@dp.callback_query_handler(lambda call: call.data == 'system_number')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Введите два числа через пробел, само число и систему счисления в которую перевести')
    await Form.number_system.set()

@dp.callback_query_handler(lambda call: call.data == 'click_download_audio')
async def callback(call: types.CallbackQuery):
    await call.message.answer("Введите url")
    await Form.url.set()

@dp.callback_query_handler(lambda call: call.data == 'convert_audio_to_text')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Отправьте или перешлите голосовое сообщение')
    await Form.voice_msg.set()

@dp.callback_query_handler(lambda call: call.data == 'convert_text_to_audio')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Напишите что конвертировать')
    await Form.text_for_convert.set()

@dp.callback_query_handler(lambda call: call.data == 'answer_user')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Введите отзыв или пожелания')
    await Form.feedback.set()

@dp.callback_query_handler(lambda call: call.data == 'convert_audio_photo_video_to_text')
async def callback(call: types.CallbackQuery):
    await call.message.answer('Отправьте фото, аудио файл или видео')
