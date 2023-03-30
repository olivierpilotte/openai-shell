
import json
import openai
import os
import readline
import time


MODEL = "gpt-3.5-turbo"
IMAGE_SIZE = "1024x1024"

HISTORY = f"{os.path.expanduser('~')}/.chatgpt_conversation_history"


histfile = "~/.ai_queries"
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass

readline.parse_and_bind("tab: complete")


if os.path.isfile(HISTORY):
    try:
        with open(HISTORY, "r") as file:
            conversation_history = json.loads(file.read())

    except Exception:
        conversation_history = []


openai.api_key = os.getenv("OPENAI_API_KEY")

while True:
    query = input("\nopenai › ")
    conversation_history.append({"role": "user", "content": query})

    if len(query) < 1:
        continue

    if query == "flush history":
        conversation_history = []
        continue

    if query.startswith("image:"):
        query.replace("image:", "")
        response = openai.Image.create(
            prompt=query,
            n=1,
            size=IMAGE_SIZE
        )

        image_url = response['data'][0]['url']
        print(f"\nImage: {image_url}")

        continue

    stream = openai.ChatCompletion.create(
        model=MODEL,
        messages=conversation_history,
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
        time.sleep(0.03)

    conversation_history.append(ai_response)
    with open(HISTORY, "w") as file:
        file.write(json.dumps(conversation_history))

    print("")
