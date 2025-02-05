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

    def process(command) -> str:
        """Processes the command and returns an appropriate response."""
        if command == "/start" or command == "/help":
            return MESSAGES["start_help"]
        else:
            raise ProcessingError(MESSAGES["unknown_command"])
