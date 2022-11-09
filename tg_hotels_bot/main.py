from loader import bot
import handlers
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
from database.model_functions.check_tables import check_if_tables_exist
if __name__ == '__main__':
    set_default_commands(bot)
    check_if_tables_exist()
    bot.add_custom_filter(StateFilter(bot))
    bot.infinity_polling()



