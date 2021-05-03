FROM python:3.8-slim

# establish working folder
WORKDIR /app

# add user and give ownership to workdir
RUN useradd -r -s /bin/bash worker && \
  chown -R worker:worker /app

USER worker

# set home & current env
ENV HOME /app
ENV PATH="/app/.local/bin:${PATH}"

# install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --user

# Copy the application contents
COPY . .

# set environment variables for the app
ENV USER Emma
ENV USER_PASS abcd
ENV AUTH_SERVER_URL 172.16.238.1
ENV AUTH_SERVER_PORT 5000

CMD [ "python", "./app.py" ]
