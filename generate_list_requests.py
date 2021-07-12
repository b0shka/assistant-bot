from list_requests import *
from generate_error_words import generate_errors


for name in list_requests:
    globals()[name] = set(globals()[f'{name}_main'])
    for i in list(globals()[name])[0:len(globals()[name])]:
        for j in range(1, 3):
            if len(i.replace(' ', '')) <= 5 and j == 2:
                continue
            globals()[name].update(list(generate_errors(i, j)))

for i in list_requests:
    with open(f'data/{i}.txt', 'w') as file:
        file.write(', '.join(globals()[i]))


'''
import re

s = 'weather'

print(bool(re.search('|'.join(weather), s)))
print(re.search('|'.join(weather), s))

if len(re.findall('|'.join(weather), s)) == 1:
    print('good')
'''