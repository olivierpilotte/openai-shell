# openai-shell binary builder
FROM python:3.10-slim AS builder
COPY . /code
WORKDIR /code
RUN apt update && \
    apt install -y binutils && \
    apt clean
RUN --mount=type=cache,target=~/.cache/pip \
    pip install -r requirements.txt && \
    pip install pyinstaller
RUN pyinstaller --onefile shell.py

FROM scratch AS binary
COPY --from=builder /code/dist/shell /

# openai-shell binary runner
FROM python:3.10-slim AS runner
COPY --from=builder /code/dist/shell /
CMD ["/shell"]
