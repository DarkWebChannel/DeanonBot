#Made with love
# By KefRC
#❤❤❤❤❤❤❤❤

import requests
import telebot
from telebot import types

import phonenumbers
from phonenumbers import geocoder, carrier

VK_ACCESS_TOKEN = '0af157510af157510af15751aa0a89e69600af10af157516a0bc15996e74fe2b440998c' #не трогать если не знаешь
URL = "https://lookup.binlist.net/{}"
API_TOKEN = '' #@botfather

bot = telebot.TeleBot(API_TOKEN)

def get_bin_data(bin_number: str) -> dict:
    url = URL.format(bin_number)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '<b>Привет! Мои команды:</b>\n\n<b>/phone (НОМЕР) - Поиск по номеру(+7XXXXXXXXXX)</b>\n<b>/ip (IP АДРЕС)- поиск по IP</b>\n<b>/bin (BIN) - поиск по BIN</b>\n<b>/mac (MAC) - поиск по MAC адресу</b>\n<b>/vk (ВК ИД) - поиск по ВК</b>\n<b>/tg (TG ID) - поиск по ТГ</b>', parse_mode="HTML")

@bot.message_handler(commands=['vk'])
def get_vk_profile(message):
    try:
        argsvk = message.text.split()
        user_id = argsvk[1]
        
        url = f"https://api.vk.com/method/users.get?access_token={VK_ACCESS_TOKEN}&v=5.131&user_ids={user_id}&fields=first_name,last_name,status,sex,country,photo_max_orig"
        response = requests.get(url)
        data = response.json()
        
        if 'error' in data:
            bot.send_message(message.chat.id, 'Ошибка при получении данных. Проверьте правильность введенного ID пользователя.')
        else:
            user = data['response'][0]
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            status = user.get('status', '')
            sex = user.get('sex', '')
            country = user.get('country', {}).get('title', '')
            photo_url = user.get('photo_max_orig', '')
            
            text = f"<b>ID: {user_id}</b>\n<b>Профиль: vk.com/{user_id}</b>\n<b>Слежка за профилем: https://v1.220vk.ru/{user_id}</b>\n<b>Имя: {first_name}</b>\n<b>Фамилия: {last_name}</b>\n<b>Статус: {status}</b>\n<b>Пол: {sex}</b>\n<b>Страна: {country}</b>\n\n<b>ПОЛ:</b>\n<b>1 - ЖЕНСКИЙ</b>\n<b>2 - МУЖСКОЙ</b>"
            
            if photo_url:
                bot.send_photo(message.chat.id, photo_url, caption=text, parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка при получении данных. Попробуйте еще раз.')
        print(f'Error: {e}')

@bot.message_handler(commands=['tg'])
def get_profile(message):
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, введите телеграм ID.")
        return
    username = message.text.split()[1]
    url = f"https://api.telegram.org/bot{API_TOKEN}/getChat?chat_id={username}"
    response = requests.get(url)
    data = response.json()
    if data["ok"]:
        profile = data["result"]
        bot.send_message(message.chat.id, f"<b>ID: {profile.get('id', '')}\nИмя: {profile.get('first_name', '')}\nФамилия: {profile.get('last_name', '')}\nUsername: @{profile.get('username', '')}</b>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при получении профиля.")

@bot.message_handler(commands=['mac'])
def handle_text(message):
    argsmac = message.text.split()
    mac_address = argsmac[1]
    
    if not is_valid_mac_address(mac_address):
        bot.send_message(message.chat.id, '<b>Некорректный MAC-адрес</b>', parse_mode="HTML")
        return
    
    url = f'https://api.macvendors.com/{mac_address}'
    response = requests.get(url)
    
    if response.status_code == 200:
        vendor = response.text
        bot.send_message(message.chat.id, f'<b>Производитель: {vendor}</b>', parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, '<b>Произошла ошибка при получении данных</b>', parse_mode='HTML')

def is_valid_mac_address(mac_address: str) -> bool:
    return len(mac_address) == 17 and mac_address.count(':') == 5

@bot.message_handler(commands=['bin'])
def process_bin_number(message):
    binargs = message.text.split()
    bin_number = binargs[1]
    if len(bin_number) != 6 or not bin_number.isdigit():
        bot.send_message(message.chat.id, "<b>Некорректный BIN номер. Попробуйте снова.</b>", parse_mode="HTML")
        return

    data = get_bin_data(bin_number)
    if data:
        bank = data.get("bank", {}).get("name", "")
        card_type = data.get("type", "")
        bot.send_message(message.chat.id, f"<b>Банк: {bank}\nТип: {card_type}</b>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "<b>Не удалось получить информацию по BIN. Попробуйте снова.</b>", parse_mode="HTML")

@bot.message_handler(commands='phone')
def process_phone_number(message):
    try:
        args = message.text.split()
        phone_number = phonenumbers.parse(args[1])
        region = geocoder.description_for_number(phone_number, "ru")
        country = geocoder.country_name_for_number(phone_number, "ru")
        operator = carrier.name_for_number(phone_number, "ru")
        responser = f'📱\n<b>├ Номер:</b> {args[1]}\n<b>├ Страна: {country}</b>\n<b>└ Оператор: {operator}</b>\n\n<a href="https://t.me/{args[1]}">Telegram</a>\n\n<a href="https://api.whatsapp.com/send/?phone={args[1]}&text&type=phone_number&app_absent=0">Whatsapp</a>\n\n<a href="https://botapi.co/viber/{args[1]}?&gclid=19956348:8f27086a14274f584a3c2a5cc3660996&_bk=cloudflare">Viber</a>'
    except phonenumbers.phonenumberutil.NumberParseException:
        responser = "<b>Ошибка! Неверный формат номера телефона.</b>"

    bot.send_message(message.chat.id, responser, parse_mode="HTML")

@bot.message_handler(commands=['ip'])
def get_ip_info(message):
    ip = message.text.split('/ip ')[1]
    response = requests.get(f'https://ipapi.co/{ip}/json/')
    if response.status_code == 200:
        ip_data = response.json()
        bot.send_message(message.chat.id, f'<b>Информация об IP-адресе {ip}:\n'
                            f'Страна: {ip_data["country_name"]}\n'
                            f'Регион: {ip_data["region"]}\n'
                            f'Город: {ip_data["city"]}\n'
                            f'Почтовый индекс: {ip_data["postal"]}\n'
                            f'Координаты: {ip_data["latitude"]}, {ip_data["longitude"]}</b>', parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, '<b>Не удалось получить информацию об IP-адресе.</b>',parse_mode="HTML")

bot.polling()
