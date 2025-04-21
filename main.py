import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultAudio
import requests
from io import BytesIO
import time

# Replace with your Telegram bot token and channel URL
BOT_TOKEN = "7048215725:AAEwP6mJiAMmDxVw1VmiiVtB6qA67L-mwkk"
CHANNEL_URL = "https://t.me/UdayScripts"  # Replace with your channel URL
API_URL = "https://music.udayscriptsx.workers.dev/?query="

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Command handler for /start
@bot.message_handler(commands=["start"])
def start(message):
    
    
    # Create an inline keyboard with buttons linking to the channel and inline search
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🌟 Join Our Channel", url=CHANNEL_URL),
        InlineKeyboardButton("🔍 Search Songs", switch_inline_query_current_chat="")
    )

    # Send the welcome message with Markdown styling and inline buttons
    bot.reply_to(
        message,
        "🎵 *Welcome to Music Downloader Bot!*\n"
        "_Send me a song name to download your favorite tracks 🎶_\n\n"
        "*⚠️ Note:* _This Bot Uses Jio Saavn API_\n\n"
        "_Join @BotBlast and @UdayScripts for more bots!_",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
 

# Message handler for song search and download
@bot.message_handler(func=lambda message: True)
def send_song(message):
    query = message.text.strip()  # Get the user's query
    if not query:
        bot.reply_to(message, "❌ Please provide a song name to search.")
        return

    songs = search_music(query)

    if not songs:
        bot.reply_to(message, "❌ No songs found. Try another query!")
        return

    song = songs[0]  # Get the first result
    media_url = song["media_url"]
    song_name = song["song"]
    singers = song["singers"]

    # Notify user about the download process
    downloading_message = bot.reply_to(message, f"⬇️ Downloading *{song_name}* by *{singers}*...", parse_mode="Markdown")

    try:
        # Fetch the MP3 file
        mp3_response = requests.get(media_url, timeout=10)  # Set timeout for the request
        if mp3_response.status_code == 200:
            # Send the MP3 file
            audio_file = BytesIO(mp3_response.content)
            audio_file.name = f"{song_name}.mp3"

            bot.send_audio(
                chat_id=message.chat.id,
                audio=audio_file,
                title=song_name,
                performer=singers,
                caption=f"🎶 *{song_name}* by *{singers}*", parse_mode="Markdown"
            )
            # Edit the downloading message to indicate success
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=downloading_message.message_id,
                text=f"✅ *{song_name}* downloaded successfully!", parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=downloading_message.message_id,
                text="❌ Unable to download the song. Try another!"
            )
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=downloading_message.message_id,
            text=f"❌ Error: {str(e)}"
        )

# Inline query handler for searching songs
@bot.inline_handler(func=lambda query: True)
def inline_search(query):
    user_query = query.query.strip()

    if not user_query:
        bot.answer_inline_query(
            query.id,
            results=[],
            switch_pm_text="Type a song name to search!",
            switch_pm_parameter="start",
            cache_time=1
        )
        return

    songs = search_music(user_query)

    if not songs:
        bot.answer_inline_query(
            query.id,
            results=[],
            switch_pm_text="No songs found!",
            switch_pm_parameter="start",
            cache_time=1
        )
        return

    # Prepare the inline query results
    results = [
        InlineQueryResultAudio(
            id=str(i),
            audio_url=song["media_url"],
            title=song["song"],
            performer=song["singers"]
        )
        for i, song in enumerate(songs)
    ]

    # Respond to the inline query
    bot.answer_inline_query(query.id, results, cache_time=1)

# Helper function to search for music
def search_music(query):
    try:
        response = requests.get(API_URL + query, timeout=5)  # Set a 5-second timeout
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching music: {e}")
    return []

# Start the bot
bot.infinity_polling()
print("Bot is running...")
