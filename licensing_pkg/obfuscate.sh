#!/bin/sh

pyarmor obfuscate --recursive --output ./src/AuthServer original/AuthServer/__init__.py

mkdir /vagrant/App/license-pkg
cd ./src/AuthServer
cp -r pytransform/ /vagrant/App/license-pkg/.

# echo "from .pytransform import pyarmor_runtime" >> ./tmp.py
# echo "pyarmor_runtime('/app/license-pkg/pytransform')" >> ./tmp.py
# echo $(cat src/AuthServer/__init__.py) >> ./tmp.py
# mv -f ./tmp.py ./__init__.py
