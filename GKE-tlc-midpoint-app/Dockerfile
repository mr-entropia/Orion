# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3-slim

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Prerequisites
RUN pip install --no-cache-dir pymysql

# Start listening
CMD python app.py