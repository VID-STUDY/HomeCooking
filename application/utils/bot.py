from application import telegram_bot
from application.resources import strings, keyboards
from application.core import userservice, dishservice
from telebot.types import Message


def check_auth(message: Message):
    return userservice.is_user_registered(message.from_user.id)


from application.bot.catalog import catalog_processor


def to_main_menu(chat_id, language, message_txt=None):
    # if message_text:
    #     main_menu_message = message_text
    # else:
    #     main_menu_message = strings.get_string('main_menu.choose_option', language)
    # main_menu_keyboard = keyboards.get_keyboard('main_menu', language)
    # telegram_bot.send_message(chat_id, main_menu_message, reply_markup=main_menu_keyboard)
    telegram_bot.send_chat_action(chat_id, 'typing')
    if not message_txt:
        catalog_message = strings.get_string('catalog.start', language)
    else:
        catalog_message = message_txt
    dishes = dishservice.get_all_dishes(sort_by_number=True)
    main_menu_keyboard = keyboards.get_main_menu_keyboard(dishes, language)
    telegram_bot.send_message(chat_id, catalog_message, reply_markup=main_menu_keyboard)
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, catalog_processor)
