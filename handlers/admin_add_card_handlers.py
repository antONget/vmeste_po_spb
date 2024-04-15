from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state


from config_data.config import Config, load_config
from keyboards.admin_add_card_keyboards import create_keyboard_list, keyboard_add_subcategory, keyboards_continue_image,\
    keyboard_add_instagram, keyboard_details, keyboard_full_text, keyboard_full_text_1
from module.data_base import get_list_category, get_list_subcategory, add_place, add_category
from filter.admin_filter import chek_superadmin


import logging

router = Router()
config: Config = load_config()


class Admin(StatesGroup):
    category_card = State()
    subcategory_card = State()
    image_card = State()
    title_card = State()
    short_card = State()
    long_card = State()
    address_card = State()
    yandex_card = State()
    instagram_card = State()

user_dict_admin = {}


@router.message(F.text == '➕ Добавить карточку', lambda message: chek_superadmin(message.chat.id))
async def process_add_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_add_card: {message.chat.id}')
    list_category = get_list_category()
    await message.answer(text=f'Введите категорию места или выберите из ранее добавленных',
                         reply_markup=create_keyboard_list(list_name_button=list_category, str_callback='category'))
    await state.update_data(image_id_list_image=[])
    await state.set_state(Admin.category_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.category_card))
async def process_add_category_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_add_category_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(category_card=message.text)
    await message.answer(text=f'Добавить подкатегорию?',
                         reply_markup=keyboard_add_subcategory())


@router.callback_query(F.data.startswith('category'), lambda message: chek_superadmin(message.message.chat.id))
async def process_add_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_category_card: {callback.message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(category_card=callback.data.split(':')[1])
    await callback.message.answer(text=f'Добавить подкатегорию?',
                                  reply_markup=keyboard_add_subcategory())


@router.callback_query(F.data == 'yes_subcategory', lambda message: chek_superadmin(message.message.chat.id))
async def process_add_subcategory_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_subcategory_card: {callback.message.chat.id}')
    user_dict_admin[callback.message.chat.id] = await state.update_data()
    list_subcategory = get_list_subcategory(user_dict_admin[callback.message.chat.id]["category_card"])
    await callback.message.edit_text(text=f'Введите название подкатегории для категории '
                                          f'{user_dict_admin[callback.message.chat.id]["category_card"]} или выберите'
                                          f' из списка',
                                     reply_markup=create_keyboard_list(list_name_button=list_subcategory,
                                                                       str_callback='subcategory'))
    await state.set_state(Admin.subcategory_card)


@router.callback_query(F.data == 'no_subcategory', lambda message: chek_superadmin(message.message.chat.id))
async def process_add_subcategory_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_nosubcategory_card: {callback.message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(subcategory_card='none')
    await callback.message.answer(text=f'Пришлите фотографии заведения')
    await state.set_state(Admin.image_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.subcategory_card))
async def process_add_category_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_add_category_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(subcategory_card=message.text)
    await message.answer(text=f'Пришлите фотографии заведения')
    await state.set_state(Admin.image_card)


@router.callback_query(F.data.startswith('subcategory'), lambda message: chek_superadmin(message.message.chat.id))
async def process_add_category_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_category_card: {callback.message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(subcategory_card=callback.data.split(':')[1])
    await callback.message.answer(text=f'Пришлите фотографии заведения')
    await state.set_state(Admin.image_card)


@router.message(F.photo, StateFilter(Admin.image_card))
async def get_image_card(message: Message, state: FSMContext) -> None:
    logging.info(f'get_image_card: {message.chat.id}')
    image_id = message.photo[-1].file_id
    user_dict_admin[message.chat.id] = await state.get_data()
    if 'image_id_list_image' in user_dict_admin[message.chat.id].keys():
        image_id_list_image = user_dict_admin[message.chat.id]['image_id_list_image']
        image_id_list_image.append(image_id)
        await state.update_data(image_id_list_image=image_id_list_image)
    else:
        await state.update_data(image_id_list_image=[image_id])
    await message.answer(text='Добавьте еще фото или нажмите «Продолжить».',
                         reply_markup=keyboards_continue_image())


@router.callback_query(F.data == 'continue_image', lambda message: chek_superadmin(message.message.chat.id))
async def process_continue_image(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_continue_image: {callback.message.chat.id}')
    await callback.message.answer(text='Введите название места')
    await state.set_state(Admin.title_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.title_card))
async def process_get_title_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_title_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(title_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите короткое описание')
    await state.set_state(Admin.short_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.short_card))
async def process_get_short_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_short_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(short_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите полное описание')
    await state.set_state(Admin.long_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.long_card))
async def process_get_long_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_long_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(long_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите адрес')
    await state.set_state(Admin.address_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.address_card))
async def process_get_address_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_address_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(address_card=message.text.replace('"', ''))
    await message.answer(text=f'Пришлите ссылку на место в яндекс картах')
    await state.set_state(Admin.yandex_card)


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.yandex_card))
async def process_get_yandex_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_yandex_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(yandex_card=message.text)
    await message.answer(text=f'Есть ссылка на инстаграм?',
                         reply_markup=keyboard_add_instagram())


