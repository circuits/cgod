.. _Gopher: http://en.wikipedia.org/wiki/Gopher_(protocol)
.. _Gophernicus: gopher://gophernicus.org/
.. _Motsognir: gopher://gopher.viste-family.net/1/projects/motsognir/
.. _Docker: https://docker.com/
.. _Python: http://python.org/
.. _circuits: http://circuitsframework.com/


cgod
====

cgod is a Gopher Daemon with a similar feature set to `Gophernicus`_ and `Motsognir`_
and is fully "Dockerized" with `Docker`_. cgod is written in `Python`_ using the `circuits`_
Application Framework.


Installation
------------

Either pull the prebuilt `Docker`_ image::
    
    $ docker pull prologic/cgod

Or install from the development repository::
    
    $ hg clone https://bitbucket.org/prologic/cgod
    $ cd cgod
    $ pip install -r requirements.txt
