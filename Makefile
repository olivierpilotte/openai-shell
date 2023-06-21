
.PHONY: binary
binary:
	docker build --output=bin --target=binary -t openai-shell:latest . --no-cache

.PHONY: build
build:
	docker build -t openai-shell:latest . --no-cache

.PHONY: run
run:
	docker run -ti -e OPENAI_API_KEY=`echo $$OPENAI_API_KEY` openai-shell:latest
