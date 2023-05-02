from project import bot
from telebot import types

from project.models import User
from project import session

import project.modules.admin as admin
from project.models import PromoCode


def is_registered(telegram_id):
    if session.query(User).filter_by(telegram_id=str(telegram_id)).first():
        return True
    return False


def welcome_message(message: types.Message):
    if not is_registered(message.from_user.id):
        bot.send_message(message.chat.id, f'Привіт {message.from_user.first_name}!😊\n\n'
                                          f'Щоб почати користуватись нашим ботом потрібно зареєструватись!\n\n')

    handle_start(message)


def handle_start(message: types.Message):
    if is_registered(message.from_user.id):
        handle_promo_code(message)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        reg_button = types.KeyboardButton(text="Поділитися номером", request_contact=True)
        markup.add(reg_button)
        bot.send_message(message.chat.id, 'Будь ласка, надішліть Ваш контактний номер телефону, натиснувши кнопку внизу 👇',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_the_phone)


@bot.message_handler(content_types=['contact'])
def get_the_phone(message: types.Message):
    try:
        user = User(telegram_id=message.from_user.id, username=message.from_user.username)
        user.phone_number = message.contact.phone_number
        session.add(user)
        session.commit()
        bot.send_message(message.chat.id, 'Дякуємо! Ви були успішно зареєстровані!🔑')
        handle_promo_code(message)
    except ValueError as value_error:
        bot.send_message(message.chat.id, value_error)
        handle_start(message)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Здається щось пішло не так! Спробуйте ще раз')
        handle_start(message)


def handle_promo_code(message: types.Message):
    if message.text == '/admin':
        message.text = ''
        admin.handle_admin(message)
    else:
        bot.send_message(message.chat.id, 'Відправте нам промокод! ⬇️')
        bot.register_next_step_handler(message, check_promo_code)


def check_promo_code(message: types.Message):
    try:
        code = session.query(PromoCode).filter_by(code=str(message.text)).filter(PromoCode.prize.isnot(None)).first()
        user = session.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
        admins = session.query(User).filter(User.is_admin.is_(True))

        if code.is_used:
            bot.send_message(message.chat.id, 'Вибачте! Цей промокод більше не дійсний!')
        else:
            bot.send_message(message.chat.id, f"Наші вітання! 🥳\n\n"
                                              f"Ви виграли {code.prize} 🎁\n\n"
                                              f"Ми передали інформацію нашому менеджеру! Найближчим часом він з вами зв'яжеться")
            code.is_used = True
            session.commit()
            for admin in admins:
                bot.send_message(chat_id=admin.telegram_id, text=f'Юзер @{user.username} виграв приз!\n'
                                                                         f'Номер телефону: {user.phone_number}\n\n'
                                                                         f'Виграш:\n'
                                                                         f'Код: {code.code}\n'
                                                                         f'Приз: {code.prize}')
    except Exception as e:
        print(e)
        # bot.send_message(message.chat.id, 'Здається ви ввели неправильний промокод!❌')
    handle_promo_code(message)
