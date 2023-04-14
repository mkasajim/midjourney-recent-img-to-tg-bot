import requests, json, os, re
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image
import imagehash
import schedule
import time
import urllib.parse
from telegram import InputFile, Bot, Update
from telegram.ext import Updater, CommandHandler
import asyncio

async def telegram_bot_sendimage_async(img_path):
    bot_token = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
    bot_chatID = os.getenv('CHAT_ID', 'YOUR_CHAT_ID')
    bot = Bot(token=bot_token)

    print(f"Sending image {img_path} to chat {bot_chatID}")

    try:
        with open(img_path, 'rb') as f:
            sent_message = await bot.send_photo(chat_id=bot_chatID, photo=f)

        if sent_message:
            print(f"Image {img_path} sent successfully")
            #print(sent_message)
        else:
            print(f"Error sending image {img_path}")

    except Exception as e:
        print(f"Exception occurred while sending image {img_path}: {e}")

    return sent_message

def telegram_bot_sendimage(img_path):
    asyncio.run(telegram_bot_sendimage_async(img_path))

def get_image_urls(url):
    urllist = []

    headers = {'User-Agent': 'curl/7.84.0'}
    page = requests.get(url, headers=headers, allow_redirects=True)
    soup = BeautifulSoup(page.content, 'html.parser')
    body = soup.find("body")
    sc = list(body.find_all("script"))[-1].string
    sc = str(sc)
    sc = json.loads(sc).get("props").get("pageProps").get("jobs")
    for i in sc:
        urllist.append(i.get("event").get("seedImageURL"))
    return urllist

def is_image_exists(img_path, directory, hash_func=imagehash.average_hash, threshold=5):
    target_hash = hash_func(Image.open(img_path))
    
    for existing_img_name in os.listdir(directory):
        if existing_img_name.endswith('.png'):
            existing_img_path = os.path.join(directory, existing_img_name)
            existing_hash = hash_func(Image.open(existing_img_path))
            if target_hash - existing_hash < threshold:
                return True
    return False

def download_image(urllist):
    img_directory = 'images'
    tmp_directory = 'tmp'
    os.makedirs(img_directory, exist_ok=True)
    os.makedirs(tmp_directory, exist_ok=True)

    headers = {'User-Agent': 'curl/7.84.0'}
    for url in urllist:
        page = requests.get(url, headers=headers, allow_redirects=True)
        img_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
        tmp_img_path = os.path.join(tmp_directory, img_name)

        with open(tmp_img_path, 'wb') as f:
            f.write(page.content)

        if not is_image_exists(tmp_img_path, img_directory):
            img_path = os.path.join(img_directory, img_name)
            os.rename(tmp_img_path, img_path)
            print(f"Downloaded {img_name}")
            telegram_bot_sendimage(img_path)  # Send the new image via Telegram bot
        else:
            os.remove(tmp_img_path)
            print(f"Image {img_name} already exists, not saved")

def main():
    url = 'https://www.midjourney.com/showcase/recents'
    url2 = 'https://www.midjourney.com/showcase/top'
    urllist1 = get_image_urls(url)
    urllist2 = get_image_urls(url2)

    unique = set()
    for i in urllist1:
        unique.add(i)
    for i in urllist2:
        unique.add(i)
    download_image(unique)

main()
schedule.every(1).hour.do(main)  # Run the main function every hour

while True:
    schedule.run_pending()
    time.sleep(1)
