.PHONY: test

init:
	virtualenv --no-site-packages venv
	source venv/bin/activate && pip install -r requirements.txt

test:
	nosetests -v
