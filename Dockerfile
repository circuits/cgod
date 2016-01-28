# Docker Image for cgod (Gopher Daemon)

FROM prologic/python-runtime:onbuild
MAINTAINER James Mills, prologic at shortcircuit dot net dot au

# Services
EXPOSE 70

# Volume
VOLUME /var/gopher

# Startup
ENTRYPOINT ["/usr/bin/cgod"]
