.PHONY: style, flakes, lint, uml

PACKAGE = espmu

all: help

help:
	@echo "style"
	@echo "flakes"
	@echo "lint"
	@echo "uml"
	@echo "make release ver=value"

style:
	pycodestyle $(PACKAGE)

flakes:
	pyflakes $(PACKAGE)

lint:
	pylint $(PACKAGE)

uml:
	pyreverse $(PACKAGE) -o png

release:
	@echo $(ver)
	hg up default
	@echo 'Update to default: OK'
	hg merge develop
	@echo 'Merge from develop: OK'
	hg ci -m 'merge from develop'
	hg tag $(ver)
	@echo 'Add tag: OK'
	hg up develop
	@echo 'Update to develop: OK'

upload:
	python3 setup.py sdist upload
