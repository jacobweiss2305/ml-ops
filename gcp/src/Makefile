# Makefile
SHELL = /bin/bash

#Help
.PHONY: help
help:
	@echo "Commands:"
	@echo "venv    : creates a virtual environment."
	@echo "style   : executes style formatting."
	@echo "clean   : cleans all unnecessary files."
	@echo "test    : execute tests on code, data and models."

# AWS
.PHONY:
push-version:
	docker build preprocess/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-preprocess:$(version) && \
	docker build train/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-train:$(version) && \
	docker build serve/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-serve:$(version) && \
	docker build monitor/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-monitor:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-preprocess:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-train:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-serve:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-monitor:$(version)