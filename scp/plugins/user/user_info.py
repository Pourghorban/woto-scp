from scp import user, bot
from scp.utils.selfInfo import info
from scp.utils.strUtils import name_check, permissionParser
from pyrogram.types import (
    Message,
    InlineQuery,
    CallbackQuery,
)
from pyrogram.raw.types.messages.bot_results import (
    BotResults,
)


__PLUGIN__ = 'UserInfo'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'Chat information resolver',
            user.md.SubSection(
                'user info',
                user.md.Code('(*prefix)info {chat_id} or {user_id}'),
            ),
        ),
    ),
)


@user.on_message(
    (user.sudo | user.owner) &
    user.command(
        'info',
        prefixes=user.cmd_prefixes,
    ),
)
async def info_handler(_, message: Message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        if message.reply_to_message.forward_from:
            get_user = message.reply_to_message.forward_from.id
        else:
            get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        Uid = (await user.get_chat(get_user)).id
        x: BotResults = await user.get_inline_bot_results(
            info['_bot_username'],
            '_userInfo ' + str(Uid),
        )
    except (
        user.exceptions.PeerIdInvalid,
        user.exceptions.BotResponseTimeout,
    ) as err:
        return await message.reply_text(err, quote=True)
    for m in x.results:
        await message.reply_inline_bot_result(
            x.query_id, 
            m.id, 
            quote=True,
        )


@bot.on_inline_query(
    user.filters.user(
        info['_user_id'],
    )
    & user.filters.regex('^_userInfo'),
)
async def _(_, query: InlineQuery):
    try:
        answers = []
        get_user = int(query.query.split(' ')[1])
    except (ValueError, IndexError):
        return None
    try:
        u = await user.get_users(get_user)
    except user.exceptions.PeerIdInvalid:
        return None
    except Exception:
        u = await user.get_chat(get_user)
    onlines = await user.try_get_online_counts(get_user)
    if isinstance(u, user.types.Chat):
        text = user.md.Section(
            'ChatInfo:',
            user.md.SubSection(
                user.md.KeyValueItem('title', u.title),
                user.md.KeyValueItem(
                    user.md.Bold('chat_id'), user.md.Code(u.id),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('type'), user.md.Code(u.type),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('title'), user.md.Code(u.title),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('invite_link'), user.md.Code(u.invite_link),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('members_count'), user.md.Code(
                        u.members_count,
                    ),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('dc_id'), user.md.Code(u.dc_id),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('online_count'), user.md.Code(str(onlines)),
                ),
                user.md.KeyValueItem(
                    user.md.Bold('username'), user.md.Code(
                        name_check(u.username),
                    ),
                ),
            ),
        )
        keyboard = user.types.InlineKeyboardMarkup(
            [
                [
                    user.types.InlineKeyboardButton(
                        'Permissions', callback_data=f'cperm_{u.id}',
                    ),
                    user.types.InlineKeyboardButton(
                        'Description', callback_data=f'cdesc_{u.id}',
                    ),
                ],
            ],
        ) if u.permissions else None
    else:
        text = user.md.Section(
            'UserInfo:',
            user.md.SubSection(
                user.md.KeyValueItem(
                    key='name', value=u.first_name + ' ' + (u.last_name or ''),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'user_id',
                    ), user.md.Code(u.id),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'is_contact',
                    ), user.md.Code(u.is_contact),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'mutual_contact',
                    ), user.md.Code(u.is_mutual_contact),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'common_groups',
                    ), user.md.Code(len(await u.get_common_chats())),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'pfp_count',
                    ), user.md.Code(await user.get_profile_photos_count(u.id)),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'username',
                    ), user.md.Code(name_check(u.username)),
                ),
                user.md.KeyValueItem(
                    user.md.Bold(
                        'dc_id',
                    ), user.md.Code(u.dc_id),
                ),
            ),
        )
        keyboard = user.types.InlineKeyboardMarkup(
            [[
                user.types.InlineKeyboardButton(
                    'UserLink',
                    url=f'tg://user?id={u.id}',
                ),
                user.types.InlineKeyboardButton(
                    'Description', callback_data=f'cdesc_{u.id}',
                ),
            ]],
        )
    answers.append(
        user.types.InlineQueryResultArticle(
            title='Info',
            input_message_content=user.types.InputTextMessageContent(text),
            reply_markup=keyboard,
        ),
    )
    await query.answer(
        answers,
        cache_time=0,

    )


@bot.on_callback_query(
    bot.sudo
    & bot.filters.regex('^cperm_'),
)
async def _(_, query: CallbackQuery):
    await query.answer(
        permissionParser(
            (await user.get_chat(int(query.data.split('_')[1]))).permissions,
        ), show_alert=True,
    )


@bot.on_callback_query(
    bot.sudo
    & bot.filters.regex('^cdesc_'),
)
async def _(_, query: CallbackQuery):
    chat = await user.get_chat(int(query.data.split('_')[1]))
    await query.answer(
        chat.description[:150] if chat.description else chat.bio,
        show_alert=True,
    )
