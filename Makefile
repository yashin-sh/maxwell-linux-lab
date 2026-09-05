PYTHON ?= python3

.PHONY: test check inventory

test:
	$(PYTHON) -m unittest discover -s tests -v

check:
	./scripts/check-environment.sh

inventory:
	$(PYTHON) -m maxwell_lab.cli inventory --output artifacts/inventory.json
