.\venv\scripts\pip.exe freeze >> requirements.txt
docker build --tag book-downloader .
echo running built container
pause
docker run --env-file=.\docker_test_env book-downloader