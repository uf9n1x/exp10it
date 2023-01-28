rmdir public /S /Q
rmdir resources /S /Q
del .hugo_build.lock
git add .
git commit -m "auto deploy"
git push
pause