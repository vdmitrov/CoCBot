import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Токены (замени на актуальные)
TELEGRAM_BOT_TOKEN = "7930052685:AAHh_3Cl86M3p6u70BThTCbE6rDQKOiDt8s"
COC_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjgwZTY2MGMxLTc4YjgtNDYwNS1hZDExLThkZWViMjU4YWI2NyIsImlhdCI6MTczOTQzNTMxNCwic3ViIjoiZGV2ZWxvcGVyLzQ2YTUwN2JhLTNjMDItZDZjNy1hMTM1LTA2MTA5YzEyZDE2MCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjIxMy4xNzQuMjkuMjEiXSwidHlwZSI6ImNsaWVudCJ9XX0.Bfs3nh0cnfXxAfHzNIEbTCIiimhoAvq1IgylqcBMV2X07bBsV7FvzmLhttvpBZwOsDkt4uzrxVC8xTxii9prNA"
CLAN_TAG = "#2GCG2C0YP"

# Создание бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Функция для получения информации о клане
async def get_clan_data():
    url = f"https://api.clashofclans.com/v1/clans/{CLAN_TAG.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logging.info(f"Запрос к API: {url}, Статус-код: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    logging.info(f"Данные получены: {data}")
                    return data
                else:
                    logging.error(f"Ошибка API: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logging.exception("Ошибка при запросе к API")
            return None

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer("Привет! Используй /info, чтобы получить информацию о клане.")

# Обработчик команды /info
@dp.message(Command("info"))
async def send_clan_info(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} запросил /info")

    data = await get_clan_data()
    if data:
        clan_name = data.get("name", "Неизвестно")
        members = data.get("memberList", [])

        player_list = []
        for player in members:
            name = player.get("name", "Без имени")
            role = player.get("role", "member")
            level = player.get("expLevel", "?")
            townhall = player.get("townHallLevel", "?")
            trophies = player.get("trophies", "?")

            role_emoji = {
                "leader": "👑",
                "coLeader": "⭐",
                "elder": "🛡",
                "member": "🔹"
            }.get(role, "❓")

            player_list.append(f"{role_emoji} {name} (⭐ {level}, 🏠 {townhall}, 🏆 {trophies})")

        text = f"🏰 **Клан {clan_name}**\n👥 Участники: {len(members)}\n\n" + "\n".join(player_list)
        await message.answer(text, parse_mode="Markdown")
    else:
        logging.error("Ошибка получения данных о клане")
        await message.answer("Ошибка: не удалось получить данные о клане 😢")

# Запуск бота
async def main():
    logging.info("Бот запущен и ожидает команды")
    await bot.delete_webhook(drop_pending_updates=True)  # Чистка очереди
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
