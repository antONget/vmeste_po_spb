from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


from config_data.config import Config, load_config
from keyboards.admin_delete_card_keyboard import create_keyboard_list, keyboard_confirm_delete_card
from module.data_base import get_list_category, get_list_subcategory, get_list_card, delete_user
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
                         reply_markup=create_keyboard_list(list_name_button=list_category, str_callback='categorydelete'))
    await state.set_state(Admin.category_card)


@router.callback_query(F.data.startswith('categorydelete'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    list_subcategory = get_list_subcategory(callback.data.split(':')[1])
    await state.update_data(category=callback.data.split(':')[1])
    print(list_subcategory)
    if list_subcategory[0] != 'none':
        await callback.message.answer(text=f'Выберите подкатегорию места для удаления',
                                      reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                        str_callback='subcategorydelete'))
    else:
        list_card = get_list_card(category=callback.data.split(':')[1], subcategory='none')
        list_title_card = []
        for card in list_card:
            list_title_card.append(card[1])
        create_keyboard_list(list_name_button=list_title_card, str_callback='title_card')


@router.callback_query(F.data.startswith('subcategorydelete'))
async def process_select_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_category_card: {callback.message.chat.id}')
    await state.update_data(subcategory=callback.data.split(':')[1])
    user_dict_admin[callback.message.chat.id] = await state.get_data()
    list_card = get_list_card(user_dict_admin[callback.message.chat.id]['category'],
                              user_dict_admin[callback.message.chat.id]['subcategory'])
    list_title_card = []
    for card in list_card:
        list_title_card.append(card[1])
    create_keyboard_list(list_name_button=list_title_card, str_callback='title_card')


@router.callback_query(F.data.startswith('title_card'))
async def process_select_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_select_title_card: {callback.message.chat.id}')
    await state.update_data(title=callback.data.split(":")[1])
    await callback.message.answer(text=f'Вы точно хотите удалить <b>{callback.data.split(":")[1]}</b>',
                                  reply_markup=keyboard_confirm_delete_card())


@router.callback_query(F.data == 'yes_delete')
async def process_yes_delete_title_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_yes_delete_title_card: {callback.message.chat.id}')
    user_dict_admin[callback.message.chat.id] = await state.get_data()
    delete_user(user_dict_admin[callback.message.chat.id]['title'])
    await callback.message.answer(text=f'Заведение {user_dict_admin[callback.message.chat.id]["title"]} успешно'
                                       f'удалено')