@router.callback_query(F.data == 'yes_instagram', lambda message: chek_superadmin(message.message.chat.id))
async def process_add_instagram_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_instagram_card: {callback.message.chat.id}')
    await callback.message.answer(text=f'Пришлите ссылку на инстаграм')
    await state.set_state(Admin.instagram_card)

@router.callback_query(F.data == 'no_instagram', lambda message: chek_superadmin(message.message.chat.id))
async def process_add_noinstagram_card(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_noinstagram_card: {callback.message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(instagram_card='none')
    user_dict_admin[callback.message.chat.id] = await state.update_data()
    add_place(title=user_dict_admin[callback.message.chat.id]["title_card"],
              short_description=user_dict_admin[callback.message.chat.id]["short_card"],
              long_description=user_dict_admin[callback.message.chat.id]["long_card"],
              address=user_dict_admin[callback.message.chat.id]["address_card"],
              instagram=user_dict_admin[callback.message.chat.id]["instagram_card"],
              yandex_map=user_dict_admin[callback.message.chat.id]["yandex_card"],
              list_image=','.join(user_dict_admin[callback.message.chat.id]["image_id_list_image"]),
              category=user_dict_admin[callback.message.chat.id]["category_card"],
              sub_category=user_dict_admin[callback.message.chat.id]["subcategory_card"],
              count_link=0)
    # add_category(category=user_dict_admin[callback.message.chat.id]["category_card"])

    media = []
    list_image = user_dict_admin[callback.message.chat.id]["image_id_list_image"]
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text=f'<b>{user_dict_admin[callback.message.chat.id]["title_card"]}</b>\n'
                                       f'{user_dict_admin[callback.message.chat.id]["short_card"]}',
                                  reply_markup=keyboard_details(),
                                  parse_mode='html')


@router.message(F.text, lambda message: chek_superadmin(message.chat.id), StateFilter(Admin.instagram_card))
async def process_get_instagram_card(message: Message, state: FSMContext) -> None:
    logging.info(f'process_get_instagram_card: {message.chat.id}')
    await state.set_state(default_state)
    await state.update_data(instagram_card=message.text)
    user_dict_admin[message.chat.id] = await state.update_data()

    add_place(title=user_dict_admin[message.chat.id]["title_card"],
              short_description=user_dict_admin[message.chat.id]["short_card"],
              long_description=user_dict_admin[message.chat.id]["long_card"],
              address=user_dict_admin[message.chat.id]["address_card"],
              instagram=message.text,
              yandex_map=user_dict_admin[message.chat.id]["yandex_card"],
              list_image=','.join(user_dict_admin[message.chat.id]["image_id_list_image"]),
              category=user_dict_admin[message.chat.id]["category_card"],
              sub_category=user_dict_admin[message.chat.id]["subcategory_card"],
              count_link=0)
    # add_category(category=user_dict_admin[message.chat.id]["category_card"])

    media = []
    list_image = user_dict_admin[message.chat.id]["image_id_list_image"]
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await message.answer_media_group(media=media)
    await message.answer(text=f'<b>{user_dict_admin[message.chat.id]["title_card"]}</b>\n'
                              f'{user_dict_admin[message.chat.id]["short_card"]}',
                         reply_markup=keyboard_details(),
                         parse_mode='html')


@router.callback_query(F.data == 'details', lambda message: chek_superadmin(message.message.chat.id))
async def process_details(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_details: {callback.message.chat.id}')
    user_dict_admin[callback.message.chat.id] = await state.update_data()
    media = []
    list_image = user_dict_admin[callback.message.chat.id]["image_id_list_image"]
    for image in list_image:
        media.append(InputMediaPhoto(media=image))
    await callback.message.answer_media_group(media=media)
    if user_dict_admin[callback.message.chat.id]['instagram_card'] != 'none':
        await callback.message.answer(text=f'<b>{user_dict_admin[callback.message.chat.id]["title_card"]}</b>\n'
                                           f'{user_dict_admin[callback.message.chat.id]["long_card"]}\n'
                                           f'<i>{user_dict_admin[callback.message.chat.id]["address_card"]}</i>',
                                      reply_markup=keyboard_full_text(user_dict_admin[callback.message.chat.id]["yandex_card"],
                                                                      user_dict_admin[callback.message.chat.id]["instagram_card"]),
                                      parse_mode='html')
    else:
        await callback.message.answer(text=f'<b>{user_dict_admin[callback.message.chat.id]["title_card"]}</b>\n'
                                           f'{user_dict_admin[callback.message.chat.id]["long_card"]}\n'
                                           f'<i>{user_dict_admin[callback.message.chat.id]["address_card"]}</i>',
                                      reply_markup=keyboard_full_text_1(user_dict_admin[callback.message.chat.id]["yandex_card"]),
                                      parse_mode='html')
