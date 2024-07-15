from telethon import TelegramClient, events, sync
import re
import argostranslate.package
import argostranslate.translate
import pandas as pd
from datetime import datetime
import google.generativeai as genai

#----------------------Check Year against Desired Year------------------------
def check_year(datetime_str):
    """Compares a date string to today's date and performs an action if they match."""

    try:
        datetime_obj = datetime.strptime(str(datetime_str), "%Y-%m-%d %H:%M:%S%z")

        # Extract the year from the datetime object
        year = datetime_obj.year

        if year == 2024:

            return True
        else:
           return False

    except ValueError:
        print(f"Invalid date format: {date_string}")

#----------------------Gemini GenAI Summarization------------------------
def gemini_summarize(outputfilename, text):

    genai.configure(api_key="")

    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    query = "help me to analyze the following telegram messages and summarize into \"hacktivist groups involved\", \"list of all organizations with associated countries in bracket and dates in square bracket \", \"motives\" and \"tactics\" - " \
            + str(text)

    response = model.generate_content(query)

    try:

        print(response.text)

    except ValueError:

        print("error printing response text")


    #with open(outputfilename, "w") as file:
    with open(outputfilename, "w", encoding="utf-8") as file:
        #print(response.text, file=file)
        file.write(response.text)

    return

#----------------------Convert Datetime String to Date------------------------

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

search_keyword_list = ['авиакомпания', 'авиация', 'аэропорт', 'аэрокосмический']

CATEGORY_MAPPING = {
    'авиакомпания': "airline",
    'авиация': "aviation",
    'аэропорт': "airport",
    'аэрокосмический': "aerospace",
}

channel_username = "@hack_n3t"

client = TelegramClient('session_name', api_id, api_hash)

async def main():

    await client.start(phone_number)

    df_list = []


    df = pd.DataFrame()

    channel_username_lst = []
    match_keyword_list = []
    message_datetime_list = []
    message_date_list = []
    message_content_list = []
    url_list = []

    for search_keyword in search_keyword_list:

        async for message in client.iter_messages(channel_username, search=search_keyword):

            if check_year(message.date):

                print(channel_username)

                keyword = CATEGORY_MAPPING[search_keyword]

                print(keyword)

                date_part = convert_datetime(str(message.date))

                print(date_part)

                translatedText = translate_text(message.message.replace("\n", "\t"))

                print(str(message.date) + "\t" + str(translatedText))


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

                channel_username_lst.append(channel_username)
                match_keyword_list.append(keyword)
                message_datetime_list.append(str(message.date))
                message_date_list.append(date_part)
                message_content_list.append("(" + str(message.date) + ") " + str(translatedText))
                url_list.append(url_lst)

            else:

                continue

    df["channel"] = channel_username_lst
    df["Match keyword"] = match_keyword_list
    df["Message datetime"] = message_datetime_list
    df["Message date"] = message_date_list
    df["Message Content"] = message_content_list
    df["URL"] = url_list

    print("############################################################################")

    collapsed_text = '\n'.join(df['Message Content'])

    print(collapsed_text)

    print("############################################################################")

    outputfilename = channel_username.replace("@", "") + str(".txt")

    gemini_summarize(outputfilename, collapsed_text)

    outputfilename_msg_excel = channel_username.replace("@", "") + str(".xlsx")

    df.to_excel(outputfilename_msg_excel, index=False)
    
    print("completed....")

with client:

    client.loop.run_until_complete(main())


