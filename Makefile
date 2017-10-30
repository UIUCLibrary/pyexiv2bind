.PHONY: clean docs build
PYTHON := python3
build: venv _skbuild
	@echo "Hello"

wheel: venv
	source venv/bin/activate && python setup.py bdist_wheel

venv:
	$(PYTHON) -m venv venv
	@source venv/bin/activate && pip install -r requirements-dev.txt

clean:
	@$(PYTHON) setup.py clean
	@cd docs && $(MAKE) clean

	@echo "removing '_skbuild'"
	@rm -rf _skbuild

	@echo "removing '.tox'"
	@rm -rf .tox

	@echo "removing '.eggs'"
	@rm -rf .eggs

	@echo "removing 'py3exiv2bind.egg-info'"
	@rm -rf py3exiv2bind.egg-info


docs: venv
	@echo building docs
	source venv/bin/activate && cd docs && $(MAKE) html

_skbuild: venv
	source venv/bin/activate && python setup.py build