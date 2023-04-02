
import logging
import openai
import os
import sys
import time

from history import Conversation

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style


BOLD = Style.from_dict({"": "bold"})
IMAGE_SIZE = "1024x1024"
QUERY_HISTORY_PATH = f"{os.path.expanduser('~')}/.openai_query_history"
OPEN_AI_MODEL = "gpt-3.5-turbo"
PRINT_DELAY = 0.03


logging.basicConfig(
    stream=sys.stdout, level=logging.INFO,
    format="%(levelname)s - %(message)s")

session = PromptSession(history=FileHistory(QUERY_HISTORY_PATH))
conversation = Conversation()
openai.api_key = os.getenv("OPENAI_API_KEY")


def _query_dalle(query):
    response = openai.Image.create(
        prompt=query, n=1, size=IMAGE_SIZE
    )

    image_url = response["data"][0]["url"]
    print(f"\nImage: {image_url}")


def _query_openai(query, retries=1):
    conversation.append({"role": "user", "content": query})

    try:
        stream = openai.ChatCompletion.create(
            model=OPEN_AI_MODEL,
            messages=conversation.get(),
            stream=True,
        )

        ai_response = {"role": "system", "content": ""}

        print("\nAI › ", end="")
        for response in stream:
            if not hasattr(response.choices[0].delta, "content"):
                continue

            content = response.choices[0].delta.content
            ai_response["content"] += content

            print(content, end="", flush=True)
            time.sleep(PRINT_DELAY)

        conversation.append(ai_response)

    except Exception as e:
        if retries > 0:
            retries -= 1
            _query_openai(query, retries=retries)

        else:
            print(f"\nSystem › There was an issue querying openai: {e}")

    print("")


def main_loop():
    while True:
        try:
            query = session.prompt("User › ", style=BOLD)

        except EOFError:
            break

        if len(query) < 1:
            continue

        if query.startswith("image:"):
            _query_dalle(query.replace("image:", ""))
            continue

        match query:
            case "flush":
                conversation.flush()
                continue

            case "history":
                print(conversation.get())
                continue

            case _:
                _query_openai(query)


if __name__ == "__main__":
    try:
        main_loop()

    except KeyboardInterrupt:
        pass
