from typing import Dict, List, Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from src.models.users import User


class Connection:
    def __init__(self, user: User):
        connection_name = user.connection_file.split(".")[0]
        self.connection = Client(
            name=connection_name
        )

    async def get_channels(self) -> Dict:
        channels = dict()
        async with self.connection:
            async for dialog in self.connection.get_dialogs():
                if dialog.chat.title:
                    channels[dialog.chat.id] = dialog.chat.title
                else:
                    continue
        return channels

    async def get_messages(self, chat_id: int) -> List:
        async with self.connection:
            messages = [message.id async for message in self.connection.get_chat_history(chat_id)]
        return messages

    async def check_media_group(self, message_id, chat_id):
        try:
            media_group = [message.id for message in await self.connection.get_media_group(chat_id, message_id)]
            return media_group
        except ValueError:
            return False

    async def send_message(self, message_id: int, chat_id: int):
        async with self.connection:
            check = await self.check_media_group(message_id, chat_id)
            if check:
                message = await self.connection.get_media_group(chat_id, message_id)
            else:
                message = await self.connection.get_messages(chat_id, message_id)
        return message

    async def download_media(self, message: Message, user_id: int):
        async with self.connection:
            result = await self.connection.download_media(
                message,
                file_name=f"./downloads/{str(user_id)}/"
            )
        return result
