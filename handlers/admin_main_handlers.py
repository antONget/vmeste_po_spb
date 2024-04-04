import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from config_data.config import Config, load_config
from keyboards.admin_main_keyboards import keyboards_start_admin
from module.data_base import create_table_users, create_table_place, get_list_card_stat
from filter.admin_filter import chek_superadmin

import logging

router = Router()
config: Config = load_config()


class User(StatesGroup):
    article = State()


@router.message(CommandStart(), lambda message: chek_superadmin(message.chat.id))
async def process_start_command_user(message: Message, state: FSMContext) -> None:
    logging.info(f'process_start_command_user: {message.chat.id}')
    create_table_users()
    create_table_place()
    await state.update_data(user_name=message.from_user.username)
    await message.answer(text=f'Здравствуй, {message.from_user.first_name}!'
                              f'Вы являетесь супер админом проекта и вам доступен расширенный функционал для'
                              f' правки контента',
                         reply_markup=keyboards_start_admin())


@router.message(F.text == '📋 Статистика', lambda message: chek_superadmin(message.chat.id))
async def process_get_stat(message: Message, state: FSMContext) -> None:
    logging.info(f'process_add_card: {message.chat.id}')
    stat = get_list_card_stat()
    text = ''
    for card in stat:
        text += f'<b>{card[0]}:</b> {card[1]}\n'
    await message.answer(text=f'Статистика:\n'
                              f'{text}',
                         parse_mode='html')
