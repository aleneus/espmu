.PHONY: style, flakes, lint, uml, docspdf

PACKAGE = espmu

all: help

help:
	@echo "style   | run style checker"
	@echo "flakes  | run flakes"
	@echo "lint    | run linter"
	@echo "uml     | build UML diagram"
	@echo "docspdf | build documentation in PDF format"
	@echo "upload  | upload new release to pypi"

style:
	pycodestyle $(PACKAGE)

flakes:
	pyflakes $(PACKAGE)

lint:
	pylint $(PACKAGE)

uml:
	pyreverse $(PACKAGE) -o png

docspdf:
	sphinx-build -b latex docs/source/ docs/build/latex
	sphinx-build -b latex docs/source/ docs/build/latex
	pdflatex -output-directory docs/build/latex docs/build/latex/$(PACKAGE).tex

upload:
	python3 setup.py sdist upload
