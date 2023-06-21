
import json
import os
import logging


CONVERSATION_HISTORY_PATH = \
    f"{os.path.expanduser('~')}/.cache/openai_shell_conversation_history"
DIVIDER_WIDTH = 80


class Conversation():

    def __init__(self):
        self.conversation_history = []
        if os.path.isfile(CONVERSATION_HISTORY_PATH):
            try:
                with open(CONVERSATION_HISTORY_PATH, "r+") as file:
                    self.conversation_history = json.loads(file.read())

            except Exception:
                pass

    def get(self):
        return self.conversation_history

    def print(self):
        print("-" * DIVIDER_WIDTH)

        for item in self.conversation_history:
            role = item.get("role")
            role = "User" if role == "user" else "AI"
            content = item.get("content")

            print(f"{role}: {content}")
            print("")

        print("-" * DIVIDER_WIDTH)

    def append(self, item: str):
        logging.debug(f"adding to conversation history: {item}")
        self.conversation_history.append(item)
        with open(CONVERSATION_HISTORY_PATH, "w+") as file:
            file.write(json.dumps(self.conversation_history))

    def flush(self):
        self.conversation_history = []
        with open(CONVERSATION_HISTORY_PATH, "w+") as file:
            file.write("")
