#! /bin/bash

# WORKDIR
cd ..

black --skip-string-normalization --skip-magic-trailing-comma --line-length=100 .
