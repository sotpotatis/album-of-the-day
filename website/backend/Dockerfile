#Backend Dockerfile
#Runs the backend (the website) which includes the API etc.
FROM ghcr.io/oracle/oraclelinux8-instantclient:21
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
# Decode Base64 environment variables to create files
RUN chmod +x ./expand-environment-files.sh
RUN ./expand-environment-files.sh
# Install Poetry and dependencies
RUN curl -sSL https://install.python-poetry.org | python3.9 -
# Add Poetry to path
ENV PATH="/root/.local/bin:$PATH"
# Install dependencies using Poetry
RUN poetry install
# And now just run the server
WORKDIR album_of_the_day_backend
EXPOSE 8080
ENTRYPOINT ["poetry", "run", "uvicorn", "album_of_the_day.asgi:application", "--host=0.0.0.0", "--port=8080"]