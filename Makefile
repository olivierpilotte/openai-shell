
.PHONY: bin
bin:
	python -m nuitka --follow-imports shell.py
	mv shell.bin openai-shell

.PHONY: standalone-bin
standalone-bin:
	python -m nuitka --standalone shell.py

.PHONY: build
build:
	docker build . -f Dockerfile.build -t openai-shell-builder --output=bin --target=binaries
