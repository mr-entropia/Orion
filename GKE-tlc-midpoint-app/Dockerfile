# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
COPY run.sh ./
RUN chmod a+x ./run.sh

# Prerequisites
RUN pip install --no-cache-dir pymysql google-cloud-pubsub

# Start listening
CMD ["./run.sh"]