import logging
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from recipes_handler import category_search_random, category_chosen, show_recipes
from token_data import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот для поиска рецептов.\n\n"
                         "Доступные команды:\n"
                         "/start - показать приветствие\n"
                         "/category_search_random <number> - поиск рецептов по категории (где <number> - количество рецептов)")

@dp.message(Command("category_search_random"))
async def cmd_category_search_random(message: types.Message, state: FSMContext):
    await category_search_random(message, state)

@dp.callback_query()
async def callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await category_chosen(callback_query, state)

@dp.message()
async def message_handler(message: types.Message, state: FSMContext):
    await show_recipes(message, state)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот прекратил работу.")