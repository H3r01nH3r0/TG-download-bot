import os

import urllib.request

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from src.connection import Connection
from src.models.users import CreateUser
from src.service.users import UsersService
from src.settings import settings

from tools.utils import get_config, generate_list
from tools.keyboards import Keyboards


config_filename = 'config.json'
config = get_config(config_filename)
user_database = UsersService()
keyboards = Keyboards(config["keyboards"])
bot = Bot(token=settings.bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


class NewSession(StatesGroup):
    connection_name = State()
    connection_file = State()


class GetPost(StatesGroup):
    post_number = State()


user_data = dict()

active_sessions = dict()

user_position = dict()

post_position = dict()


async def get_post(post_number: int, user_id: int) -> None:
    try:
        post_id = post_number
        channel_id = user_data[user_id]["channel_id"]
        res = await active_sessions[user_id].send_message(post_id, channel_id)
        text = config["text"]["chat_data"]
        if isinstance(res, list):
            message_id = [message.id for message in res]
            chat_title = res[0].chat.title
            message_text = res[0].caption if res[0].caption else "empty"
            media = [message.media for message in res]
            download_available = True
        else:
            if not res.media:
                message_id = res.id
                chat_title = res.chat.title
                message_text = res.text
                media = "no available media"
                download_available = False
            else:
                message_id = res.id
                chat_title = res.chat.title
                message_text = res.caption if res.caption else "empty"
                media = res.media
                download_available = True
        await bot.send_message(
            user_id,
            text=text.format(message_id, chat_title, message_text, media),
            reply_markup=keyboards.context_menu(post_position[user_id], download=download_available)
        )
    except Exception as a:
        print(a)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    try:
        await bot.send_message(
            message.from_user.id,
            text=config["text"]["hello_message"],
            reply_markup=keyboards.main_keyboard(
                group="start",
                active_session=user_data[message.from_user.id]["active"]
            )
        )
    except KeyError:
        await bot.send_message(
            message.from_user.id,
            text=config["text"]["hello_message"],
            reply_markup=keyboards.main_keyboard(group="start")
        )


@dp.callback_query_handler(state="*")
async def callback_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        if callback_query.data == "create":
            await NewSession.connection_name.set()
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["create_connection"],
                reply_markup=keyboards.main_keyboard(group="cancel_tool")
            )

        elif callback_query.data == "cancel":
            await state.finish()
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            try:
                await bot.send_message(
                    callback_query.from_user.id,
                    text=config["text"]["canceled"],
                    reply_markup=keyboards.main_keyboard(
                        group="start",
                        active_session=user_data[callback_query.from_user.id]["active"]
                    )
                )
            except KeyError:
                await bot.send_message(
                    callback_query.from_user.id,
                    text=config["text"]["canceled"],
                    reply_markup=keyboards.main_keyboard(
                        group="start"
                    )
                )

        elif callback_query.data == "choose":
            connections = await user_database.get_all(
                user_id=callback_query.from_user.id
            )
            if connections:
                await bot.delete_message(
                    callback_query.from_user.id,
                    callback_query.message.message_id
                )
                await bot.send_message(
                    callback_query.from_user.id,
                    text=config["text"]["choose_session"],
                    reply_markup=keyboards.from_orm(connections)
                )
            else:
                await bot.delete_message(
                    callback_query.from_user.id,
                    callback_query.message.message_id
                )
                await bot.send_message(
                    callback_query.from_user.id,
                    text=config["text"]["no_session"],
                    reply_markup=keyboards.main_keyboard(group="start")
                )

        elif callback_query.data.startswith("connect"):
            user = await user_database.get(
                callback_query.from_user.id,
                callback_query.data.split("_")[-1]
            )
            user_data[callback_query.from_user.id] = dict()
            active_sessions[callback_query.from_user.id] = Connection(user)
            channels = await active_sessions[callback_query.from_user.id].get_channels()
            user_data[callback_query.from_user.id]["active"] = user.connection_name
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["choose_channel"],
                reply_markup=keyboards.choose_channel(channels)
            )

        elif callback_query.data.startswith("channel_id"):
            channel_id = int(callback_query.data.split("=")[-1])
            posts = await active_sessions[callback_query.from_user.id].get_messages(channel_id)
            post_list = generate_list(posts)
            user_data[callback_query.from_user.id]["channel_id"] = channel_id
            user_data[callback_query.from_user.id]["post_list"] = post_list
            user_data[callback_query.from_user.id]["all_posts"] = posts
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["choose_action"].format(len(posts)),
                reply_markup=keyboards.main_keyboard(group="choose_action")
            )

        elif callback_query.data == "post_number":
            await GetPost.post_number.set()
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["input_post"],
                reply_markup=keyboards.main_keyboard(group="cancel_tool")
            )

        elif callback_query.data == "post_list":
            post_list = user_data[callback_query.from_user.id]["post_list"]
            user_pos = user_position[callback_query.from_user.id] = (1, len(post_list))
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["post_list"],
                reply_markup=keyboards.post_list(post_list[user_pos[0]-1], user_pos)
            )

        elif callback_query.data.startswith("forward"):
            user_pos, list_end = user_position[callback_query.from_user.id]
            post_list = user_data[callback_query.from_user.id]["post_list"]
            if callback_query.data.endswith("+"):
                if user_pos < list_end:
                    user_position[callback_query.from_user.id] = (user_pos + 1, list_end)
            elif callback_query.data.endswith("-"):
                if user_pos > 1:
                    user_position[callback_query.from_user.id] = (user_pos - 1, list_end)
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["post_list"],
                reply_markup=keyboards.post_list(
                    post_list[user_position[callback_query.from_user.id][0] - 1],
                    user_position[callback_query.from_user.id]
                )
            )

        elif callback_query.data == user_data[callback_query.from_user.id]["active"]:
            channels = await active_sessions[callback_query.from_user.id].get_channels()
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["choose_channel"],
                reply_markup=keyboards.choose_channel(channels)
            )

        elif callback_query.data == "disconnect":
            user_list = [active_sessions, user_data, user_position, post_position]
            for item in user_list:
                try:
                    del item[callback_query.from_user.id]
                except KeyError:
                    continue
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                text=config["text"]["disconnected"],
                reply_markup=keyboards.main_keyboard(group="start")
            )

        elif callback_query.data.startswith("post_id="):
            post_id = int(callback_query.data.split("=")[-1])
            post_pos = user_data[callback_query.from_user.id]["all_posts"].index(post_id)
            post_position[callback_query.from_user.id] = (
                post_pos + 1,
                len(user_data[callback_query.from_user.id]["all_posts"])
            )
            await get_post(post_id, callback_query.from_user.id)
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )

        elif callback_query.data in ["prev", "next"]:
            current, list_end = post_position[callback_query.from_user.id]
            if callback_query.data == "prev":
                if current > 1:
                    current -= 1
            elif callback_query.data == "next":
                if current < list_end:
                    current += 1
            post_position[callback_query.from_user.id] = (current, list_end)
            post_id = user_data[callback_query.from_user.id]["all_posts"][current-1]
            await get_post(post_id, callback_query.from_user.id)
            await bot.delete_message(
                callback_query.from_user.id,
                callback_query.message.message_id
            )

        elif callback_query.data == "download":
            post_poss = post_position[callback_query.from_user.id][0]
            post_id = user_data[callback_query.from_user.id]["all_posts"][post_poss-1]
            channel_id = user_data[callback_query.from_user.id]["channel_id"]
            result = await active_sessions[callback_query.from_user.id].send_message(post_id, channel_id)
            download = active_sessions[callback_query.from_user.id].download_media
            await types.ChatActions.upload_document()
            if isinstance(result, list):
                content = [await download(message, callback_query.from_user.id) for message in result]
                for file in content:
                    await bot.send_document(
                        callback_query.from_user.id,
                        document=open(file, "rb")
                    )
                    os.remove(file)
            else:
                content = await download(result, callback_query.from_user.id)
                await bot.send_document(
                    callback_query.from_user.id,
                    document=open(content, "rb")
                )
                os.remove(content)
    except Exception as a:
        print(a)


