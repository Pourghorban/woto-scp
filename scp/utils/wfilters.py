from pyrogram import (
    types,
    filters,
)


async def my_contacts_filter(_, __, m: types.Message) -> bool:
    return m and m.from_user and m.from_user.is_contact

my_contacts = filters.create(my_contacts_filter)
"""Filter messages sent by contact users."""

async def stalk_filter(_, __, m: types.Message) -> bool:
    return m and m.text and m.text.find('stalk') != -1

stalk_text = filters.create(stalk_filter)
"""Filter messages which contains stalk in them."""


async def channel_in_group_filter(_, __, m: types.Message) -> bool:
    if m.service or not m.chat or not m.chat.title:
        return False
    elif m.game:
        return False
    elif m.empty:
        return False
    my_lower = m.chat.title.lower()
    if m.chat.username:
        if m.chat.username.lower().find('night') >= 0:
            return False
    if (
        my_lower.find('chat') >= 0 or
        my_lower.find('talk') >= 0 or
        my_lower.find('@') >= 0 or
        my_lower.find('discussion') >= 0 or
        my_lower.find('tele') >= 0 or
        my_lower.find('dev') >= 0
    ):
        if not my_lower.find('anime') >= 0:
            return False
    return (
        m and
        m.chat.type in ['group', 'supergroup'] and
        m.sender_chat and
        m.sender_chat.type == 'channel'
    )

channel_in_group = filters.create(channel_in_group_filter)
"""Filter messages sent by contact users."""
