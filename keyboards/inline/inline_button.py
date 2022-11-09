from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

class Inline:
    @staticmethod
    def add_buttons(text: List[str], callback: List[str]) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for index, line in enumerate(text):
            button = InlineKeyboardButton(text=f"{line}", callback_data=callback[index])
            markup.add(button)
        return markup



