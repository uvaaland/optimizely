init:
	pip install -r requirements.txt

pull:
	python3 optimizely.py

test:
	py.test test

.PHONY: init test
