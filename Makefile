.PHONY: upgrade

PIP_COMPILE_CMD = pip-compile -U --allow-unsafe
upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade:
	pip install -q -r requirements/pip-tools.pip
	$(PIP_COMPILE_CMD) -o requirements/coverage.pip requirements/coverage.in
	$(PIP_COMPILE_CMD) --pip-args '-c requirements/coverage.pip' -o requirements/requirements.pip setup.cfg
	$(PIP_COMPILE_CMD) -o requirements/coveralls.pip requirements/coveralls.in
	$(PIP_COMPILE_CMD) -o requirements/lint.pip requirements/lint.in
	$(PIP_COMPILE_CMD) -o requirements/pip-tools.pip requirements/pip-tools.in
	$(PIP_COMPILE_CMD) -o requirements/test.pip requirements/test.in
	$(PIP_COMPILE_CMD) -o requirements/dev.pip requirements/dev.in
