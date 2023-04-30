import flask
import telebot
import config

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


bot = telebot.TeleBot(config.BOT_API)
logger = telebot.logger
app = flask.Flask(__name__)
engine = create_engine(config.DATABASE_URI)

Session = sessionmaker(bind=engine)
session = Session()

app.config.from_object(config.Config)

app.debug = config.DEBUG

from project import routes
