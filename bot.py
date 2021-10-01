# Part of < https://github.com/xditya/TelegraphUploader >
# (c) 2021 @xditya.

import os
import logging
from PIL import Image
from telethon import TelegramClient, events, Button
from telethon.tl.functions.users import GetFullUserRequest
from decouple import config
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telegraph import Telegraph, exceptions, upload_file

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

appid = apihash = bottoken = None
# start the bot
print("Starting...")
try:
    apiid = config("API_ID", cast=int)
    apihash = config("API_HASH")
    bottoken = config("BOT_TOKEN")
except:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quiting...")
    exit()

if (apiid != None and apihash!= None and bottoken != None):
    try:
        BotzHub = TelegramClient('bot', apiid, apihash).start(bot_token=bottoken)
    except Exception as e:
        print(f"ERROR!\n{str(e)}")
        print("Bot is quiting...")
        exit()
else:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quiting...")
    exit()

# join check
async def get_user(id):
    ok = True
    try:
        await BotzHub(GetParticipantRequest(channel='@SFCorpChannel', participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok

@BotzHub.on(events.NewMessage(incoming=True, pattern="/start", func=lambda e: e.is_private))
async def start(event):
    ok = await BotzHub(GetFullUserRequest(event.sender_id))
    await event.reply(f"Hello {ok.user.first_name}!\nI'm SF telegraph Uploader bot.",
                     buttons=[
                         Button.inline("Help", data="help"),
                         Button.url("More Bots", url="https://t.me/SFCorpChannel/8")
                     ])

@BotzHub.on(events.callbackquery.CallbackQuery(data="help"))
async def _(event):
    ok = await BotzHub(GetFullUserRequest(event.sender_id))
    if (await get_user(event.sender_id)) == False:
        return await event.edit(f"{ok.user.first_name}, Tolong join ke Channel untuk menggunakan bot ini!", buttons=[Button.url("Join Channel", url="https://t.me/SFCorpChannel")])
    await event.edit(f"Kirim saya gambar dan Saya akan upload ke Telegraph!\n\n~[@SF Corp](https://t.me/SFCorpChannel)")

@BotzHub.on(events.NewMessage(incoming=True, func=lambda e: e.is_private and e.media))
async def uploader(event):
    if (await get_user(event.sender_id)) is False:
        return
    TMP_DOWNLOAD_DIRECTORY = "./BotzHub/"
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    pic = event.media
    ok = await event.reply("`Uploading...`")
    downloaded_file_name = await BotzHub.download_media(pic, TMP_DOWNLOAD_DIRECTORY)
    if downloaded_file_name.endswith((".webp")):
        await ok.edit("`Oh! Itu sebuah sticker...\nConvret dulu!!`")
        resize_image(downloaded_file_name)
    try:
        media_urls = upload_file(downloaded_file_name)
    except exceptions.TelegraphException as exc:
        await ok.edit("**Error : **" + str(exc))
        os.remove(downloaded_file_name)
        return
    else:
        os.remove(downloaded_file_name)
        await ok.edit("Uploaded to **Telegraph**\n\n       Klik link di bawah untuk mengcopy👇🏻👇🏻👇🏻\n```url=f"https://telegra.ph{media_urls[0]}"```\n\n~[@SF Corp](https://t.me/SFCorpChannel)",
                    link_preview=False,
                    buttons=[
                        Button.url("Link To File", url=f"https://telegra.ph{media_urls[0]}")
                    ])

def resize_image(image):
    im = Image.open(image)
    tmp = im.save(image, "PNG")

print("Bot has started.")
print("Do visit @SFCorpChannel..")
BotzHub.run_until_disconnected()
