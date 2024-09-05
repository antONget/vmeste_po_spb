from aiogram.types import Message

import sqlite3
from config_data.config import Config, load_config
import logging


config: Config = load_config()
db = sqlite3.connect('navigation.db', check_same_thread=False, isolation_level='EXCLUSIVE')
# sql = db.cursor()


# СОЗДАНИЕ ТАБЛИЦ
def create_table_users() -> None:
    """
    Создание таблицы верифицированных пользователей
    :return: None
    """
    logging.info("table_users")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER,
            username TEXT,
            is_admin INTEGER,
            operator INTEGER
        )""")
        db.commit()


def create_table_place() -> None:
    logging.info("create_table_place")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS places(
            id INTEGER PRIMARY KEY,
            title TEXT,
            short_description TEXT,
            long_description TEXT,
            address TEXT,
            instagram TEXT,
            yandex_map TEXT,
            list_image TEXT,
            category TEXT,
            sub_category TEXT,
            count_link INTEGER,
            position INTEGER DEFAULT -1
        )""")
        db.commit()


def create_table_category() -> None:
    logging.info("create_table_place")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS category(
            id INTEGER PRIMARY KEY,
            category TEXT UNIQUE,
            position INTEGER DEFAULT 0
        )""")
        db.commit()


# ЗАВЕДЕНИЯ/МЕСТА
def add_place(title, short_description, long_description, address, instagram, yandex_map, list_image, category,
              sub_category, count_link) -> None:
    logging.info(f'add_place')
    # print(title, short_description, long_description, address, instagram, yandex_map, list_image, category, sub_category, count_link)
    with db:
        sql = db.cursor()
        sql.execute(f'INSERT INTO places (title, short_description, long_description, address, instagram, yandex_map,'
                    f' list_image, category, sub_category, count_link) '
                    f'VALUES ("{title}", "{short_description}", "{long_description}", "{address}", "{instagram}",'
                    f' "{yandex_map}", "{list_image}", "{category}", "{sub_category}", "{count_link}")')
        db.commit()


def add_category(category) -> None:
    logging.info(f'add_category')
    with db:
        sql = db.cursor()

        sql.execute(f'INSERT INTO category (category, position) '
                    f'VALUES ("{category}")')
        db.commit()


def get_list_category():
    """
    Получаем список категорий
    :return:
    """
    logging.info(f'get_list_category')
    with db:
        sql = db.cursor()
        list_category = [category[0] for category in sql.execute('SELECT category FROM places ORDER BY pos_cat').fetchall()]
        list_category_uniq = []
        for category in list_category:
            if list_category_uniq.count(category) == 0:
                list_category_uniq.append(category)
        return list_category_uniq


def get_list_category_():
    logging.info(f'get_list_category')
    with db:
        sql = db.cursor()
        list_category = [category for category in sql.execute('SELECT category, position FROM category ORDER BY id').fetchall()]
        list_category_uniq = []
        for category in list_category:
            if list_category_uniq.count(category) == 0:
                list_category_uniq.append(category)
        return list_category_uniq


def get_list_subcategory(category):
    logging.info(f'get_list_subcategory')
    with db:
        print(category)
        sql = db.cursor()
        list_subcategory = [subcategory[0] for subcategory in sql.execute('SELECT sub_category FROM places WHERE category=? ORDER BY id', (category,)).fetchall()]
        print(list_subcategory)
        list_subcategory_uniq = []
        for subcategory in list_subcategory:
            if list_subcategory_uniq.count(subcategory) == 0:
                list_subcategory_uniq.append(subcategory)
        return list_subcategory_uniq


def get_list_card(category, subcategory):
    logging.info(f'get_list_subcategory')
    with db:
        sql = db.cursor()
        list_card = [card for card in sql.execute('SELECT * FROM places WHERE category=? AND sub_category=? ORDER BY id', (category, subcategory)).fetchall()]
        list_card_sort = []
        list_card_top = []
        for card in list_card:
            if card[-1] == -1:
                list_card_sort.append(card)
            else:
                list_card_top.append(card)
        list_card_top.sort(key=lambda x: x[-1])
        list_card_top += list_card_sort
        return list_card_top


def get_list_card_event():
    logging.info(f'get_list_card_event')
    with db:
        sql = db.cursor()
        list_card = [card for card in sql.execute('SELECT * FROM places WHERE category=? ORDER BY id',
                                                  ("🎧Мероприятия недели",)).fetchall()]
        return list_card


def get_list_card_stat():
    logging.info(f'get_list_card_stat')
    with db:
        sql = db.cursor()
        list_card_stat = [category for category in sql.execute('SELECT title, count_link FROM places').fetchall()]
        return list_card_stat


def info_card(id_card):
    logging.info(f'info_card')
    with db:
        sql = db.cursor()
        card = sql.execute('SELECT * FROM places WHERE id=?', (id_card,)).fetchone()
        return card


def info_card_title(title):
    logging.info(f'info_card')
    with db:
        sql = db.cursor()
        card = sql.execute('SELECT * FROM places WHERE title=?', (title,)).fetchone()
        return card


def delete_card(title_card: str):
    logging.info(f'delete_card')
    with db:
        print(title_card)
        sql = db.cursor()
        sql.execute('DELETE FROM places WHERE id = ?', (int(title_card),))
        # sql.execute(f'DELETE FROM places WHERE title LIKE "{title_card}"')
        db.commit()


def set_attribute_card(attribute, set_attribute, id_card):
    logging.info(f'set_attribute_card')
    with db:
        sql = db.cursor()
        sql.execute(f'UPDATE places SET {attribute}= ? WHERE  id= ?', (set_attribute, id_card))
        db.commit()


def set_position_card(category: str, subcategory: str, id_card: int):
    """
    Устанавливаем позицию карточки
    :param category:
    :param subcategory:
    :param id_card:
    :return:
    """
    logging.info(f'set_attribute_card')
    # получаем список карточек в выбранной категории и подкатегории
    list_card_top = get_list_card(category, subcategory)
    with db:
        sql = db.cursor()
        # обновляем позицию карточек
        for card in list_card_top:
            # обновляем позицию карточку
            sql.execute(f'UPDATE places SET position= ? WHERE  id= ? AND NOT position=?', (card[-1]+1, card[0], -1))
        sql.execute(f'UPDATE places SET position= ? WHERE  id= ?', (0, id_card))
        db.commit()


def set_position_category(category: str):
    """
    Устанавливаем позицию карточки
    :param category:
    :return:
    """
    logging.info(f'set_attribute_card {category}')
    # получаем список карточек в выбранной категории и подкатегории
    list_category_top = get_list_category()
    with db:
        sql = db.cursor()
        # обновляем позицию карточек
        for cat in list_category_top:
            pos_cat = sql.execute('SELECT pos_cat FROM places WHERE category=?', (cat,)).fetchone()
            sql.execute(f'UPDATE places SET pos_cat= ? WHERE  category= ?', (pos_cat[0]+1, cat))
        sql.execute(f'UPDATE places SET pos_cat= ? WHERE  category= ?', (0, category))
        db.commit()


def set_count_show_card(count, id_card):
    logging.info(f'set_attribute_card')
    with db:
        sql = db.cursor()
        sql.execute(f'UPDATE places SET count_link= ? WHERE  id= ?', (count, id_card))
        db.commit()


# ПОЛЬЗОВАТЕЛЬ
def add_user(telegram_id: int, username: str) -> None:
    logging.info(f'add_user')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id FROM users')
        list_user = [row[0] for row in sql.fetchall()]
        if int(telegram_id) not in list_user:
            sql.execute(f'INSERT INTO users (telegram_id, username, is_admin, operator) '
                        f'VALUES ({telegram_id}, "{username}", 0, 0)')
            db.commit()



def get_list_users() -> list:
    """
    ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
    :return:
    """
    logging.info(f'get_list_users')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users ORDER BY id')
        list_id_username = [row for row in sql.fetchall()]
        return list_id_username


# def get_user(telegram_id):
#     """
#     ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
#     :param telegram_id:
#     :return:
#     """
#     logging.info(f'get_user')
#     with db:
#         sql = db.cursor()
#         return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


