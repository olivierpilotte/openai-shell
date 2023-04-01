
import json
import os
import logging
import readline


HOME_DIR = os.path.expanduser('~')
QUERY_HISTORY_PATH = f"{HOME_DIR}/.openai_query_history"
CONVERSATION_HISTORY_PATH = f"{HOME_DIR}/.openai_conversation_history"


class Conversation():

    def __init__(self):
        self._converstion_history = []
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


class Queries():
    def __init__(self):
        readline.parse_and_bind("tab: complete")

        self.query_history = []
        try:
            readline.read_history_file(QUERY_HISTORY_PATH)

        except FileNotFoundError:
            pass

    def write(self):
        readline.write_history_file(QUERY_HISTORY_PATH)
