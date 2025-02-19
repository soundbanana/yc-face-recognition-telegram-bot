import json
import logging
import requests
import hashlib
from constants import MESSAGES, TELEGRAM_API_URL
from helpers import ProcessingError, CommandHandler, MessageResponse
from bucket_service import save_original_photo_to_bucket, rename_face

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_message(chat_id, text):
    """Sends a message to a given Telegram chat."""
    logger.info(f"Sending message to chat {chat_id}: {text}")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    return requests.post(url, data=data)

def send_photo(chat_id, photo_url, caption):
    url = f"{TELEGRAM_API_URL}/sendPhoto"
    print(photo_url)
    data = {'chat_id': chat_id, 'photo': photo_url, 'caption': caption}
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

def get_message_type(message):
    """Processes the message and returns the appropriate response."""
    # Check if the message contains a photo
    if photo := message.get("photo"):  # If the message contains a photo
        return MessageResponse(photo, MessageResponse.PHOTO)
    elif text := message.get("text"):  # If the message contains text
        entities = message.get("entities", [])
        command_entity = next((e for e in entities if e.get("type") == "bot_command"), None)

        if command_entity:  # If the message is a command
            return MessageResponse(text, MessageResponse.COMMAND)

        return MessageResponse(text, MessageResponse.TEXT)

    raise ProcessingError(MESSAGES["incorrect_input"])

def process_message(message, chat_id):
    """Processes the incoming message and responds accordingly."""
    try:
        response = get_message_type(message)

        logger.info(response)

        if response.is_command():
            command_message = CommandHandler.process(response.message)

            if command_message == MESSAGES["start_help"]:
                send_message(chat_id, command_message)
            elif response.message.startswith("/find"):
                for message in command_message:
                    send_photo(chat_id, f"{message}", "")
            elif response.message.startswith("/getface"):
                send_photo(chat_id, command_message, f"Ответом на это сообщение пришлите как зовут этого человека\n{command_message.split("?key=")[1]}")
            return

        elif response.is_text():
            if reply_message := message.get("reply_to_message", {}):
                name = message.get("text")
                file_id = reply_message.get("caption").split("\n")[1]

                if not file_id:
                    raise ProcessingError("Я ничего не понял. Попробуйте еще раз")

                rename_face(name, file_id)
                send_message(chat_id, f"Теперь его зовут {name}.\n Можешь проверить написав /find {name}")    
                return
            else:
                send_message(chat_id, "Отправлен текст")
                return
        
        elif response.is_photo():
            file_id = message['photo'][-1]['file_id']
            
            send_message(chat_id, f"Отправлена фотография {file_id}")
            save_original_photo_to_bucket(file_id)
            return

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
