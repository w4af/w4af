## w4af - Web application security scanner
Official docker image for [w4af](http://w4af.net/)

There are two different Docker images for w4af: `stable` and `unstable`. The
`stable` image is built from the `master` branch in the project repositories while
`unstable` is built from `develop`. Choose wisely, as usual unstable releases have
more features but also potential bugs.

## Usage

 * In order to use w4af's docker image you'll first have to
 [install docker](http://docs.docker.com/installation/)
 
 * Then run these commands, please notice that the first time these commands are
 run the script will download a docker image from the registry, which might take
 between 1 and 5 minutes depending on your internet connection speed:

```
git clone https://github.com/andresriancho/w4af.git
cd w4af/extras/docker/scripts/
sudo ./w4af_console_docker
```

Running the `unstable` version is trivial (but dangerous since it might yield
unexpected results):

```
sudo ./w4af_console_docker -t unstable
```

## Sharing data with the container

When starting w4af using the `w4af_console_docker` or `w4af_gui_docker` commands
the docker containers are started with two volumes which are mapped to your
home directory:

 * `~/.w4af/` from your host is mapped to `/root/.w4af/` in the container.
 This directory is mostly used by w4af to store scan profiles and internal data.
 
 * `~/w4af-shared` from your host is mapped to `/root/w4af-shared` in the container.
 Use this directory to save your scan results and provide input files to w4af.

## Updating w4af-docker installation

When you first run `sudo ./w4af_console_docker` the helper script downloaded the
latest available docker image for w4af. Since we're improving our scanner almost
every week, you might want to get the latest docker image by running:

```
sudo docker pull andresriancho/w4af
```

## Debugging the container

The container runs a SSH daemon, which can be used to both run the `w4af_console`
and `w4af_gui`. To connect to a running container use `root` as username and
`w4af` as password. Usually you don't need to worry about this, since the helper
scripts will connect to the container for you.

Another way to debug the container is to run the script with the `-d` flag: 

```
$ sudo ./w4af_console_docker -d
root@a01aa9631945:~# 
```

## Building a new container

The docker container provided at the public docker hub is enough for most users,
but if you want to customize or improve the container we recommend using the
provided build helper script:

```
$ cd w4af
$ # <your changes to w4af here>
$ cd extras/docker/
$ pip install --upgrade docker-tag-naming
$ sudo ./docker-build-local.sh
...
```

This will build a local image named `andresriancho/w4af` with the latest git
commit as tag. Run `docker images` to find the created tag and then:

```
sudo ./w4af_console_docker -t <image-tag>
```

## Security

Don't bind w4af's docker image to a public IP address unless you really know
what you're doing! Anyone will be able to SSH into the docker image using the
hard-coded SSH keys! 

## TODO

We still need to figure out (and add to this documentation) the best way for
users to be able to perform these tasks:
 
 * Passing parameters to the docker: scripts, profiles, dictionary files
   (how do I run ./w4af_console -s foo.w4af ?). I believe that the helper script
   would have to "forward" the parameters to the docker run command.
   [#8461](https://github.com/andresriancho/w4af/issues/8461)
 * Run the GUI environment [#8460](https://github.com/andresriancho/w4af/issues/8460)
 * Remove root requirement for helper script [#8493](https://github.com/andresriancho/w4af/issues/8493)

Want to help? Just follow the link to the task and add a comment saying you'll
be working on it.
