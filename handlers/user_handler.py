import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f, and_f
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


import logging
from module.data_base import get_list_category, get_list_subcategory, get_list_card, info_card, create_table_users, \
    create_table_place, set_count_show_card
from config_data.config import Config, load_config
from keyboards.user_keyboards import keyboards_start_user, create_keyboard_list, keyboard_details, keyboard_full_text, \
    keyboard_full_text_1, keyboard_get_more
from filter.admin_filter import chek_superadmin

router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    category = State()



user_dict = {}


@router.message(or_f(and_f(CommandStart(), lambda message: not chek_superadmin(message.chat.id)),
                     and_f(lambda message: chek_superadmin(message.chat.id), F.text == '/user')))
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    logging.info(f'process_start_command_user: {message.chat.id}')
    create_table_users()
    create_table_place()
    await state.update_data(user_name=message.from_user.username)
    await message.answer(text=f'приветственное сообщение и предложение выбрать меню.',
                         reply_markup=keyboards_start_user())


@router.message(F.text == 'Выбрать место')
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    logging.info(f'process_start_command_user: {message.chat.id}')
    list_category = get_list_category()
    await message.answer(text=f'Выберите категорию места',
                         reply_markup=create_keyboard_list(list_name_button=list_category, str_callback='usercategory'))


async def show_card(callback: CallbackQuery, state: FSMContext, list_card) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    print('list_card', list_card)
    count_show = 3
    user_dict[callback.message.chat.id] = await state.get_data()
    count_card_show = user_dict[callback.message.chat.id]['count_card_show'] + count_show
    await state.update_data(count_card_show=count_card_show)
    for info_card in list_card[count_card_show - count_show:count_card_show]:
        media = []
        list_image = info_card[7].split(',')
        for image in list_image:
            print(image)
            media.append(InputMediaPhoto(media=image))
        await callback.message.answer_media_group(media=media)
        await callback.message.answer(text=f'<b>{info_card[1]}</b>\n'
                                           f'{info_card[2]}',
                                      reply_markup=keyboard_details(info_card[0]),
                                      parse_mode='html')
    if len(list_card) > count_card_show:
        await callback.message.answer(text='Не хватило мест?',
                                      reply_markup=keyboard_get_more())



@router.callback_query(F.data == 'get_more')
async def process_select_get_more(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_get_more: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    list_card = user_dict[callback.message.chat.id]['list_card']
    await show_card(callback=callback, state=state, list_card=list_card)


@router.callback_query(F.data.startswith('usercategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory = get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    print(list_subcategory)
    if list_subcategory[0] != 'none':
        await callback.message.answer(text=f'Выберите подкатегорию места',
                                      reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                        str_callback='usersubcategory'))
    else:
        await callback.message.answer(text=f'Подкатегорий у категории нет')
        await state.update_data(subcategory='none')
        user_dict[callback.message.chat.id] = await state.get_data()
        list_card = get_list_card(user_dict[callback.message.chat.id]['category'],
                                  user_dict[callback.message.chat.id]['subcategory'])
        await state.update_data(list_card=list_card)
        await state.update_data(count_card_show=0)
        await show_card(callback=callback, state=state, list_card=list_card)


@router.callback_query(F.data.startswith('usersubcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    user_dict[callback.message.chat.id] = await state.get_data()
    list_card = get_list_card(user_dict[callback.message.chat.id]['category'],
                              user_dict[callback.message.chat.id]['subcategory'])
    await state.update_data(list_card=list_card)
    await state.update_data(count_card_show=0)
    await show_card(callback=callback, state=state, list_card=list_card)




@router.callback_query(F.data.startswith('details_user:'))
async def process_details(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_details: {callback.message.chat.id}')
    id_card = callback.data.split(':')[1]
    card = info_card(int(id_card))
    count = card[10] + 1
    set_count_show_card(count, id_card)
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
