"""
Reordering users' positions in a given queue.
"""

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, queues
from states.all_states import QueueSetup
from utils.get_db_data import get_queue_list, get_team_id
from utils.sticker_file_ids import CONFUSED_STICKER


@dp.callback_query_handler(text="reorder", state=QueueSetup.setting_up)
async def ask_to_pick(call: types.CallbackQuery, state: FSMContext):
    """Ask the user to pick a person to move on the list (part 1)."""
    logging.info("Reordering queue.")

    state_data = await state.get_data()

    queue_array = state_data["queue_array"]

    keyboard = types.InlineKeyboardMarkup()

    queue_list = ""
    for index, member in enumerate(queue_array, start=1):
        name = member["name"]
        queue_list += f"{index}. {name}\n"

        keyboard.add(
            types.InlineKeyboardButton(
                text=name,
                callback_data=f"from_{index-1}",
            )
        )

    await call.message.edit_text(
        f"<b>Pick the name that you want to move on the list.</b>\n{queue_list}",
        reply_markup=keyboard,
    )

    await call.answer()


@dp.callback_query_handler(text_startswith="from_", state=QueueSetup.setting_up)
async def ask_to_position(call: types.CallbackQuery, state: FSMContext):
    """Ask the user where to move the previously selected item (part 2)."""
    from_position = int(call.data.split("_")[-1])
    await state.update_data(from_position=from_position)

    queue_data = await state.get_data()
    queue_array = queue_data["queue_array"]

    keyboard = types.InlineKeyboardMarkup()

    queue_list = await get_queue_list(queue_array)

    for index, _ in enumerate(queue_array, start=1):
        keyboard.add(
            types.InlineKeyboardButton(
                text=str(index),
                callback_data=f"to_{index-1}",
            )
        )

    await call.message.edit_text(
        "<b>Pick the place that you want to move it to on the "
        f"list.</b>\n{queue_list}",
        reply_markup=keyboard,
    )

    await call.answer()


@dp.callback_query_handler(text_startswith="to_", state=QueueSetup.setting_up)
async def reorder_queue(call: types.CallbackQuery, state: FSMContext):
    """Reorder the queue and present it (final part 3)."""
    state_data = await state.get_data()

    from_position = state_data["from_position"]
    to_position = int(call.data.split("_")[-1])

    queue_array = state_data["queue_array"]
    queue_name = state_data["queue_name"]

    # reordering doesnt make any sense
    if from_position == to_position:
        name = call.from_user.first_name

        await call.message.answer_sticker(CONFUSED_STICKER)
        await call.message.answer(
            f"Are you sure that you are not drunk, {name}-san?",
        )
    else:
        item_to_move = queue_array.pop(from_position)
        queue_array.insert(to_position, item_to_move)

        await state.update_data(queue_array=queue_array)

        team_id = await get_team_id(call.from_user.id)

        queue_data = {f"queues.{queue_name}": queue_array}
        await queues.update_one({"id": team_id}, {"$set": queue_data}, upsert=True)

    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Reorder", callback_data=f"reorder"),
        types.InlineKeyboardButton(text="Done", callback_data=f"order_ready"),
    ]
    keyboard.add(*buttons)

    queue_list = await get_queue_list(queue_array)

    await call.message.edit_text(
        f"<b>Here is your {queue_name} queue:</b>\n{queue_list}\nIf you "
        f"would like the {queue_name} queue to have a different order, "
        "choose the <b>Reorder</b> option below.\nOnce you are happy with "
        "the queue order, select <b>Done</b>.",
        reply_markup=keyboard,
    )

    await call.answer()
