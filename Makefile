.PHONY: docs

PACKAGE = espmu

all: help

help:
	@echo "flake   run flake8"
	@echo "lint    run linter"
	@echo "uml     build UML diagram"
	@echo "docs    build documentation in PDF format"
	@echo "upload  upload new release to pypi"

flake:
	flake8 $(PACKAGE)

lint:
	pylint $(PACKAGE)

uml:
	pyreverse $(PACKAGE) -o png

docs:
	sphinx-build -b latex docs/source/ docs/build/latex
	pdflatex -output-directory docs/build/latex docs/build/latex/$(PACKAGE).tex
	pdflatex -output-directory docs/build/latex docs/build/latex/$(PACKAGE).tex
	cp docs/build/latex/$(PACKAGE).pdf .

upload:
	python3 setup.py sdist upload
