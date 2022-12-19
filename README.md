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
```

- Get your Telegram bot token from https://t.me/BotFather
- You can deploy Redis database on your own server or use for example
on https://redis.com.
- For VK bot you have to create new community. After that go to
the Community - Settings - API usage - Access tokens - Create token.
Then go to the Messages - Bot settings and turn on "Community messages"

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
