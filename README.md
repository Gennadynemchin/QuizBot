# QuizBot

The quiz-bot integrated to Telegram and vk.com.
The bot uses prepared question-answer sample.json file that uses
key-value (question-answer) structure. The bot doesn't use any AI
frameworks or cloud-based services. In this case your answers must be
the same as in sample.json file. So, the better way to use the bot - 
is a kind of quiz with unambiguous answers (for example math quiz).

### How to install

```
git clone https://github.com/Gennadynemchin/QuizBot.git
```

- Use .env.example as a draft and fill all of the requested
variables:

```
TELEGRAM_TOKEN='YOUR_TELEGRAM_TOKEN'
VK_TOKEN='VK_GROUP_TOKEN'
GOOGLE_APPLICATION_CREDENTIALS='JSON_WITH_GOOGLE_CREDENTIALS'
GOOGLE_CLOUD_PROJECT='ID_OF_GOOGLE_CLOUD_PROJECT'
```

### How to start

Run in a terminal:

```
tg_bot.py
vk_bot.py
```

### Deploy with Docker

1. Copy this repository to your server:
```
git clone git@github.com:Gennadynemchin/VerbGameBot.git
```
2. `cd VerbGameBot`
3. `nano .env.example`. Then fill all needed variables as shown above;
4. `nano verbgamebot_credentials.json.example` Then save it;
5. Save google credentials as `verbgamebot_credentials.json`
6. Build an image:
`docker build -t your-image-name . `
7. Then `docker run -d --restart always your-image-name`
