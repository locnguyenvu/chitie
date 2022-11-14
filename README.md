# 🤖chitie

Chitie stands for `chi tiết` & `chi tiêu` in Vietnamese it means detail on your expenses. 

This is a bot for the Telegram messaging app using their bot platform. It helps you to keep track of your expenses, supporting your financial planning. 
It is simple, like sending a message to a friend on Telegram. No extra application is installed, but it can work on multiple platforms, desktops, and mobiles (like Telegram 😊)

Your data is secured on your server, which is very flexible as you can write your SQL to build reports.

[# View demo](#demo)


## Build with

* ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
* ![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
* ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
* ![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## Setup on your server
### Prerequisites

To host this bot on your own, you need a few things.
* Server to run the bot on [^1]
* A domain name with `HTTPS` enabled [^2]
* A bot token, which you get from registering a new bot to the [@BotFather](https://t.me/BotFather)

On your server:
* Python3
* PostgreSQL
* Nginx


### Configuration
Link your domain to the bot

> Once you have chosen a bot, send the /setdomain command to @Botfather to link your website's domain to the bot. Then configure your widget below and embed the code on your website.


Set following environment variable on the running application session, or create an `.env` file in the root directory of the application


| Property                | Example                                          | Description                                                  |
|-------------------------|--------------------------------------------------|--------------------------------------------------------------|
| DB_URL                  | postgresql://user:password@localhost:5432/chitie | PostgreSQL connection url                                    |
| SECRET_KEY              | complex-random-string                            | A secret key that will be used for securely signing the session cookie and can be used for any other security related needs by extensions or your application|
| SERVER_NAME             | chitie.yourdomain                                | Your web domain                                              |
| TELEGRAM_SECRET         | telegram-secret-string                           | The secret string gotten from @BotFather when create new bot |
| TELEGRAM_WEBHOOK_SECRET | some-secret-string                               | To generate a secure url for webhook endpoint                |

### Initial setup

Install dependencies

```
pip install -e '.[production]'
```

Init database schema

```
alembic upgrade head
```

### Run application
```
uwsgi --enable-threads --socket 0.0.0.0:5000 --protocol http -w wsgi:webserver
```

## Usage

### Expense loggin

Send a message in the configured group with the format.

```
<expense subject: string> <amount: float><transaction_type:enum(‘’, ‘c’)>
```

There are two types of transactions – debit & credit. In a logging message, if the transaction type is empty, the default value is debit, and if the amount pattern is followed with a c letter, the transaction type is credit.

Example:

Debit expense:

![Debit expense](https://locnguyenvu.github.io/chitie/assets/debit_expense.png)

Credit expense:

![Credit expense](https://locnguyenvu.github.io/chitie/assets/credit_expense.png)

### Commands

| Command | Description |
| --- | --- |
|/category| List all categories|
|/review `<month-year>`| Summary all expenses in the given time range. The default time range is the current month if not given|

## Demo
Init the expense chat group

![Init the expense chat group](https://locnguyenvu.github.io/chitie/assets/setup.gif)

Logging your expenses by sending a message

![Logging your expenses by sending a message](https://locnguyenvu.github.io/chitie/assets/logging.gif)


Review your expense in month

![Review your expense in month](https://locnguyenvu.github.io/chitie/assets/review.gif)

## References
[^1]: I use [Digital Ocean](https://m.do.co/c/13d83e9b5d60) with $6/

[^2]: I use free SSL of [Cloudflare](https://www.cloudflare.com/ssl/)
