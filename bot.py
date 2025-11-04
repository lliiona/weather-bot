import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные из .env
load_dotenv()

# Читаем ключи из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из .env
API_KEY = os.getenv("API_KEY")      # Ключ OpenWeatherMap из .env

if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в переменных окружения (.env)")
if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения (.env)")

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = f"""
Привет, {user.first_name}! 🌤️

Я бот погоды. Вот что я умею:

/start - начать работу
/help - помощь
/weather - погода в Санкт-Петербурге
/weather <город> - погода в любом городе

Например: /weather Москва
    """
    await update.message.reply_text(welcome_text)

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 Доступные команды:

/start - начать работу
/help - помощь
/weather - погода в Санкт-Петербурге
/weather <город> - погода в указанном городе

🌤️ Примеры:
/weather
/weather Москва
/weather London
    """
    await update.message.reply_text(help_text)

# Команда /weather
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Если указан город, используем его, иначе - Санкт-Петербург
        if context.args:
            city = " ".join(context.args)
        else:
            city = "Saint Petersburg"
        
        # Параметры для запроса к API погоды
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru",
        }
        
        # Отправляем запрос к API
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        response.raise_for_status()  # проверяем ошибки HTTP
        data = response.json()
        
        # Форматируем время восхода и заката
        sunrise_timestamp = data["sys"]["sunrise"]
        sunset_timestamp = data["sys"]["sunset"]
        
        sunrise_time = datetime.fromtimestamp(sunrise_timestamp).strftime('%H:%M')
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime('%H:%M')
        
        # Формируем красивое сообщение о погоде
        weather_text = f"""
🌤️ Погода в {data['name']}:

📝 Состояние: {data["weather"][0]["description"].capitalize()}
🌡️ Температура: {data["main"]["temp"]}°C
💧 Влажность: {data["main"]["humidity"]}%
🌬️ Давление: {data["main"]["pressure"]} гПа
💨 Ветер: {data["wind"]["speed"]} м/с
🌅 Восход: {sunrise_time}
🌇 Закат: {sunset_time}
        """
        
        await update.message.reply_text(weather_text)
        
    except requests.exceptions.HTTPError:
        await update.message.reply_text("❌ Город не найден. Проверьте название города.")
    except Exception as e:
        await update.message.reply_text("❌ Произошла ошибка при получении погоды.")
        print(f"Ошибка: {e}")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if 'погода' in text:
        await update.message.reply_text("Используйте команду /weather для получения погоды 🌤️")
    elif 'привет' in text:
        await update.message.reply_text("Привет! 👋 Используйте /help для списка команд")
    else:
        await update.message.reply_text("Не понял вас... Используйте /help для списка команд")

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

def main():
    # Создаем приложение бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather_command))
    
    # Добавляем обработчики сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    app.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот погоды запущен...")
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()