@dp.message_handler(content_types=types.ContentType.all(), state=NewSession.connection_name)
async def set_connection_name(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["connection_name"] = message.text

        connections = await user_database.get_all(message.from_user.id)
        for connection in connections:
            if connection.connection_name == message.text:
                await state.finish()
                await NewSession.connection_name.set()
                await bot.send_message(
                    message.from_user.id,
                    text=config["text"]["choose_another_name"],
                    reply_markup=keyboards.main_keyboard("cancel_tool")
                )
                break
        else:
            await NewSession.connection_file.set()
            await bot.send_message(
                message.from_user.id,
                text=config["text"]["get_session"],
                reply_markup=keyboards.main_keyboard("cancel_tool")
            )
    except Exception as a:
        print(a)


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=NewSession.connection_file)
async def set_connection_file(message: types.Message, state: FSMContext):
    try:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file = file_info.file_path
        file_format = message.document.file_name.split(".")[-1]
        async with state.proxy() as data:
            connection_name = data["connection_name"]
        connection_file = f"{connection_name}_{message.from_user.id}.{file_format}"
        path = f"{connection_file}"
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{settings.bot_token}/{file}', path)
        user = CreateUser(
            user_id=message.from_user.id,
            connection_name=connection_name,
            connection_file=connection_file
        )
        await user_database.create(user)
        try:
            await bot.send_message(
                message.from_user.id,
                text=config["text"]["session_saved"],
                reply_markup=keyboards.main_keyboard(
                    group="start",
                    active_session=user_data[message.from_user.id]["active"]
                )
            )
        except KeyError:
            await bot.send_message(
                message.from_user.id,
                text=config["text"]["session_saved"],
                reply_markup=keyboards.main_keyboard(
                    group="start"
                )
            )
    except Exception as a:
        print(a)


@dp.message_handler(content_types=types.ContentType.all(), state=GetPost.post_number)
async def set_post_number(message: types.Message, state: FSMContext):
    try:
        post_id = int(message.text)
        post_pos = user_data[message.from_user.id]["all_posts"].index(post_id)
        post_position[message.from_user.id] = (
            post_pos + 1,
            len(user_data[message.from_user.id]["all_posts"])
        )
        await state.finish()
        await get_post(post_id, message.from_user.id)
        await bot.delete_message(
            message.from_user.id,
            message.message_id
        )
    except Exception as a:
        print(a)


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=False)
