import asyncio
import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from random import choices
from googletrans import Translator

translator = Translator()

async def get_categories(session):
    async with session.get('https://www.themealdb.com/api/json/v1/1/categories.php') as response:
        data = await response.json()
        return data['categories']

async def get_meals_by_category(session, category, num_recipes):
    async with session.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?c={category}') as response:
        data = await response.json()
        meals = data['meals']
        if len(meals) < num_recipes:
            num_recipes = len(meals)
        selected_meals = choices(meals, k=num_recipes)
        return [meal['idMeal'] for meal in selected_meals]

async def get_recipe_details(session, meal_id):
    async with session.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}') as response:
        data = await response.json()
        return data['meals'][0]


async def category_search_random(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Пожалуйста, укажите количество рецептов после команды.")
            return

        num_recipes = int(parts[1])

    except (IndexError, ValueError):
        await message.answer("Пожалуйста, укажите количество рецептов после команды.")
        return
    await state.set_data({"num_recipes": num_recipes})
    async with aiohttp.ClientSession() as session:
        categories = await get_categories(session)
        buttons = []
        for c in categories:
            callback_data = f"{c['strCategory']}:{num_recipes}"
            buttons.append(types.InlineKeyboardButton(text=c['strCategory'], callback_data=callback_data))
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons],row_width=2)
        await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state("choose_category")


async def category_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "show_recipes":
      data = await state.get_data()
      num_recipes = data["num_recipes"]
      category = data["category"]
      async with aiohttp.ClientSession() as session:
          meal_ids = await get_meals_by_category(session, category, num_recipes)
          await state.set_data({"meal_ids": meal_ids})
          translated_titles = [translator.translate(meal['strMeal'], dest='ru').text for meal in (await asyncio.gather(*[get_recipe_details(session,meal_id) for meal_id in meal_ids]))]
          keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Показать рецепты", callback_data="show_recipes")]])
          await callback_query.message.edit_text("\n".join(translated_titles), reply_markup=keyboard)
          await callback_query.answer()
      await state.set_state("show_recipes")
      return

    category, num_recipes = callback_query.data.split(':')
    await state.set_data({"category": category})
    data = await state.get_data()
    num_recipes = int(num_recipes)
    async with aiohttp.ClientSession() as session:
        meal_ids = await get_meals_by_category(session, category, num_recipes)
        await state.set_data({"meal_ids": meal_ids})
        translated_titles = [translator.translate(meal['strMeal'], dest='ru').text for meal in (await asyncio.gather(*[get_recipe_details(session,meal_id) for meal_id in meal_ids]))]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Показать рецепты", callback_data="show_recipes")]])
        await callback_query.message.edit_text("\n".join(translated_titles), reply_markup=keyboard)
        await callback_query.answer()
    await state.set_state("show_recipes")


async def show_recipes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    meal_ids = data["meal_ids"]
    async with aiohttp.ClientSession() as session:
      for meal_id in meal_ids:
        meal = await get_recipe_details(session, meal_id)
        translated_recipe = translator.translate(meal['strInstructions'], dest='ru').text
        ingredients = []
        for i in range(1,21):
          ingredient = meal[f'strIngredient{i}']
          if ingredient:
            measure = meal[f'strMeasure{i}']
            ingredients.append(translator.translate(f'{measure} {ingredient}', dest='ru').text)

        await message.answer(f"""{translator.translate(meal['strMeal'], dest='ru').text}

Рецепт:
{translated_recipe}

Ингредиенты: {', '.join(ingredients)}""")
    await state.finish()