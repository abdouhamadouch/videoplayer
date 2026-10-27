import asyncio
import logging

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
for noisy in ("pytgcalls", "pyrogram", "ntgcalls"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
for ours in ("program", "driver", "__main__"):
    logging.getLogger(ours).setLevel(logging.INFO)
log = logging.getLogger(__name__)

from pytgcalls import idle
from pyrogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats
from pyrogram.errors import FloodWait
from driver.clients import call_py, bot
from driver.queues import load_resume, load_topic_lock
from program.resume import track_position
from program.radio import radio_updater
import program.iptv

BOT_COMMANDS = [
    BotCommand("play", "play music from YouTube, or reply to an audio"),
    BotCommand("vplay", "play video from YouTube, or reply to a video"),
    BotCommand("vstream", "stream a live / m3u8 / YouTube link"),
    BotCommand("search", "search YouTube and pick a result to play"),
    BotCommand("library", "browse the local media library + web-sourced cartoons"),
    BotCommand("lplay", "play a local library file by name"),
    BotCommand("radio", "tune in to an internet radio station"),
    BotCommand("iptv", "search and stream live TV channels (iptv-org catalogue)"),
    BotCommand("topic", "restrict the bot to one forum topic: lock|unlock|status"),
    BotCommand("record", "record audio/video; /record 01:30 02:00 to clip a range"),
    BotCommand("stoprec", "stop the current recording and send it"),
    BotCommand("pause", "pause playback (admin)"),
    BotCommand("resume", "resume playback (admin)"),
    BotCommand("continue", "resume the last track from where it stopped"),
    BotCommand("skip", "skip to the next track (admin)"),
    BotCommand("loop", "toggle repeat of the current track (admin)"),
    BotCommand("autoplay", "auto-DJ: keep playing related tracks when the queue ends"),
    BotCommand("shuffle", "shuffle the upcoming queue (admin)"),
    BotCommand("clear", "clear upcoming tracks, keep current (admin)"),
    BotCommand("stop", "stop and leave the voice chat (admin)"),
    BotCommand("seek", "jump to a time in the current track, e.g. /seek 12:30"),
    BotCommand("vmute", "mute the assistant in the voice chat"),
    BotCommand("vunmute", "unmute the assistant in the voice chat"),
    BotCommand("playlist", "show the current queue"),
    BotCommand("info", "now playing + controls"),
    BotCommand("screenshot", "screenshot the current video"),
    BotCommand("help", "show the command list"),
    BotCommand("song", "download a song from YouTube"),
    BotCommand("video", "download a video from YouTube"),
    BotCommand("userbotjoin", "make the assistant join this group"),
    BotCommand("userbotleave", "make the assistant leave this group"),
    BotCommand("ping", "check if the bot is alive"),
    BotCommand("alive", "bot status"),
    BotCommand("uptime", "bot uptime"),
]

async def heartbeat():
    while True:
        try:
            with open("/tmp/heartbeat", "w") as f:
                f.write("ok")
        except OSError:
            pass
        await asyncio.sleep(30)

async def start_bot():
    log.info("starting bot client")
    while True:
        try:
            await bot.start()
            break
        except FloodWait as e:
            wait = int(getattr(e, "value", 0)) + 5
            log.error(
                "Telegram rate-limited bot login for %ss. Keeping this process alive until the wait ends; "
                "do not repeatedly redeploy or restart during this period.",
                wait,
            )
            await asyncio.sleep(wait)
        except Exception:
            log.exception("Bot client failed to start. Check BOT_TOKEN, API_ID, API_HASH, and Telegram login limits.")
            raise

    try:
        await bot.set_bot_commands(BOT_COMMANDS)
        await bot.set_bot_commands(BOT_COMMANDS, scope=BotCommandScopeAllGroupChats())
        await bot.set_bot_commands(BOT_COMMANDS, scope=BotCommandScopeAllPrivateChats())
        log.info("bot commands registered")
    except Exception:
        log.exception("Could not register bot commands; continuing startup")

    load_resume()
    load_topic_lock()
    asyncio.create_task(heartbeat())
    asyncio.create_task(track_position())
    asyncio.create_task(radio_updater())

    log.info("starting PyTgCalls assistant client")
    try:
        await call_py.start()
        log.info("PyTgCalls assistant client started; voice/video streaming is available")
    except Exception as e:
        if type(e).__name__ == "AuthKeyDuplicated":
            log.error(
                "SESSION_NAME is invalidated because the same Telegram assistant session is active in another process. "
                "Stop every other copy using this session string, then restart this Render service. "
                "Do not create or share a new session string unless the existing one is confirmed unusable."
            )
        else:
            log.exception("PyTgCalls assistant client failed to start; bot commands may work, but voice/video streaming will not.")
        # Keep the bot command client alive so /help and diagnostics remain available.
    try:
        await idle()
    finally:
        log.info("stopping bot and assistant clients")
        try:
            await call_py.stop()
        except Exception:
            log.exception("Error stopping PyTgCalls client")
        try:
            await bot.stop()
        except Exception:
            log.exception("Error stopping bot client")

if __name__ == "__main__":
    asyncio.run(start_bot())
