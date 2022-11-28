# Minimal makefile for building and publishing pypub

DIST = sdist 

build: clean setup

clean:
	rm -rf build/ dist/ .eggs/ *.egg-info/

setup:
	python3 setup.py $(DIST)

publish-test:
	twine upload -r testpypi dist/*

publish:
	twine upload dist/*
