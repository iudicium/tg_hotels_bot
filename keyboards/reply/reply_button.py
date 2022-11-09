from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class Reply:
    @staticmethod
    def add_buttons(text: str) -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        button = KeyboardButton(text=f"{text}")
        markup.add(button)
        return markup

