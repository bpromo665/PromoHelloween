from project import bot, app
import config
import flask
import telebot
from project.models import Base
from project import engine
import os


if app.debug is True:
    bot.remove_webhook()
    Base.metadata.create_all(engine)
    bot.polling()
else:
    Base.metadata.create_all(engine)


    @app.route('/' + config.BOT_API, methods=['POST'])
    def get_message():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            print('[GOT UPDATES]')
            bot.process_new_updates([update])
            return 'ok', 200
        else:
            flask.abort(403)


    @app.route('/')
    def webhook():
        bot.delete_webhook()
        bot.set_webhook(url=config.WEB_HOOK_URL)
        return '!', 200


    if __name__ == '__main__':
        app.run(host=config.APP_HOST, port=int(os.environ.get('PORT', 5000)))
