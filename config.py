import os

BOT_API = '6013400790:AAGr7s2KQIFPBkubuvkDJlHqg5Vm5UzOgSE' #deploy

# BOT_API = '6065135429:AAHQlkhjys7E2XpLhxHaC8jk9xzrQyISnZk'

APP_HOST = '0.0.0.0'  # Default value
APP_PORT = '8444'  # Default value

# Webhook configuration
APP_NAME = 'promocodes-cisn.onrender.com'
WEB_HOOK_URL = f'https://{APP_NAME}/{BOT_API}'


# Database configuration
DB_USERNAME = 'Your value here'
DB_PASSWORD = 'Your value here'
HOST_NAME = 'Your value here'
DB_NAME = 'Your value here'

DB_PORT = '3306'

KEY = 'you-will-never-guess'
basedir = os.path.abspath(os.path.dirname(__file__))


# DATABASE_URI = 'mysql://' + f'{DB_USERNAME}:{DB_PASSWORD}@{HOST_NAME}:{DB_PORT}/{DB_NAME}'

# test db
# DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'main.db')
DATABASE_URI = 'postgresql://promo:kE5Cr8JLQGtDkc14UqDGKgIbZAnQod7o@dpg-ch7qsf02qv2864o96bfg-a/promo'  # deploy
# DATABASE_URI = 'postgresql://promo:kE5Cr8JLQGtDkc14UqDGKgIbZAnQod7o@dpg-ch7qsf02qv2864o96bfg-a.frankfurt-postgres.render.com/promo'  # test

# app config
DEBUG = False  # set True if you want to run it on your pc

ADMIN_USERNAME = 'chikundant'


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or KEY
