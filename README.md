# QuizBot

The quiz-bot integrated to Telegram and vk.com.
The bot uses prepared question-answer sample.json file that uses
key-value (question-answer) structure. The bot doesn't use any AI
frameworks or cloud-based services. In this case your answers must be
the same as in sample.json file. So, the better way to use the bot - 
is a kind of quiz with unambiguous answers (for example math quiz).

### How to install

```
git clone git@github.com:Gennadynemchin/QuizBot.git
```

Use .env.example as a draft and fill all of the requested
variables:

```
TELEGRAM_TOKEN=<YOUR-TELEGRAM-TOKEN>
REDIS_HOST=<YOUR-REDIS-DB-URL>
REDIS_LOGIN=<YOUR-REDIS-LOGIN>
REDIS_PASSWORD=<YOUR-REDIS-PASSWORD>
VK_TOKEN=<YOUR-VK-TOKEN>
QUESTIONS_PATH=<PATH-TO-QUESTIONS-FILE>
FOLDER_PATH=<PATH-TO-FOLDER-WITH-RAW-QUESTIONS-DATA>
```

- Get your Telegram bot token from https://t.me/BotFather
- You can deploy Redis database on your own server or use for example
on https://redis.com
- For VK bot you have to create new community. After that go to
the Community - Settings - API usage - Access tokens - Create token.
Then go to the Messages - Bot settings and turn on "Community messages"

### How to get questions

You can use sample.json which has questions and answers. However,
there is quiz-questions folder that has several .txt files with
questions and answers. Before use with both of the bots you have to
prepare sample.json file with questions and answers as dictionary.
For generating a new sample.json just run:

```
parse_quiz_questions.py
```
The script is already has path to the folder with env ```FOLDER_PATH```.
The all the file in the folder will be parsed and
saved as the ```QUESTIONS_PATH```. Just put ```QUESTIONS_PATH```
filename (ex. sample.json) in root of your app.
Also you can change the path to the parsed and prepared questions
using ```QUESTIONS_PATH``` in .env file. 


### How to start

Run in a terminal:

```
tg_bot.py
vk_bot.py
```

### Deploy with Docker

1. Copy this repository to your server:
```
git clone git@github.com:Gennadynemchin/QuizBot.git
```
2. `cd QuizBot`
3. `nano .env.example`. Then fill all needed variables as shown above. 
Save edited file as `.env`;
4. Build an image:
`docker build -t your-image-name . `
5. Then `docker run -d --restart always your-image-name`
