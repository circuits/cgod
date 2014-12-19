# Docker Image for cgod (Gopher Daemon)

FROM crux/python:onbuild
MAINTAINER James Mills, prologic at shortcircuit dot net dot au

# Services
EXPOSE 70

# Startup
ENTRYPOINT ["/usr/bin/cgod"]
