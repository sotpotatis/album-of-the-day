#Backend Dockerfile
#Runs the backend (the website) which includes the API etc.
FROM ghcr.io/oracle/oraclelinux8-instantclient:21
WORKDIR /app
COPY ./album_of_the_day_backend .
RUN cat ./backend.env || exit 1 # Validate environment variable file
# Install dependencies
# (coreutils is for Base64), python3-devel and postgresql is for psycopg2
RUN yum install python39 curl wget unzip coreutils postgresql python3-devel -y
WORKDIR album_of_the_day_backend
# Download Archivo Black - not needed anymore as it is handled by the code
# RUN wget https://www.1001fonts.com/download/archivo-black.zip
# RUN unzip archivo-black.zip
# Set environment variable to where the font was downloaded
# ENV ALBUM_IMAGES_FONT_PATH=$(pwd)/archivo-black/ArchivoBlack-Regular.zip
WORKDIR /app
# Install Poetry and dependencies
RUN curl -sSL https://install.python-poetry.org | python3.9 -
# Add Poetry to path
ENV PATH="/root/.local/bin:$PATH"
# Install dependencies using Poetry
RUN poetry install
# Work with the environment variables
WORKDIR album_of_the_day_backend
RUN poetry run python album_of_the_day/expand_files_from_environment.py
# And now just run the server
EXPOSE 8080
ENTRYPOINT ["poetry", "run", "uvicorn", "album_of_the_day.asgi:application", "--host=0.0.0.0", "--port=8080"]
