SCRIPT=		wpa_psk_roller.py

VENV=		venv
MODULES=	pylint pexpect pyyaml

all:
	
lint:
	pylint --reports=no -d line-too-long $(SCRIPT)

$(VENV):
	virtualenv -p python3 $(VENV)
	$(VENV)/bin/pip install $(MODULES)

realclean: clean
	rm -rf $(VENV)

clean:
