import os

_basedir = os.path.abspath(os.path.dirname(__file__))
_strings_ru = {
    'welcome': 'Здравствуйте!\nДля начала выберите язык',
    'welcome.say_me_language': 'Выберите язык ниже.',
    'language.russian': '🇷🇺 Русский',
    'language.uzbek': '🇺🇿 Узбекский',
    'welcome.user_name': 'Представьтесь. Отправте мне своё имя',
    'my_number': '📱 Мой номер',
    'welcome.phone_number': 'Какой у Вас номер?\nВы можете прислать текстом в формате <b>998 ** *** ** **</b> '
                            'или воспользоваться кнопкой "📱 Мой номер"',
    'welcome.company_name': 'Отправьте название Вашей компании',
    'welcome.registration_successfully': 'Отлично, вы зарегистрировались! Выберите пункт меню.',
    'main_menu.settings': '⚙ Настройки',
    'main_menu.choose_option': 'Выберите пункт меню.',
    'settings.change_user_name': 'Изменить имя 👤',
    'settings.send_name': 'Отправьте мне новое имя.',
    'settings.success_change_name': 'Имя изменено ✅',
    'settings.change_phone_number': 'Изменить номер 📱',
    'settings.send_phone_number': 'Отправьте новый номер телефона\nВы можете прислать текстом в формате '
                                  '<b>998 ** *** ** **</b> '
                                  'или воспользоваться кнопкой "📱 Мой номер"',
    'settings.success_change_phone_number': 'Номер телефона изменён ✅',
    'settings.change_company_name': '🏢 Сменить компанию',
    'settings.send_company_name': 'Отправьте новое название компании',
    'settings.success_change_company_name': 'Название компании изменено ✅',
    'settings.change_language': '🌐 Изменить язык',
    'settings.choose_language': 'Выберите язык ниже',
    'settings.success_change_language': 'Язык изменён ✅',
    'go_back': '⬅ Назад'
}
_strings_uz = {
'welcome': 'Здравствуйте!\nДля начала выберите языкUZ',
    'welcome.say_me_language': 'Выберите язык ниже.UZ',
    'language.russian': '🇷🇺 Русский',
    'language.uzbek': '🇺🇿 Узбекский',
    'welcome.user_name': 'Представьтесь. Отправте мне своё имяUZ',
    'my_number': '📱 Мой номерUZ',
    'welcome.phone_number': 'Какой у Вас номер?\nВы можете прислать текстом в формате <b>998 ** *** ** **</b> '
                            'или воспользоваться кнопкой "📱 Мой номер"UZ',
    'welcome.company_name': 'Отправьте название Вашей компанииUZ',
    'welcome.registration_successfully': 'Отлично, вы зарегистрировались! Выберите пункт меню.UZ',
    'main_menu.settings': '⚙ НастройкиUZ',
    'main_menu.choose_option': 'Выберите пункт меню.UZ',
    'settings.change_user_name': 'Изменить имя 👤UZ',
    'settings.send_name': 'Отправьте мне новое имя.UZ',
    'settings.success_change_name': 'Имя изменено ✅UZ',
    'settings.change_phone_number': 'Изменить номер 📱UZ',
    'settings.send_phone_number': 'Отправьте новый номер телефона\nВы можете прислать текстом в формате '
                                  '<b>998 ** *** ** **</b> '
                                  'или воспользоваться кнопкой "📱 Мой номер"UZ',
    'settings.success_change_phone_number': 'Номер телефона изменён ✅UZ',
    'settings.change_company_name': '🏢 Сменить компаниюUZ',
    'settings.send_company_name': 'Отправьте новое название компанииUZ',
    'settings.success_change_company_name': 'Название компании изменено ✅UZ',
    'settings.change_language': '🌐 Изменить языкUZ',
    'settings.choose_language': 'Выберите язык нижеUZ',
    'settings.success_change_language': 'Язык изменён ✅UZ',
    'go_back': '⬅ НазадUZ'
}


def get_string(key, language='ru'):
    if language == 'ru':
        return _strings_ru.get(key, 'no_string')
    elif language == 'uz':
        return _strings_uz.get(key, 'no_string')
    else:
        raise Exception('Invalid language')
