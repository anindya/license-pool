#!/bin/sh

pyarmor obfuscate --recursive --output ./src/app_pkg original/app_pkg/__init__.py

mkdir /vagrant/App/app_pkg
cd ./src/app_pkg
cp -r pytransform/ /vagrant/App/app_pkg/.

# echo "from .pytransform import pyarmor_runtime" >> ./tmp.py
# echo "pyarmor_runtime('/app/app_pkg/pytransform')" >> ./tmp.py
# echo $(cat src/AuthServer/__init__.py) >> ./tmp.py
# mv -f ./tmp.py ./__init__.py
