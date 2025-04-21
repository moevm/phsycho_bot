#! /bin/bash

# WORKDIR
cd ..

pylint $(git ls-files '/src/*.py')