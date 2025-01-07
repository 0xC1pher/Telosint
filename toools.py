import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import json
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("monitor.log"),  # Guardar logs en un archivo
        logging.StreamHandler(),  # Mostrar logs en la consola
    ],
)

# Cargar configuración desde un archivo JSON
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Datos de autenticación de Telethon
API_ID = config["api_id"]
API_HASH = config["api_hash"]
TARGET_USERS = config["target_users"]  # Lista de usuarios a monitorear
OUTPUT_FILE = "monitored_messages.json"  # Archivo para guardar los mensajes encontrados

async def search_messages_in_dialog(client, dialog):
    """Busca mensajes de los usuarios objetivo en un diálogo específico."""
    if dialog.is_group or dialog.is_channel:
        try:
            logging.info(f"Buscando en: {dialog.name} (ID: {dialog.id})")
            for target_user in TARGET_USERS:
                async for message in client.iter_messages(dialog.id, from_user=target_user):
                    # Guardar el mensaje encontrado
                    save_message(message, dialog.name)
        except Exception as e:
            if "Chat admin privileges" in str(e):
                logging.warning(f"No tienes privilegios de administrador en {dialog.name}.")
            else:
                logging.error(f"Error al buscar en {dialog.name}: {e}")

def save_message(message, chat_name):
    """Guarda un mensaje en un archivo JSON."""
    message_data = {
        "chat_name": chat_name,
        "sender": message.sender_id,
        "text": message.text,
        "date": message.date.isoformat(),
    }
    with open(OUTPUT_FILE, "a") as f:
        f.write(json.dumps(message_data) + "\n")
    logging.info(f"Mensaje guardado: {message.text}")

async def search_messages_from_user(client):
    """Busca mensajes de los usuarios objetivo en todos los diálogos accesibles."""
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        await search_messages_in_dialog(client, dialog)

async def main():
    """Función principal para iniciar la sesión y ejecutar la búsqueda."""
    client = TelegramClient("my_session", API_ID, API_HASH)
    
    await client.start()
    logging.info("Conexión exitosa.")
    
    me = await client.get_me()
    logging.info(f"Conectado como: {me.username}")
    
    await search_messages_from_user(client)
    
    await client.disconnect()
    logging.info("Búsqueda completada.")

if __name__ == "__main__":
    asyncio.run(main())
