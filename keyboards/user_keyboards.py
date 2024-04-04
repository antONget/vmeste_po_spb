from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import validators

def keyboards_start_user():
    logging.info("keyboards_start_user")
    button_1 = KeyboardButton(text='Выбрать место')
    button_2 = KeyboardButton(text='Задать вопрос')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2],],
        resize_keyboard=True
    )
    return keyboard



def create_keyboard_list(list_name_button, str_callback):
    logging.info("create_keyboard_list")
    kb_builder = InlineKeyboardBuilder()
    list_button = []
    for i, value in enumerate(list_name_button):
        list_button.append(InlineKeyboardButton(text=value, callback_data=f'{str_callback}:{value}'))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*list_button, width=1)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def keyboard_details(id_card):
    logging.info("keyboard_details")
    button_1 = InlineKeyboardButton(text='Узнать больше',  callback_data=f'details_user:{id_card}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboard_get_more():
    logging.info("keyboard_get_more")
    button_1 = InlineKeyboardButton(text='Получить еще',  callback_data=f'get_more')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboard_full_text(yandex, instagram):
    logging.info("keyboard_full_text")
    button_1 = ''
    button_2 = ''
    if validators.url(yandex):
        button_1 = InlineKeyboardButton(text='Яндекс Карты',  url=f'{yandex}')
    else:
        button_1 = InlineKeyboardButton(text='Яндекс Карты', callback_data=' ')
    if validators.url(instagram):
        button_2 = InlineKeyboardButton(text='Ссылка на проект',  url=f'{instagram}')
    else:
        button_2 = InlineKeyboardButton(text='Ссылка на проект', callback_data=' ')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]], )
    return keyboard


def keyboard_full_text_1(yandex):
    logging.info("keyboard_full_text_1")
    button_1 = ''
    if validators.url(yandex):
        button_1 = InlineKeyboardButton(text='Яндекс Карты',  url=f'{yandex}')
    else:
        button_1 = InlineKeyboardButton(text='Яндекс Карты', callback_data=' ')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard