#!/usr/bin/env python3
"""
daily_telegram_bot.py
Simple daily Telegram sender with user input and weekend delivery.
Requires: requests, schedule
"""

import requests, schedule, time, logging
import os
from datetime import datetime
from pathlib import Path

# ------------- CONFIG -------------
BOT_TOKEN = os.getenv("BOT_TOKEN")   # replace with your token
CHAT_ID   = os.getenv("CHAT_ID")     # replace with your chat id (string or number)
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "08:00")  # 24-hour format
MESSAGE_FILE = "daily_message.txt"
LOG_FILE = "bot.log"
SEND_ON_START = os.getenv("SEND_ON_START", "false").lower() == "true"
# ----------------------------------

if not BOT_TOKEN or not CHAT_ID:
    print("ERROR: BOT_TOKEN and CHAT_ID must be set as environment variables.")
    exit(1)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def prompt_for_message():
    """Load or prompt for message"""
    p = Path(MESSAGE_FILE)
    if p.exists():
        msg = p.read_text(encoding='utf-8').strip()
        logging.info("Loaded message from %s", MESSAGE_FILE)
        return msg
    else:
        print("Enter your daily message (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        msg = "\n".join(lines).strip()
        if not msg:
            print("No message entered. Exiting.")
            logging.error("No message entered.")
            exit(1)
        return msg

def send_telegram_message(token, chat_id, message):
    """Send Telegram message"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": str(chat_id),
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, data=payload, timeout=15)
        if r.status_code == 200:
            logging.info("Message sent successfully.")
            return True
        else:
            logging.error("Failed to send message. Status %s, Response: %s", r.status_code, r.text)
            return False
    except Exception as e:
        logging.exception("Exception sending message: %s", e)
        return False

def job():
    """Daily message task"""
    global daily_message
    today = datetime.now().strftime("%A")
    message_to_send = daily_message

    # Weekend variations
    if today == "Saturday":
        message_to_send = f"🌞 Happy Weekend — ({today})!\n\nEnjoy your rest day traders!"
    elif today == "Sunday":
        message_to_send = f"🌞 Hey traders, Happy {today}!\n\nPrepare for a new week ahead 💹"

    logging.info(f"Sending message for {today}")
    sent = send_telegram_message(BOT_TOKEN, CHAT_ID, message_to_send)
    if sent:
        print(f"[{datetime.now()}] ✅ {today} message sent.")
    else:
        print(f"[{datetime.now()}] ❌ Failed to send {today} message. See {LOG_FILE} for details.")

if __name__ == "__main__":
    logging.info("Bot starting.")
    print("Starting daily Telegram bot...")

    # Validation
    if "YOUR_TELEGRAM_BOT_TOKEN" in BOT_TOKEN or "YOUR_CHAT_ID" in CHAT_ID:
        print("Please configure BOT_TOKEN and CHAT_ID correctly.")
        logging.error("BOT_TOKEN/CHAT_ID not configured.")
        exit(1)

    daily_message = prompt_for_message()

    # Schedule messages daily (Mon–Sun)
    schedule.every().day.at(SCHEDULE_TIME).do(job)

    print(f"✅ Bot scheduled to send daily (Mon–Sun) at {SCHEDULE_TIME}. Logs: {LOG_FILE}")
    logging.info("Scheduled job at %s", SCHEDULE_TIME)

    # Optional immediate send
    if SEND_ON_START:
        print("SEND_ON_START=true → Sending message now...")
        job()

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
        logging.info("Bot stopped by user.")
