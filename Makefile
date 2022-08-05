.PHONY: help
help:
	@echo "make prepare          # install all requirements"
	@echo "make run_dev          # run REST API server"
	@echo "make build_docker     # build docker image"
	@echo "make run_docker       # build docker image"
	@echo "make lint             # check linting"
	@echo "make flake8           # alias for `make lint`"
	@echo "make tests            # runs tests"
	@echo "make help             # show this help"

.PHONY: prepare
prepare:
	pip3 install -r api/requirements-dev.txt

.PHONY: run_dev
run_dev:
	$(PYTHON) -m app.app

.PHONY: build
build_docker:
	docker build -t flask-api .

.PHONY: run_docker
run_docker:
	docker run -p 5000:5000 -it flask-api

.PHONY: lint
lint:
	python3 -m flake8
	
.PHONY: flake8
flake8:
	python3 -m flake8

.PHONY: tests
tests:
	python3 -m pytest api/tests -vvv

