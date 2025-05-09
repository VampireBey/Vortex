from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from config import BANNED_USERS
from strings import get_command
from LostMuzik import YouTube, app
from LostMuzik.core.call import LostMuzik
from LostMuzik.misc import db
from LostMuzik.utils.database import get_loop
from LostMuzik.utils.decorators import AdminRightsCheck
from LostMuzik.utils.inline.play import (stream_markup,
                                          telegram_markup)
from LostMuzik.utils.stream.autoclear import auto_clean


# Commands
SKIP_COMMAND = get_command("SKIP_COMMAND")


@app.on_message(
    filters.command(SKIP_COMMAND)
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_12"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                            except:
                                return await message.reply_text(
                                    _["admin_16"]
                                )
                            if popped:
                                if (
                                    config.AUTO_DOWNLOADS_CLEAR
                                    == str(True)
                                ):
                                    await auto_clean(popped)
                            if not check:
                                try:
                                    await message.reply_text(
                                        _["admin_10"].format(
                                            message.from_user.first_name
                                        )
                                    )
                                    await LostMuzik.stop_stream(chat_id)
                                except:
                                    return
                                break
                    else:
                        return await message.reply_text(
                            _["admin_15"].format(count)
                        )
                else:
                    return await message.reply_text(_["admin_14"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_13"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                if config.AUTO_DOWNLOADS_CLEAR == str(True):
                    await auto_clean(popped)
            if not check:
                await message.reply_text(
                    _["admin_10"].format(message.from_user.first_name)
                )
                try:
                    return await LostMuzik.stop_stream(chat_id)
                except:
                    return
        except:
            try:
                await message.reply_text(
                    _["admin_10"].format(message.from_user.first_name)
                )
                return await LostMuzik.stop_stream(chat_id)
            except:
                return
    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await message.reply_text(
                _["admin_11"].format(title)
            )
        try:
            await LostMuzik.skip_stream(chat_id, link, video=status)
        except Exception:
            return await message.reply_text(_["call_9"])
        button = telegram_markup(_, chat_id)
        img = None
        run = await message.reply_text(
                text=_["stream_1"].format(
                  title,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    elif "vid_" in queued:
        mystic = await message.reply_text(
            _["call_10"], disable_web_page_preview=True
        )
        try:
            file_path, direct = await YouTube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )
        except:
            return await mystic.edit_text(_["call_9"])
        try:
            await LostMuzik.skip_stream(chat_id, file_path, video=status)
        except Exception:
            return await mystic.edit_text(_["call_9"])
        button = stream_markup(_, videoid, chat_id)
        img = None
        run = await message.reply_text(
                text=_["stream_1"].format(
                  title,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"
        await mystic.delete()
    elif "index_" in queued:
        try:
            await LostMuzik.skip_stream(chat_id, videoid, video=status)
        except Exception:
            return await message.reply_text(_["call_9"])
        button = telegram_markup(_, chat_id)
        run = await message.reply_text(
                text=_["stream_2"].format(
                  title,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    else:
        try:
            await LostMuzik.skip_stream(chat_id, queued, video=status)
        except Exception:
            return await message.reply_text(_["call_9"])
        if videoid == "telegram":
            button = telegram_markup(_, chat_id)
            run = await message.reply_text(
                text=_["stream_3"].format(
                    title, check[0]["dur"], user
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif videoid == "soundcloud":
            button = telegram_markup(_, chat_id)
            run = await message.reply_text(
                text=_["stream_3"].format(
                    title, check[0]["dur"], user
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        else:
            button = stream_markup(_, videoid, chat_id)
            img = None
            run = await message.reply_text(
                text=_["stream_1"].format(
                  title,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
