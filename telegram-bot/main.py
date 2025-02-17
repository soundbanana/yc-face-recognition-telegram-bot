import json
import logging
import requests
import hashlib
from constants import MESSAGES, TELEGRAM_API_URL, BUCKET_PHOTOS_NAME
from helpers import ProcessingError, CommandHandler, MessageResponse
from bucket_service import save_original_photo_to_bucket

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_message(chat_id, text):
    """Sends a message to a given Telegram chat."""
    logger.info(f"Sending message to chat {chat_id}: {text}")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    return requests.post(url, data=data)

def get_message_id(processing_message):
    """Extracts the message ID from the Telegram response."""
    return processing_message.json().get("result", {}).get("message_id")

def delete_message(chat_id, message_id):
    """Deletes a specific message in Telegram."""
    url = f"{TELEGRAM_API_URL}/deleteMessage"
    data = {'chat_id': chat_id, 'message_id': message_id}
    r = requests.post(url, data=data)
    return r

def get_message_type(message, chat_id):
    """Processes the message and returns the appropriate response."""
    # Check if the message contains a photo
    if photo := message.get("photo"):  # If the message contains a photo
        return MessageResponse(photo, MessageResponse.PHOTO)
    elif text := message.get("text"):  # If the message contains text
        entities = message.get("entities", [])
        command_entity = next((e for e in entities if e.get("type") == "bot_command"), None)

        if command_entity:  # If the message is a command
            command = text[command_entity["offset"]:command_entity["offset"] + command_entity["length"]]
            return MessageResponse(command, MessageResponse.COMMAND)

        return MessageResponse(text, MessageResponse.TEXT)

    raise ProcessingError(MESSAGES["incorrect_input"])

def process_message(message, chat_id) -> None:
    """Processes the incoming message and responds accordingly."""
    try:
        response = get_message_type(message, chat_id)

        logger.info(response)

        if response.is_command():
            command_message = CommandHandler.process(response.message)
            send_message(chat_id, command_message)
            return

        elif response.is_text():
            send_message(chat_id, "Отправлен текст")
        
        elif response.is_photo():
            file_id = message['photo'][-1]['file_id']
            
            send_message(chat_id, f"Отправлена фотография {file_id}")
            save_original_photo_to_bucket(BUCKET_PHOTOS_NAME, file_id)

    except ProcessingError as e:
        logger.error(f"Processing error: {e}")
        send_message(chat_id, str(e))

def handler(event, context):
    """Handles the incoming event from Telegram and processes the message."""
    try:
        body = json.loads(event['body'])
        message = body.get("message")

        if not message:
            return {"statusCode": 200, "body": MESSAGES["no_message"]}

        chat_id = message["from"]["id"]
        logger.info(f"Received message from chat {chat_id}: {message}")

        # Process the message
        process_message(message, chat_id)

        return {"statusCode": 200, "body": "Message processed."}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"statusCode": 500, "body": f"{MESSAGES['error']}: {str(e)}"}
