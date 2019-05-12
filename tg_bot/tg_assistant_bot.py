import urllib

import requests
import telebot
import logging
import shelve
import re
import json

from telebot import types

from tg_bot import tg_config
from tg_bot.database import sqlite_db, TelegramUser, Group

logger = logging.getLogger("main")


bot = telebot.TeleBot(tg_config.ASSISTANT_BOT_TOKEN)


def listener(messages):
    # print(messages)
    for msg in messages:
        print(msg)
        TelegramUser.update_data(msg)
        with shelve.open("tg_messages_cache") as f:
            f[str(msg.chat.id) + "_" + str(msg.message_id)] = str(msg)

        # bot.send_message(msg.chat.id, str(msg))


@bot.message_handler(commands=["start"])
def cmd_start(message):
    pass


@bot.message_handler(commands=["setInfo"])
def edu_info_input(message):
    current_user = TelegramUser.get(TelegramUser.user_id == message.from_user.id)
    current_group = Group.get(Group.id == current_user.group)
    print()

    input_data = [
        ("Вибрати групу" if not current_group else current_group.group_name.upper(), "group_info"),
        ("Статистика", "statistics"),
        ("Увімкнути нагадування про поточну пару", "subscribe_alarm"),
        ("Вимкнути нагадування про поточну пару", "unsubscribe_alarm"),
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        *[types.InlineKeyboardButton(text=text, callback_data=str(data)) for text, data in input_data]
    )
    bot.send_message(
        message.chat.id,
        "Було б добре дізнатись наскільки багато наукових робіт у тебе за спиною?",
        reply_markup=keyboard
    )


input_parameters = {
    "group_name": {
        "message": {
            "start":
                "Було би круто дізнатись до якої групи належить мій улюблений користувач.\n\n"
                "* <GROUP_PREFIX>-<INDEX> *, наприклад: *ДП-41, ТК-62, тк-31*\n\n"
                "Але це лише приклад, потрібно все ж ввести свою групу: ",
            "search_result":
                "API RozkladKPI: group_name={}\n"
                "Знайдено {} схожих за назвою. Залишився остаточний вибір...",
        },
        "regexp": "[А-Яа-я]{2} [1-9]{2}",
    }
}


class InputState:

    START = 0

    INPUT_GROUP_NAME = 10
    SELECT_GROUP_NAME = 11

    @staticmethod
    def set_state(user_id, state):
        key = "state_{}".format(user_id)
        try:
            with shelve.open("tg_messages_cache") as cache:
                cache[key] = state
                return True
        except Exception as e:
            return False

    @staticmethod
    def get_current_state(user_id):
        key = "state_{}".format(user_id)
        try:
            with shelve.open("tg_messages_cache") as cache:
                return cache[key]
        except:
            return 0


group_pattern = "[А-Яа-яіІ]{2}-[1-9]{2}"


@bot.message_handler(commands=["setGroup"])
def group_input(message):
    output = input_parameters["group_name"]["message"]["start"]

    chat_id = message.chat.id
    user_id = message.from_user.id
    InputState.set_state(user_id, InputState.START)

    bot.send_message(chat_id, output, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
    InputState.set_state(user_id, InputState.INPUT_GROUP_NAME)


@bot.message_handler(
    func=lambda message: InputState.get_current_state(message.from_user.id) == InputState.INPUT_GROUP_NAME,
    regexp="[А-Яа-яіІ]{2}-[1-9]{2}",
    content_types=["text"]
)
def group_name_search_callback(message):
    output = input_parameters["group_name"]["message"]["search_result"]
    regexp = re.compile("[А-Яа-яіІ]{2}-[1-9]{2}")

    def get_group_by_name(group_name):
        response = requests.get(
            "http://api.rozklad.org.ua/v2/groups/",
            params={
                "search": json.dumps({'query': group_name})
            }).json()
        try:
            return response["data"]
        except KeyError as e:
            return []

    user_id = message.from_user.id
    group_name = regexp.findall(message.text).pop()
    group_data = get_group_by_name(group_name)

    if group_name:
        for item in group_data:
            Group().update_data(**{
                "group_id": item["group_id"],
                "group_okr": item["group_okr"],
                "group_name": item["group_full_name"],
                "group_type": item["group_type"],
            })

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            *[types.KeyboardButton(text="{id}: {group_name}".format(
                id=item["group_id"], group_name=item["group_full_name"]
            )) for item in group_data]
        )
        bot.send_message(message.chat.id, output.format(group_name, len(group_data)),
                         reply_markup=keyboard, parse_mode="HTML")
        InputState.set_state(user_id, InputState.SELECT_GROUP_NAME)


@bot.message_handler(
    func=lambda message: InputState.get_current_state(message.from_user.id) == InputState.SELECT_GROUP_NAME,
    content_types=["text"]
)
def select_group_name(message):
    group_id, group_name = message.text.split(": ")
    user = TelegramUser.find_by_id(message.from_user.id)
    user.group = Group.get(Group.group_id == group_id).id
    user.save()

    InputState.set_state(user.user_id, InputState.START)


if __name__ == '__main__':
    bot.set_update_listener(listener)
    bot.polling(none_stop=True)