from typing import Dict, List, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Keyboards:
    def __init__(self, text: Dict):
        self._text = text

    def main_keyboard(self, group: str, active_session: str = False) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for key, value in self._text[group].items():
            markup.add(InlineKeyboardButton(text=value, callback_data=key))
        if active_session:
            markup.add(InlineKeyboardButton(text=f"{active_session} [active]🟢", callback_data=active_session))
        return markup

    def context_menu(self, number: Tuple[int, int], download: bool = False) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        now, end = number
        row = list()
        for key, value in self._text["select_message"].items():
            if key == "number":
                button = InlineKeyboardButton(text=value.format(now, end), callback_data=key)
                row.append(button)
            else:
                button = InlineKeyboardButton(text=value, callback_data=key)
                row.append(button)
        markup.row(*row)
        if download:
            markup.add(InlineKeyboardButton(text="DOWNLOAD ⬇️", callback_data="download"))
        markup.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data="cancel"),
            InlineKeyboardButton(text="DISCONNECT 🔴", callback_data="disconnect")
        )
        return markup

    @staticmethod
    def post_list(post_data: List, user_position: Tuple[int, int]) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        now, end = user_position
        for message_id in post_data:
            markup.add(InlineKeyboardButton(text=f"Пост №{message_id}", callback_data=f"post_id={message_id}"))
        markup.add(
            InlineKeyboardButton(text="◀️", callback_data="forward-"),
            InlineKeyboardButton(text=f"{now}/{end}", callback_data="None"),
            InlineKeyboardButton(text="▶️", callback_data="forward+")
        )
        markup.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data="cancel"),
            InlineKeyboardButton(text="DISCONNECT 🔴", callback_data="disconnect")
        )
        return markup

    @staticmethod
    def from_orm(data: List) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for user in data:
            markup.add(InlineKeyboardButton(
                text=user.connection_name,
                callback_data=f"connect_{user.connection_name}"
            ))
        markup.add(InlineKeyboardButton(text="Назад 🔙", callback_data="cancel"))
        return markup

    @staticmethod
    def choose_channel(channels: Dict):
        markup = InlineKeyboardMarkup()
        for channel_id, channel_name in channels.items():
            markup.add(InlineKeyboardButton(text=channel_name, callback_data=f"channel_id={channel_id}"))
        markup.add(
            InlineKeyboardButton(text="Назад 🔙", callback_data="cancel"),
            InlineKeyboardButton(text="DISCONNECT 🔴", callback_data="disconnect")
        )
        return markup
