SCRIPT=		wpa_psk_roller.py

TEMPFILES=	psk.txt

PYTHON=		python3
VENV=		venv
MODULES=	pylint pexpect pyyaml

all:

test:
	$(PYTHON) $(SCRIPT)
lint:
	pylint --reports=no -d line-too-long $(SCRIPT)

$(VENV):
	virtualenv -p $(PYTHON) $(VENV)
	$(VENV)/bin/pip install $(MODULES)

realclean: clean
	rm -rf $(VENV)

clean:
	rm -f $(TEMPFILES)
