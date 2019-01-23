#!/bin/bash
set -e

pipenv run pytest -vv --doctest-modules brainslug tests
pipenv run pycodestyle brainslug
