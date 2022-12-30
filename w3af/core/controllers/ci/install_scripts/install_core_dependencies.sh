#!/bin/bash -x

# We now install the core dependencies for the w4af project.
python -c 'from w4af.core.controllers.dependency_check.dependency_check import dependency_check;dependency_check()'

if [ -f requirements.txt ]; then
	pip install -r requirements.txt;
fi

