from scp import bot, user
from pyrogram import filters
from pyrogram.types import CallbackQuery


@bot.on_callback_query(
    user.sudo &
    filters.regex("^reply_")
)
async def reply_button_handler(_, query: CallbackQuery):
    pass

@bot.on_callback_query(
    user.sudo &
    filters.regex("^msg_")
)
async def send_msg_button_handler(_, query: CallbackQuery):
    pass

@bot.on_callback_query(
    user.sudo &
    filters.regex("^block_")
)
async def block_button_handler(_, query: CallbackQuery):
    pass

@bot.on_callback_query(
    user.sudo &
    filters.regex("delete_msg$")
)
async def delete_msg_button_handler(_, query: CallbackQuery):
    pass

@bot.on_callback_query(
    user.sudo &
    filters.regex("^react_")
)
async def react_button_handler(_, query: CallbackQuery):
    pass

@bot.on_callback_query(
    user.sudo &
    filters.regex("^read_")
)
async def read_button_handler(_, query: CallbackQuery):
    pass

@bot.on_callback_query(
    (
        user.owner | user.sudo
    ) & filters.regex("^sendMedia_")
)
async def send_media_button_handler(_, query: CallbackQuery):
    target_chat_id = user.scp_config.avalon_pms
    my_strs = query.data.split("_")
    from_chat_id = int(my_strs[1])
    message_id = int(my_strs[2])
    if len(my_strs) > 3:
        target_chat_id = int(my_strs[3])

    if query.message:
        message_field = query.message.text.split("• MESSAGE: (")
        if not message_field or message_field[0].find(")") == -1:
            return await query.answer("No file id was found...", show_alert=True)
        
        my_strs = message_field[0].split(") ")
        media_type = my_strs[0]
        file_id = my_strs[1]
        send_method = getattr(user, f"send_{media_type}", None)
        if not send_method:
            return await query.answer(f"Couldn't find send method for {media_type}.")
        
        return await send_method(user, target_chat_id, file_id, reply_to_message_id=query.message.id)
    
    

    # second way around: no message is passed
    try:
        await user.forward_messages(
            chat_id=target_chat_id,
            from_chat_id=from_chat_id,
            message_ids=message_id
        )
    except Exception as e:
        await query.answer(f"Failed due to: {str(e)[:60]}")


    
