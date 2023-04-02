
import json
import os
import logging


CONVERSATION_HISTORY_PATH = f"{os.path.expanduser('~')}/.openai_conversation_history"


class Conversation():

    def __init__(self):
        self.conversation_history = []
        if os.path.isfile(CONVERSATION_HISTORY_PATH):
            try:
                with open(CONVERSATION_HISTORY_PATH, "r") as file:
                    self.conversation_history = json.loads(file.read())

            except Exception:
                pass

    def get(self):
        return self.conversation_history

    def append(self, item):
        logging.debug(f"adding to conversation history: {item}")
        self.conversation_history.append(item)
        with open(CONVERSATION_HISTORY_PATH, "w") as file:
            file.write(json.dumps(self.conversation_history))

    def flush(self):
        self.conversation_history = []
        with open(CONVERSATION_HISTORY_PATH, "w") as file:
            file.write("")
