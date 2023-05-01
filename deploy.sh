rm -rf public/
rm -rf resources/
rm .hugo_build.lock
git add .
git commit -m 'auto deploy'
git push
