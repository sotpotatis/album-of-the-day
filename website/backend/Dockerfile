#Backend Dockerfile
#Runs the backend (the website) which includes the API etc.
FROM ghcr.io/oracle/oraclelinux8-instantclient:21
# Set all the environment variables from arguments (see docker-compose.yml)
ARG DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
ARG DATABASE_USER=$DATABASE_USER
ARG DATABASE_PASSWORD=$DATABASE_PASSWORD
ARG DATABASE_NAME=$DATABASE_NAME
ARG DATABASE_HOST=$DATABASE_HOST
ARG DATABASE_PORT=$DATABASE_PORT
ARG DATABASE_ENGINE=$DATABASE_ENGINE
ARG LAST_FM_API_KEY=$LAST_FM_API_KEY
ARG LAST_FM_USER_AGENT=$LAST_FM_USER_AGENT
ARG LAST_FM_USERNAME=$LAST_FM_USERNAME
ARG SPOTIFY_CLIENT_ID=$SPOTIFY_CLIENT_ID
ARG SPOTIFY_CLIENT_SECRET=$SPOTIFY_CLIENT_SECRET
ARG SPOTIFY_USER_AGENT=$SPOTIFY_USER_AGENT
ARG FRONTEND_BASE_URL=$FRONTEND_BASE_URL
ARG BASE_URL=$BASE_URL
ARG BASE_DOMAIN=$BASE_DOMAIN
ARG ALBUM_OF_THE_DAY_BOT_TOKEN=$ALBUM_OF_THE_DAY_BOT_TOKEN
ARG ALBUM_IMAGES_FONT_PATH=$ALBUM_IMAGES_FONT_PATH
ARG DJANGO_CSRF_ORIGINS=$DJANGO_CSRF_ORIGINS
ARG ORACLE_WALLET_FILE_CONTENTS=$ORACLE_WALLET_FILE_CONTENTS
ARG ORACLE_SQLNET_FILE_CONTENTS=$ORACLE_SQLNET_FILE_CONTENTS
ARG ORACLE_TNSNAMES_FILE_CONTENTS=$ORACLE_TNSNAMES_FILE_CONTENTS
ARG TASK_RUNNER_CONFIG_FILE_CONTENTS=$TASK_RUNNER_CONFIG_FILE_CONTENTS
WORKDIR /app
COPY ./album_of_the_day_backend .
# Install dependencies
 #(coreutils is for Base64), python3-devel and postgresql is for psycopg2
RUN yum install python39 curl wget unzip coreutils postgresql python3-devel -y
WORKDIR album_of_the_day_backend
# Download Archivo Black
RUN wget https://www.1001fonts.com/download/archivo-black.zip
RUN unzip archivo-black.zip
# Set environment variable to where the font was downloaded
ENV ALBUM_IMAGES_FONT_PATH=$(pwd)/archivo-black/ArchivoBlack-Regular.zip
WORKDIR /app
# Install Poetry and dependencies
RUN curl -sSL https://install.python-poetry.org | python3.9 -
# Add Poetry to path
ENV PATH="/root/.local/bin:$PATH"
# Install dependencies using Poetry
RUN poetry install
WORKDIR album_of_the_day_backend
# Decode environment variables from Base64
RUN poetry run python ./album_of_the_day/expand_files_from_environment.py
# And now just run the server
EXPOSE 8080
ENTRYPOINT ["poetry", "run", "uvicorn", "album_of_the_day.asgi:application", "--host=0.0.0.0", "--port=8080"]
