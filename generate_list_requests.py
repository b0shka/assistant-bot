from list_requests import *
from generate_error_words import generate_errors


for name in list_requests:
    globals()[name] = set(globals()[f'{name}_main'])

    for i in list(globals()[name])[:len(globals()[name])]:
        for j in range(1, 3):
            globals()[name].update(list(generate_errors(i, j)))

            with open(f'data/{name}.txt', 'w') as file:
                file.write(', '.join(globals()[name]))