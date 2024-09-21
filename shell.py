#!/usr/bin/env python

import argparse
import logging
import os
import sys

import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from model import Conversation


API_KEY = os.getenv("OPENAI_API_KEY", None)
BOLD = Style.from_dict({"": "bold"})
DEFAULT_RETRIES = 1
IMAGE_SIZE = "1024x1024"
OPEN_AI_DEFAULT_MODEL = "gpt-3.5-turbo-16k"
QUERY_HISTORY_PATH = \
    f"{os.path.expanduser('~')}/.cache/openai_shell_query_history"

session = PromptSession(history=FileHistory(QUERY_HISTORY_PATH))
conversation = Conversation()


def _query_dalle(query: str):
    response = openai.Image.create(
        prompt=query, n=1, size=IMAGE_SIZE
    )

    image_url = response["data"][0]["url"]
    print(f"\nImage: {image_url}")


def _query_openai(model: str, query: str, retries: int):
    conversation.append({"role": "user", "content": query})

    try:
        stream = openai.ChatCompletion.create(
            model=model,
            messages=conversation.get(),
            stream=True,
            max_tokens=1024,
        )

        ai_response = {"role": "system", "content": ""}

        print("\nAI › ", end="")
        for response in stream:
            if not hasattr(response.choices[0].delta, "content"):
                continue

            content = response.choices[0].delta.content
            ai_response["content"] += content

            print(content, end="", flush=True)

        conversation.append(ai_response)

        print("")

    except Exception as e:
        print(f"\nSystem › There was an issue querying openai: {e}")

        if retries > 0:
            print("")
            retries -= 1
            _query_openai(model, query, retries)

    print("")


def main(model: str, query: str = None, retries: int = DEFAULT_RETRIES):
    try:
        if not query:
            query = session.prompt("User › ", style=BOLD)

    except EOFError:
        exit(0)

    if len(query) < 1:
        return

    if query.startswith("image:"):
        _query_dalle(query.replace("image:", ""))
        return

    match query:
        case "exit" | "quit":
            exit(0)

        case "flush":
            conversation.flush()
            return

        case "help":
            print(
                "\ncommands:\n"
                "- exit | quit\t\t\texit shell\n"
                "- flush\t\t\t\tflush conversation history\n"
                "- history\t\t\tprints conversation history\n"
                "- image: <description>\t\task DallE to generate an image"
                "\n"
            )

        case "history":
            conversation.print()
            return

        case _:
            _query_openai(model, query, retries)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="openai shell")
        parser.add_argument("-m", "--model", help="openai model",
                            default=OPEN_AI_DEFAULT_MODEL, required=False)
        parser.add_argument("-k", "--api-key", help="openai api key", required=False)
        parser.add_argument("-q", "--query", help="openai query (e.g. \"why is the sky blue?\")")
        parser.add_argument("-r", "--retries", type=int,
                            help="number of retries in case of failure")
        parser.add_argument("-d", "--debug", action="store_true", help="debug logging")
        args = parser.parse_args()

        logging_level = logging.DEBUG if args.debug else logging.INFO
        logging.basicConfig(
            stream=sys.stdout, level=logging_level,
            format="%(levelname)s - %(message)s")

        openai.api_key = args.api_key or API_KEY
        if not openai.api_key:
            print("Please provide an API key: "
                  "\n\nexport OPENAI_API_KEY=<api_key>"
                  "\n\nor run this program with -k <api_key>")
            sys.exit(1)

        # if a query is passed as argument, program
        # will exit after openai response
        if args.query:
            main(model=args.model, query=args.query, retries=args.retries)

        # else, it goes into shell mode (infinite loop)
        else:
            while True:
                try:
                    main(model=args.model, retries=args.retries)

                except KeyboardInterrupt:
                    pass

    except Exception as e:
        print(e)

    except KeyboardInterrupt:
        pass