# def delete_user(telegram_id):
#     """
#     ПОЛЬЗОВАТЕЛЬ - удалить пользователя
#     :param telegram_id:
#     :return:
#     """
#     logging.info(f'delete_user')
#     with db:
#         sql = db.cursor()
#         sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
#         db.commit()


# def get_list_notadmins() -> list:
#     logging.info(f'get_list_notadmins')
#     with db:
#         sql = db.cursor()
#         sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (0, 'username'))
#         list_notadmins = [row for row in sql.fetchall()]
#         return list_notadmins


# АДМИНИСТРАТОРЫ - назначить пользователя администратором
# def set_admins(telegram_id):
#     logging.info(f'set_admins')
#     with db:
#         sql = db.cursor()
#         sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (1, telegram_id))
#         db.commit()


# АДМИНИСТРАТОРЫ - список администраторов
# def get_list_admins() -> list:
#     logging.info(f'get_list_admins')
#     with db:
#         sql = db.cursor()
#         sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (1, 'username'))
#         list_admins = [row for row in sql.fetchall()]
#         return list_admins


# АДМИНИСТРАТОРЫ - разжаловать пользователя из администраторов
# def set_notadmins(telegram_id):
#     logging.info(f'set_notadmins')
#     with db:
#         sql = db.cursor()
#         sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (0, telegram_id))
#         db.commit()
#
#
# def update_operator():
#     logging.info(f'update_operator')
#     sql.execute('UPDATE users SET operator = ?', (0,))
#     db.commit()
#
#
# def get_operator():
#     logging.info(f'get_operator')
#     list_operator = sql.execute('SELECT * FROM users WHERE operator = ?', (1,)).fetchall()
#     is_operator = [operator for operator in list_operator]
#     return is_operator

if __name__ == '__main__':
    db = sqlite3.connect('/Users/antonponomarev/PycharmProjects/PRO_SOFT/database.db', check_same_thread=False, isolation_level='EXCLUSIVE')
    sql = db.cursor()
    list_user = get_list_users()
    print(list_user)
