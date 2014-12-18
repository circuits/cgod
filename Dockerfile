# Docker Image for cgod (Gopher Daemon)

FROM crux/python
MAINTAINER James Mills, prologic at shortcircuit dot net dot au

# Services
EXPOSE 70

# Startup
ENTRYPOINT ["./server.py"]

# Runtime Dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Application
WORKDIR /app
ADD . /app
