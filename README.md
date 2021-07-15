# Assistant bot
Assistant bot in telegram, with many useful features
____
### Install everything you need and run
#### Installation
```
git clone https://github.com/b0shka/assistant-bot.git
cd assistant-bot/
pip3 install -r requirements.txt
```
In the file `assistant-bot/config.py` in the `email` and `password` fields, we enter our data for further information about users and the status of the bot
#### Run
```
cd assistant-bot/
python3 ./main.py
```

### Additionally
A `tgbot.service` file was also created to run this bot on the server. The `assistant-bot/data` folder contains text files with all possible erroneous requests
