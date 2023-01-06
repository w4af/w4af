## w4af - Web application security scanner
Official docker image for [w4af](http://w4af.net/)

## Usage

 * In order to use w4af's docker image you'll first have to
 [install docker](http://docs.docker.com/installation/)
 
 * Then run this command:

```
docker run -it w4af/w4af:latest
```

to launch the interactive w4af console.


## Building a new container

The docker container provided at the public docker hub is enough for most users,
but if you want to customize or improve the container we recommend using the
provided build helper script:

```
$ cd w4af
$ # <your changes to w4af here>
$ docker build -t w4af -f extras/docker/Dockerfile .
$ docker tag w4af w4af/w4af
```

This will build a local image named `w4af/w4af`
