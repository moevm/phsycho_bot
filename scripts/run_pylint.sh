#! /bin/bash

# WORKDIR
cd ..

pylint $(find src -type f -name "*.py")