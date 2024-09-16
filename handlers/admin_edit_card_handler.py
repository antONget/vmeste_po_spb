from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


from config_data.config import Config, load_config
from keyboards.admin_edit_card_keyboard import create_keyboard_list, keyboard_details_edit, keyboards_edit_attribute, \
    keyboard_full_text, keyboard_full_text_1
from keyboards.admin_main_keyboards import keyboards_start_admin
from module.data_base import get_list_category, get_list_subcategory, get_list_card, \
    info_card, set_attribute_card, set_position_card, set_position_category
from filter.admin_filter import chek_superadmin


import logging

router = Router()
config: Config = load_config()


class Admin(StatesGroup):
    update_attribute = State()


user_dict_admin = {}


@router.message(F.text == '📝 Редактировать карточку', lambda message: chek_superadmin(message.chat.id))
async def process_edit_card(message: Message) -> None:
    logging.info(f'process_edit_card: {message.chat.id}')
    list_category: list = get_list_category()
    await message.answer(text=f'Выберите категорию заведение, из которого нужно изменить',
                         reply_markup=create_keyboard_list(list_name_button=list_category,
                                                           str_callback='editcategory'))


@router.callback_query(F.data == 'top_category')
async def process_top_category(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_top_category: {callback.message.chat.id} {callback.data}')
    data = await state.get_data()
    set_position_category(category=data['category'])
    await callback.answer(text='Позиция категории обновлена', show_alert=True)


@router.callback_query(F.data.startswith('editcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory: list = get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    print(list_subcategory)
    if list_subcategory[0] != 'none':
        await callback.message.answer(text=f'Выберите подкатегорию места для редактирования',
                                      reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                        str_callback='editsubcategory'))
    else:
        list_card: list = get_list_card(category=callback.data.split(':')[1],
                                        subcategory='none')
        list_title_card = []
        list_id_card = []
        for card in list_card:
            list_title_card.append(card[1])
            list_id_card.append(card[0])
        await callback.message.answer(text='Выберите заведение для редактирования',
                                      reply_markup=
                                      create_keyboard_list(list_name_button=list_title_card,
                                                           str_callback='edittitle_card',
                                                           list_id_button=list_id_card))


@router.callback_query(F.data.startswith('editsubcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    user_dict_admin[callback.message.chat.id] = await state.get_data()
    list_card: list = get_list_card(user_dict_admin[callback.message.chat.id]['category'],
                                    user_dict_admin[callback.message.chat.id]['subcategory'])
    list_title_card = []
    list_id_card = []
    for card in list_card:
        list_title_card.append(card[1])
        list_id_card.append(card[0])
    await callback.message.answer(text='Выберите заведение для редактирования',
                                  reply_markup=
                                  create_keyboard_list(list_name_button=list_title_card,
                                                       str_callback='edittitle_card',
                                                       list_id_button=list_id_card))


@router.callback_query(F.data.startswith('edittitle_card'))
async def process_select_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_title_card: {callback.message.chat.id}')
    await state.update_data(title=callback.data.split(":")[1])
    # card = info_card_title(title=callback.data.split(":")[1])
    card: list = info_card(int(callback.data.split(":")[1]))
    await state.update_data(id_card=card[0])
    media = []
    list_image: list = card[7].split(',')
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text=f'<b>{card[1]}</b>\n'
                                       f'{card[2]}',
                                  reply_markup=keyboard_details_edit(card[0]),
                                  parse_mode='html')
    await callback.message.answer(text='Выберите поля для редактирования',
                                  reply_markup=keyboards_edit_attribute())


@router.callback_query(F.data.startswith('details_edit:'))
async def process_details(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_details: {callback.message.chat.id}')
    id_card = callback.data.split(':')[1]
    card = info_card(int(id_card))
    if card[5] != 'none':
        await callback.message.edit_text(text=f'<b>{card[1]}</b>\n'
                                              f'{card[3]}\n'
                                              f'<i>{card[4]}</i>',
                                         reply_markup=keyboard_full_text(card[6], card[5]),
                                         parse_mode='html')
    else:
        await callback.message.edit_text(text=f'<b>{card[1]}</b>\n'
                                              f'{card[3]}\n'
                                              f'<i>{card[4]}</i>',
                                         reply_markup=keyboard_full_text_1(card[6]),
                                         parse_mode='html')


@router.message(F.text == 'Главное меню', lambda message: chek_superadmin(message.chat.id))
async def process_back_menu(message: Message, state: FSMContext) -> None:
    logging.info(f'process_back_menu: {message.chat.id}')
    await message.answer(text='Выберите раздел',
                         reply_markup=keyboards_start_admin())


@router.message(lambda message: message.text in ['Название', 'Короткое описание', 'Полное описание', 'Адрес',
                                                 'Категория', 'Поднять в TOP'],
                lambda message: chek_superadmin(message.chat.id))
async def process_update_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_update_card: {message.chat.id}')
    await state.set_state(Admin.update_attribute)
    await state.update_data(attribute=message.text)
    if message.text == 'Название':
        await message.answer(text='Пришлите новое название:')
    elif message.text == 'Категория':
        await message.answer(text='Пришлите новое название категории:')
    elif message.text == 'Короткое описание':
        await message.answer(text='Пришлите новое короткое описание')
    elif message.text == 'Полное описание':
        await message.answer(text='Пришлите новое полное описание')
    elif message.text == 'Адрес':
        await message.answer(text='Пришлите новый адрес')
    elif message.text == 'Поднять в TOP':
        user_dict_admin[message.chat.id] = await state.get_data()
        if 'subcategory' in user_dict_admin[message.chat.id].keys():
            set_position_card(category=user_dict_admin[message.chat.id]['category'],
                              subcategory='None',
                              id_card=int(user_dict_admin[message.chat.id]['id_card']))
        else:
            set_position_card(category=user_dict_admin[message.chat.id]['category'],
                              subcategory=user_dict_admin[message.chat.id]['subcategory'],
                              id_card=int(user_dict_admin[message.chat.id]['id_card']))
        await message.answer(text='Позиция карточки обновлена')
    # print(message.text)


@router.message(F.text, StateFilter(Admin.update_attribute), lambda message: chek_superadmin(message.chat.id))
async def process_update_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_update_card: {message.chat.id}')
    user_dict_admin[message.chat.id] = await state.get_data()
    attribute = user_dict_admin[message.chat.id]['attribute']
    # print(attribute, user_dict_admin[message.chat.id]['title'])
    if attribute == 'Название':
        set_attribute_card(attribute='title',
                           set_attribute=message.text,
                           id_card=int(user_dict_admin[message.chat.id]['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Категория':
        set_attribute_card(attribute='category',
                           set_attribute=message.text,
                           id_card=int(user_dict_admin[message.chat.id]['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Короткое описание':
        set_attribute_card(attribute='short_description',
                           set_attribute=message.text,
                           id_card=int(user_dict_admin[message.chat.id]['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Полное описание':
        set_attribute_card(attribute='long_description',
                           set_attribute=message.text,
                           id_card=int(user_dict_admin[message.chat.id]['id_card']))
        await message.answer(text='Поле обновлено')
    elif attribute == 'Адрес':
        set_attribute_card(attribute='address',
                           set_attribute=message.text,
                           id_card=int(user_dict_admin[message.chat.id]['id_card']))
        await message.answer(text='Поле обновлено')
    # elif attribute == 'Поднять в TOP':
    #     set_attribute_card(attribute='position',
    #                        set_attribute=int(message.text),
    #                        id_card=int(user_dict_admin[message.chat.id]['id_card']))
    #     await message.answer(text='Позиция карточки обновлена')
