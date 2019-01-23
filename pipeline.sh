#!/bin/bash
set -e

pytest -vv --doctest-modules brainslug tests
pycodestyle brainslug
