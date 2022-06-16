.\venv\scripts\pip.exe freeze >> requirements.txt
docker build --tag tailslide/book-downloader .
echo running built container
pause
docker run --env-file=.\docker_test_env tailslide/book-downloader
echo pushing to dockerhub
pause
docker push tailslide/book-downloader:latest
