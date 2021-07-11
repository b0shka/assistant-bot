from generate_list_requests import list_all_requests


for i in list_all_requests.keys():
    with open(f'data/{i}.txt', 'r') as file:
        #exec("%s = %d" % (i, len(file.read().split(', '))))
        globals()[i] = file.read().split(', ')