list_requests = [
    'weather', 
    'rate', 
    'news', 
    'covid', 
    'skills',
	'download_audio',
	'convert',
	'vioce_to_text',
	'text_to_audio',
	'audio_photo_video_to_text',
	'feedback',
	'random_number',
	'population',
	'country',
	'system_number',
	'throw',
	'recognition'
]

for i in list_requests:
    with open(f'data/{i}.txt', 'r') as file:
        #exec("%s = %d" % (i, len(file.read().split(', '))))
        globals()[i] = file.read().split(', ')

weather_main = ['погода', 'weather']
rate_main = ['курс', 'валют', 'долар', 'доллар', 'евро', 'боткоин', 'rate']
news_main = ['новости', 'news']
covid_main = ['статистика', 'коронавирус', 'covid']
skills_main = ['что ты', 'умеешь', 'skil', 'what you']
download_audio_main = ['скачать аудио', 'музык']
convert_main = ['конвертировать', 'convert']
vioce_to_text_main = ['голосово']
text_to_audio_main = ['в аудио', 'текст в']
audio_photo_video_to_text_main = ['аудио', 'фото', 'видео']
feedback_main = ['отзыв', 'разработчик', 'пожелан']
random_number_main = ['любое число', 'число от', 'цифра от', 'рандом']
population_main = ['население', 'сколько людей']
country_main = ['стран']
system_number_main = ['счислен', 'систем']
throw_main = ['бросить']
recognition_main = ['найти', 'определить', 'распознать']