
.PHONY: build
build:
	docker build . -f Dockerfile.build -t openai-shell-builder --output=bin --target=binaries
