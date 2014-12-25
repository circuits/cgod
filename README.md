cgod
====

cgod is a Gopher Daemon with a similar feature set to [Gophernicus](gopher://gophernicus.org/) and [Motsognir](gopher://gopher.viste-family.net/1/projects/motsognir/) and is fully "Dockerized" with [Docker](https://docker.com/). cgod is written in [Python](http://python.org/) using the [circuits](http://circuitsframework.com/) Application Framework.

Full documentation can be found on Gopherspace at:

<gopher://arrow.shortcircuit.net.au/1~prologic/projects/cgod/>

Installation
------------

Either pull the prebuilt [Docker](https://docker.com/) image:

    $ docker pull prologic/cgod

Or install from the development repository:

    $ hg clone https://bitbucket.org/prologic/cgod
    $ cd cgod
    $ pip install .

Usage
-----

Using [Docker](https://docker.com/):

    $ docker run -d 70:70 -v /var/gopher:/var/gopher -H domain.com -r /var/gopher

Or via a local install:

    # cgod -H domain.com -r /var/gopher

> **note**
>
> It is important to configure the `-H/--hostname` properly and set this to  
> the hostname that remote Gopher clients will connect to your Gopher server with.
>
For other configuration options:

    $ docker run prologic/cgod --help

or:

    $ cgod --help

A path to a configuration file can also be specified with the `-c/--config` option. The file format is INI-style and takes all of the same long options as the command-line.

Example Configuration:

    [globals]
    rootdir = '/var/gopher'
    host = 'domain.com'
