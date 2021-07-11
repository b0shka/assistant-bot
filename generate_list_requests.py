from generate_error_words import generate_errors

weather = set(['погода', 'weather'])
for i in list(weather)[0:2]:
	for j in range(1, 3):
		weather.update(list(generate_errors(i, j)))

rate = set(['курс', 'валют', 'долар', 'доллар', 'евро', 'боткоин', 'rate'])
for i in list(rate)[0:7]:
	for j in range(1, 3):
		if len(i.replace(' ', '')) <= 5 and j == 2:
			continue
		rate.update(list(generate_errors(i, j)))

news = set(['новости', 'news'])
for i in list(news)[0:2]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        news.update(list(generate_errors(i, j)))

covid = set(['статистика', 'коронавирус', 'covid'])
for i in list(covid)[0:3]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        covid.update(list(generate_errors(i, j)))

skills = set(['что ты', 'умеешь', 'skil', 'what you'])
for i in list(skills)[0:3]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        skills.update(list(generate_errors(i, j)))

download_audio = set(['скачать аудио', 'музык'])
for i in list(download_audio)[0:2]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        download_audio.update(list(generate_errors(i, j)))

convert = set(['конвертировать'])
for j in range(1, 3):
	convert.update(list(generate_errors(list(convert)[0], j)))

vioce_to_text = set(['голосово'])
for j in range(1, 3):
	vioce_to_text.update(list(generate_errors(list(vioce_to_text)[0], j)))

text_to_audio = set(['в аудио', 'текст', 'аудио в'])
for i in list(text_to_audio)[0:3]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        text_to_audio.update(list(generate_errors(i, j)))

audio_photo_video_to_text = set(['аудио', 'фото', 'видео'])
for i in list(audio_photo_video_to_text)[0:3]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        audio_photo_video_to_text.update(list(generate_errors(i, j)))

feedback = set(['отзыв', 'написать разработчику', 'пожелан', 'списаться с разработчиком'])
for i in list(feedback)[0:4]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        feedback.update(list(generate_errors(i, j)))

random_number = set(['любое число', 'число от', 'цифра от', 'рандом'])
for i in list(random_number)[0:4]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        random_number.update(list(generate_errors(i, j)))

population = set(['население', 'сколько людей'])
for i in list(population)[0:2]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        population.update(list(generate_errors(i, j)))

country = set(['стран'])
for j in range(1, 3):
	country.update(list(generate_errors(list(country)[0], j)))

system_number = set(['счислен', 'систем'])
for i in list(system_number)[0:2]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        system_number.update(list(generate_errors(i, j)))

throw = set(['бросить'])
for j in range(1, 3):
	throw.update(list(generate_errors(list(throw)[0], j)))

recognition = set(['найти', 'определить'])
for i in list(recognition)[0:2]:
    for j in range(1, 3):
        if len(i.replace(' ', '')) <= 5 and j == 2:
            continue
        recognition.update(list(generate_errors(i, j)))


list_all_requests = {
    'weather': weather, 
    'rate': rate, 
    'news': news, 
    'covid': covid, 
    'skills': skills,
	'download_audio': download_audio,
	'convert': convert,
	'vioce_to_text': vioce_to_text,
	'text_to_audio': text_to_audio,
	'audio_photo_video_to_text': audio_photo_video_to_text,
	'feedback': feedback,
	'random_number': random_number,
	'population': population,
	'country': country,
	'system_number': system_number,
	'throw': throw,
	'recognition': recognition
}

for i in list_all_requests.keys():
    with open(f'data/{i}.txt', 'w') as file:
        file.write(', '.join(list_all_requests[i]))

'''
import re

s = 'weather'

print(bool(re.search('|'.join(weather), s)))
print(re.search('|'.join(weather), s))

if len(re.findall('|'.join(weather), s)) == 1:
    print('good')
'''