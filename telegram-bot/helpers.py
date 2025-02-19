from constants import MESSAGES

# Custom error class to handle errors
class ProcessingError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class MessageResponse:
    """Represents a structured message response with a type and message content."""
    
    TEXT = "text"
    PHOTO = "photo"
    COMMAND = "command"
    
    def __init__(self, message: str, response_type: str):
        self.message = message
        self.response_type = response_type

    def is_command(self):
        return self.response_type == self.COMMAND

    def is_text(self):
        return self.response_type == self.TEXT
    
    def is_photo(self):
        return self.response_type == self.PHOTO
    

class CommandHandler:
    """Handles incoming commands."""
    
    def __init__(self, command):
        self.command = command

    def process(command):
        from bucket_service import process_getface_command, find_faces_by_name
        """Processes the command and returns an appropriate response."""
        if command == "/start" or command == "/help":
            return MESSAGES["start_help"]
        elif command == "/getface":
            photo_url, error = process_getface_command()
            if error:
                raise ProcessingError(error)
            elif error == None:
                print(photo_url)
                print(123)
                return photo_url
        elif command.startswith("/find"):
            parts = command.split(maxsplit=1)
            print(parts)
            if len(parts) < 2:
                raise ProcessingError("Укажите имя после команды /find")

            name = parts[1].strip()
            if not name:
                raise ProcessingError("Укажите имя после команды /find")

            photo_urls = find_faces_by_name(name)
            print(photo_urls)
            return photo_urls
        else:
            raise ProcessingError(MESSAGES["unknown_command"])
