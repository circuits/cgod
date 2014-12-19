cgod
====

cgod is a Gopher Daemon with a similar feature set to [Gophernicus](gopher://gophernicus.org/) and [Motsognir](gopher://gopher.viste-family.net/1/projects/motsognir/) and is fully "Dockerized" with [Docker](https://docker.com/). cgod is written in [Python](http://python.org/) using the [circuits](http://circuitsframework.com/) Application Framework.

Installation
------------

Either pull the prebuilt [Docker](https://docker.com/) image:

    $ docker pull prologic/cgod

Or install from the development repository:

    $ hg clone https://bitbucket.org/prologic/cgod
    $ cd cgod
    $ pip install -r requirements.txt
