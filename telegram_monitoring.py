from telethon import TelegramClient, events, sync
import telethon
import re
import argostranslate.package
import argostranslate.translate
from datetime import datetime
import telebot


#----------------------Check If Data is Today------------------------

def check_date(date_string):
    """Compares a date string to today's date and performs an action if they match."""

    try:
        # Parse the date string
        date_obj = datetime.strptime(str(date_string), "%Y-%m-%d").date()

        # Get today's date
        today = datetime.now().date()

        if date_obj == today:

            return True
        else:
           return False

    except ValueError:
        print(f"Invalid date format: {date_string}")
        
#----------------------Send Telegram Notification Message Via Telebot------------------------

def send_telegram_group_message(message):

    excel_file = "recent_messages.xlsx"

    """Sends a WhatsApp message to a group chat, checking against recent messages in an Excel file."""

    TOKEN = ''
    chat_id = ''

    bot = telebot.TeleBot(TOKEN)

    excel_file = "recent_messages.xlsx"
    # Load recent messages from Excel
    try:
        df = pd.read_excel(excel_file)
        recent_messages = df['Message'].tolist()
    except FileNotFoundError:
        recent_messages = []

    if message not in recent_messages:
        try:

            message_to_send = message

            print(message_to_send)

            bot.send_message(chat_id, message_to_send)

            print(f"Message sent successfully!")

            new_row_series = pd.Series({"Message": message})

            df = pd.concat([df, pd.DataFrame([new_row_series])], ignore_index=True)

            # Write the updated DataFrame back to the Excel sheet
            df.to_excel(excel_file, index=False)

        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Duplicate message detected. Not sending.")
        
#----------------------Convert Datetime string to Date------------------------

def convert_datetime(datetime_str):

    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")

    # Extract the date part
    date_part = datetime_obj.date()

    return date_part

#----------------------Language Translation------------------------

def translate_text(sentence):
    from_code = "ru"
    to_code = "en"

    # Download and install Argos Translate package
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())

    # Translate
    translatedText = argostranslate.translate.translate(sentence, from_code, to_code)

    return translatedText


# Replace with your API credentials from my.telegram.org
api_id = ''
api_hash = ''
phone_number = ''

#airline - авиакомпания
#aviation - авиация
#airport - аэропорт
#aerospace - аэрокосмический


channel_username_list = ['@hack_n3t']

search_keyword_list = ['авиакомпания', 'авиация', 'аэропорт', 'аэрокосмический']

CATEGORY_MAPPING = {
    'авиакомпания': "airline",
    'авиация': "aviation",
    'аэропорт': "airport",
    'аэрокосмический': "aerospace",
}

client = TelegramClient('session_name', api_id, api_hash)

async def main():

    await client.start(phone_number)

    df_list = []

    # ----------------------Loop for Checking Multiple Telegram Channels------------------------
    
    for channel_username in channel_username_list:

        df = pd.DataFrame()

        channel_username_lst = []
        match_keyword_list = []
        message_datetime_list = []
        message_date_list = []
        message_content_list = []
        url_list = []

        for search_keyword in search_keyword_list:

            try:

                async for message in client.iter_messages(channel_username, limit=1, search=search_keyword):

                    print(channel_username)

                    keyword = CATEGORY_MAPPING[search_keyword]

                    print(keyword)

                    date_part = convert_datetime(str(message.date))

                    print(date_part)

                    print(message.message)

                    translatedText = translate_text(message.message.replace("\n", "\t"))

                    url_pattern = r"(?i)\b((?:https?://|ftp://|www\.)\S+[^\s+\)])"

                    matches = re.findall(url_pattern, message.message)

                    url_lst = []

                    if matches:

                        for url in matches:

                            match_check_host = re.search("check-host.net", url)

                            if not match_check_host:

                                print(url)
                                url_lst.append(url)
                            else:
                                continue

                    notification_message =  str(channel_username) + "\n" + \
                                    "search keyword: " + str(keyword) + "\n" + \
                                    str(date_part) + "\n" + \
                                    str(message.date) +  "\n" + \
                                    str(translatedText.replace("\t", "\n")) + "\n" + \
                                    str(url_lst)

                    if check_date(date_part):

                        send_telegram_group_message(notification_message)

                    else:

                        print("no new chat......")

            except telethon.errors.rpcerrorlist.UsernameInvalidError:

                continue


        print("completed....")


with client:

    client.loop.run_until_complete(main())


