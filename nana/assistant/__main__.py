import os
from platform import python_version
import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from nana.tr_engine.strings import tld
from nana import (
    app,
    setbot,
    AdminSettings,
    DB_AVAILABLE,
    USERBOT_VERSION,
    ASSISTANT_VERSION,
    BotUsername,
    OwnerName,
    NANA_IMG,
)

if DB_AVAILABLE:
    from nana.modules.database.chats_db import get_all_chats


@setbot.on_message(filters.private & ~filters.user(AdminSettings))
async def un_auth(_, message):
    if message.chat.id is AdminSettings:
        return

    msg = f"""
Hi {message.chat.first_name},
You must be looking forward on how I work.
In that case I can give you helpful links to self host me on your own.
Here are some links for you
        """
    buttons = [
        [
            InlineKeyboardButton(
                "Documentation", url="https://aman-a.gitbook.io/nana-remix/"
            )
        ],
        [
            InlineKeyboardButton(
                "Repository", url="https://github.com/pokurt/Nana-Remix"
            ),
            InlineKeyboardButton("Support", url="https://t.me/nanabotsupport"),
        ],
    ]
    await message.reply(msg, reply_markup=InlineKeyboardMarkup(buttons))


@setbot.on_message(filters.user(AdminSettings) & filters.command(["start"]))
async def start(_, message):
    if message.chat.type != "private":
        await message.reply("henlo ^0^")
    else:
        if len(message.text.split()) >= 2:
            helparg = message.text.split()[1]
            if helparg == "help_inline":
                await message.reply(tld("inline_help_text").format(BotUsername))
                return
        try:
            me = await app.get_me()
        except ConnectionError:
            me = None
        userbot_stat = "Stopped" if not me else "Running"
        db_stat = len(get_all_chats()) if DB_AVAILABLE else "None"
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=tld("help_btn"), callback_data="help_back"
                    ),
                    InlineKeyboardButton(
                        tld("language_btn"), callback_data="set_lang_"
                    ),
                ]
            ]
        )
        if NANA_IMG:
            await message.reply_photo(
                NANA_IMG,
                caption=tld("start_message").format(
                    OwnerName,
                    python_version(),
                    userbot_stat,
                    USERBOT_VERSION,
                    ASSISTANT_VERSION,
                    DB_AVAILABLE,
                    db_stat,
                ),
                reply_markup=buttons,
            )
        else:
            await message.reply(
                tld("start_message").format(
                    OwnerName,
                    python_version(),
                    userbot_stat,
                    USERBOT_VERSION,
                    ASSISTANT_VERSION,
                    DB_AVAILABLE,
                    db_stat,
                ),
                reply_markup=buttons,
            )


@setbot.on_message(filters.user(AdminSettings) & filters.command(["getme"]))
async def get_myself(client, message):
    try:
        me = await app.get_me()
    except ConnectionError:
        await message.reply("Bot is currently turned off!")
        return
    getpp = await client.download_media(
        me.photo.big_file_id, file_name="nana/downloads/pfp.png"
    )
    text = "**ℹ️ Your profile:**\n"
    text += "First name: {}\n".format(me.first_name)
    if me.last_name:
        text += "Last name: {}\n".format(me.last_name)
    text += "User ID: `{}`\n".format(me.id)
    if me.username:
        text += "Username: @{}\n".format(me.username)
    text += "Phone number: `{}`\n".format(me.phone_number)
    text += "`Nana Version    : v{}`\n".format(USERBOT_VERSION)
    text += "`Manager Version : v{}`".format(ASSISTANT_VERSION)
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Hide phone number", callback_data="hide_number")]]
    )
    if me.photo:
        await message.reply_photo(photo=getpp, caption=text, reply_markup=button)
    else:
        await message.reply(text, reply_markup=button)
    if os.path.exists(getpp):
        os.remove(getpp)


# For callback query button
def dynamic_data_filter(data):
    async def func(flt, _, query):
        return flt.data == query.data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


@setbot.on_callback_query(dynamic_data_filter("hide_number"))
async def get_myself_btn(client, query):
    try:
        me = await app.get_me()
    except ConnectionError:
        await client.answer_callback_query(
            query.id, "Bot is currently turned off!", show_alert=True
        )
        return

    if query.message.caption:
        text = query.message.caption.markdown
    else:
        text = query.message.text.markdown

    num = ["*" * len(me.phone_number)]

    if "***" not in text.split("Phone number: `")[1].split("`")[0]:
        text = text.replace(
            "Phone number: `{}`\n".format(me.phone_number),
            "Phone number: `{}`\n".format("".join(num)),
        )
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Show phone number", callback_data="hide_number")]]
        )
    else:
        text = text.replace(
            "Phone number: `{}`\n".format("".join(num)),
            "Phone number: `{}`\n".format(me.phone_number),
        )
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Hide phone number", callback_data="hide_number")]]
        )

    if query.message.caption:
        await query.message.edit_caption(caption=text, reply_markup=button)
    else:
        await query.message.edit(text, reply_markup=button)
    await query.answer()


@setbot.on_callback_query(dynamic_data_filter("language_back"))
async def lang_back(_, query):
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    userbot_stat = "Stopped" if not me else "Running"
    db_stat = len(get_all_chats()) if DB_AVAILABLE else "None"
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=tld("help_btn"), callback_data="help_back"),
                InlineKeyboardButton(tld("language_btn"), callback_data="set_lang_"),
            ]
        ]
    )
    if NANA_IMG:
        await query.message.edit_caption(
            tld("start_message").format(
                OwnerName,
                python_version(),
                userbot_stat,
                USERBOT_VERSION,
                ASSISTANT_VERSION,
                DB_AVAILABLE,
                db_stat,
            ),
        )
        await query.message.edit_reply_markup(buttons)
    else:
        await query.message.edit(
            tld("start_message").format(
                OwnerName,
                python_version(),
                userbot_stat,
                USERBOT_VERSION,
                ASSISTANT_VERSION,
                DB_AVAILABLE,
                db_stat,
            ),
            reply_markup=buttons,
        )
    await query.answer()


@setbot.on_callback_query(dynamic_data_filter("report_errors"))
async def report_some_errors(client, query):
    await app.join_chat("@nanabotsupport")
    text = "Hi @DeprecatedUser, i got an error for you.\nPlease take a look and fix it if possible.\n\nThank you ❤️"
    err = query.message.text
    open("nana/cache/errors.txt", "w").write(err)
    await asyncio.gather(
        query.message.edit_reply_markup(reply_markup=None),
        app.send_document("nanabotsupport", "nana/cache/errors.txt", caption=text),
        client.answer_callback_query(query.id, "Report was sent!"),
    )
    os.remove("nana/cache/errors.txt")
