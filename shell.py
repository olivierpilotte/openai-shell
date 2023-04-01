
import logging
import openai
import os
import sys
import time

from history import Conversation, Queries


logging.basicConfig(
    stream=sys.stdout, level=logging.INFO,
    format="%(levelname)s - %(message)s")


MODEL = "gpt-3.5-turbo"
IMAGE_SIZE = "1024x1024"


BOLD = "\033[1m"
NORMAL = "\033[0m"

PRINT_DELAY = 0.03


conversation = Conversation()
queries = Queries()


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
            model=MODEL,
            messages=conversation.get(),
            stream=True,
        )

        ai_response = {"role": "system", "content": ""}

        print(f"\n{NORMAL}AI › ", end="")
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
            query = input(f"\n{BOLD}User › ")
        except EOFError:
            break

        if len(query) < 1:
            continue

        queries.write()

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
