import os
import pytube
from telebot import TeleBot
from telebot import types
from config import API_TOKEN


bot = TeleBot(API_TOKEN)
yt = None


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Greet user after /start or /help command"""

    name = f'{message.from_user.first_name} + {message.from_user.last_name}'.title() if message.from_user.last_name \
        else f'{message.from_user.first_name}'.title()
    welcome_message = f"Hi, {name}!\nSend me a link to a YouTube video and I'll download it for you."
    bot.send_message(message.chat.id, welcome_message)

    # Remove all .mp4 files
    dir_name = "/Users/nurto/PycharmProjects/YouTube Bot"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".mp4"):
            os.remove(os.path.join(dir_name, item))


def youtube_download(message, path, call):
    """Dowmload YouTube video by pytube"""

    if call == 'High':
        bot.send_message(message.chat.id, 'Loading...')
        video_path = path.streams.get_highest_resolution().download()
        video = open(video_path, 'rb')

        bot.send_video(message.chat.id, video)
    else:
        bot.send_message(message.chat.id, 'Loading...')
        video_path = path.streams.first().download()
        video_path_copy = video_path.split('\\')[-1]
        name = video_path_copy.split('.')[0]
        result = name + '.mp4'
        os.rename(video_path, result)
        video = open(result, 'rb')

        bot.send_video(message.chat.id, video)


@bot.message_handler(content_types=['text'])
def get_message(message):
    """Get link from YouTube"""

    dir_name = "/Users/nurto/PycharmProjects/YouTube Bot"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".mp4"):
            os.remove(os.path.join(dir_name, item))

    try:
        global yt
        yt = pytube.YouTube(message.text)

    except pytube.exceptions.RegexMatchError:
        error_message = "It doesn't look like a YouTube video link :(\nTry again."
        bot.send_message(message.chat.id, error_message)

    keyboard = types.InlineKeyboardMarkup()
    high = types.InlineKeyboardButton('High', callback_data='High')
    low = types.InlineKeyboardButton('Low', callback_data='Low')
    keyboard.add(high, low)
    bot.send_message(message.chat.id, 'Choose resolution:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: True)
def download(callback):
    """Get callback data and call youtube_download"""

    youtube_download(callback.message, yt, callback.data)


bot.infinity_polling()
