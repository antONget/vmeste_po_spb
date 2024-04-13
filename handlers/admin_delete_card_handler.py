from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


from config_data.config import Config, load_config
from keyboards.admin_delete_card_keyboard import create_keyboard_list, keyboard_confirm_delete_card
from module.data_base import get_list_category, get_list_subcategory, get_list_card, delete_card, info_card
from filter.admin_filter import chek_superadmin


import logging

router = Router()
config: Config = load_config()


class Admin(StatesGroup):
    category_card = State()


user_dict_admin = {}


@router.message(F.text == '❌ Удалить карточку', lambda message: chek_superadmin(message.chat.id))
async def process_add_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_add_card: {message.chat.id}')
    list_category = get_list_category()
    await message.answer(text=f'Выберите категорию заведение, из которого нужно удалить',
                         reply_markup=create_keyboard_list(list_name_button=list_category, str_callback='deletecategory'))


@router.callback_query(F.data.startswith('deletecategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory = get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    print(list_subcategory)
    if list_subcategory[0] != 'none':
        await callback.message.answer(text=f'Выберите подкатегорию места для удаления',
                                      reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                        str_callback='deletesubcategory'))
    else:
        list_card = get_list_card(category=callback.data.split(':')[1], subcategory='none')
        list_title_card = []
        list_id_card = []
        for card in list_card:
            list_title_card.append(card[1])
            list_id_card.append(card[0])
        await callback.message.answer(text='Выберите заведение для удаления',
                                      reply_markup=
                                      create_keyboard_list(list_name_button=list_title_card, str_callback='title_card',
                                                           list_id_button=list_id_card))


@router.callback_query(F.data.startswith('deletesubcategory'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    user_dict_admin[callback.message.chat.id] = await state.get_data()
    list_card = get_list_card(user_dict_admin[callback.message.chat.id]['category'],
                              user_dict_admin[callback.message.chat.id]['subcategory'])
    list_title_card = []
    list_id_card = []
    for card in list_card:
        list_title_card.append(card[1])
        list_id_card.append(card[0])
    await callback.message.answer(text='Выберите заведение для удаления',
                                  reply_markup=
                                  create_keyboard_list(list_name_button=list_title_card, str_callback='title_card',
                                                       list_id_button=list_id_card))


@router.callback_query(F.data.startswith('title_card'))
async def process_select_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_title_card: {callback.message.chat.id}')
    await state.update_data(id_title=callback.data.split(":")[1])
    title_card = info_card(int(callback.data.split(":")[1]))[1]
    await callback.message.answer(text=f'Вы точно хотите удалить <b>{title_card}</b>',
                                  reply_markup=keyboard_confirm_delete_card(),
                                  parse_mode='html')


@router.callback_query(F.data == 'yes_delete')
async def process_yes_delete_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_yes_delete_title_card: {callback.message.chat.id}')
    user_dict_admin[callback.message.chat.id] = await state.get_data()
    title_card = info_card(int(user_dict_admin[callback.message.chat.id]['id_title']))[1]
    delete_card(user_dict_admin[callback.message.chat.id]['id_title'])
    await callback.message.answer(text=f'Заведение {title_card} успешно удалено')

@router.callback_query(F.data == 'no_delete')
async def process_yes_delete_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_yes_delete_title_card: {callback.message.chat.id}')
    await callback.message.answer(text='Удаление отменено')