pyarmor obfuscate --recursive --output App_dist/ App/main.py
cp App/Dockerfile App_dist/
cp App/requirements.txt App_dist/
cp -r App/app_pkg App_dist/
cp -r App/license-pkg App_dist/
#rm -rf dist/pytransform
#cp -r pytransform dist/pytransform
