
import json
import openai
import os
import readline
import time


MODEL = "gpt-3.5-turbo"
IMAGE_SIZE = "1024x1024"


BOLD = "\033[1m"
NORMAL = "\033[0m"


QUERY_HISTORY = f"{os.path.expanduser('~')}/.openai_query_history"
try:
    readline.read_history_file(QUERY_HISTORY)

except FileNotFoundError:
    pass

readline.parse_and_bind("tab: complete")

conversation_history = []

CONVERSATION_HISTORY = f"{os.path.expanduser('~')}/.openai_conversation_history"
if os.path.isfile(CONVERSATION_HISTORY):
    try:
        with open(CONVERSATION_HISTORY, "r") as file:
            conversation_history = json.loads(file.read())

    except Exception:
        pass


openai.api_key = os.getenv("OPENAI_API_KEY")


def _query_dalle(query):
    response = openai.Image.create(
        prompt=query,
        n=1,
        size=IMAGE_SIZE
    )

    image_url = response["data"][0]["url"]
    print(f"\nImage: {image_url}")


def _query_openai(query):
    global conversation_history

    conversation_history.append({"role": "user", "content": query})

    try:
        stream = openai.ChatCompletion.create(
            model=MODEL,
            messages=conversation_history,
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
            time.sleep(0.03)

        conversation_history.append(ai_response)
        with open(CONVERSATION_HISTORY, "w") as file:
            file.write(json.dumps(conversation_history))

    except Exception as e:
        print(f"\nSystem › There was an issue querying openai: {e}")

    print("")


def main_loop():
    global conversation_history

    while True:
        try:
            query = input(f"\n{BOLD}User › ")

        except EOFError:
            break

        if len(query) < 1:
            continue

        readline.write_history_file(QUERY_HISTORY)

        if query.startswith("image:"):
            _query_dalle(query.replace("image:", ""))
            continue

        match query:
            case "flush history":
                conversation_history = []
                continue

            case "history":
                print(json.dumps(conversation_history, indent=2))
                continue

            case _:
                _query_openai(query)


if __name__ == "__main__":
    try:
        main_loop()

    except KeyboardInterrupt:
        pass
