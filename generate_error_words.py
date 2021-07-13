symbols_en = "qwertyuiopasdfghjklzxcvbnm;',./"
symbols_ru = "йцукенгшщзхъфывапролджэячсмитьбю."

def check_language(message):
	try:
		for i in symbols_en:
			if i in message:
				return 'EN'

		for j in symbols_ru:
			if j in message:
				return 'RU'

		return 'Not found'
	except Exception as error:
		print(f'[ERROR] {error}')


def generate_errors(message, count_error):
	try:
		error_words = set()
		symbols = {'EN': symbols_en, 'RU': symbols_ru}
		language = check_language(message)

		for i in symbols[language]:
			for j in message:
				error_message = message.replace(j, i, 1)

				if count_error > 1 and count_error < len(message) and len(message) > 5:
					for count_ in range(count_error-1):
						for symb in symbols[language]:
							for s in message:
								if s != j:
									two_error_message = error_message.replace(s, symb, 1)
									error_words.add(two_error_message)
				else:
					error_words.add(error_message)

		return error_words
	except TypeError:
		print('[INFO] Language not found')
	except Exception as error:
		print(f'[ERROR] {error}')