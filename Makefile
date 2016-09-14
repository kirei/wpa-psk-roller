SCRIPT=		wpa_psk_roller.py

TEMPFILES=	psk.txt psk.json

PYTHON=		python3
VENV=		venv
MODULES=	pylint wheel pexpect pyyaml
DISTDIRS=	*.egg-info build dist


all:

test:
	$(PYTHON) $(SCRIPT)
lint:
	pylint --reports=no -d line-too-long $(SCRIPT)

$(VENV):
	virtualenv -p $(PYTHON) $(VENV)
	$(VENV)/bin/pip install $(MODULES)

wheel:
	$(PYTHON) setup.py bdist_wheel

realclean: clean
	rm -rf $(VENV)

clean:
	rm -f $(TEMPFILES)
	rm -fr $(DISTDIRS)
