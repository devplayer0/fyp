#!/bin/sh
set -e

die() {
    >&2 echo $@
    exit 1
}

[ $# -ne 2 ] && die "usage: $0 <pipeline dir> <pipeline>"
exec docker run --rm -ti --privileged -v /dev/bus/usb:/dev/bus/usb -v "$1:/pipelines" ghcr.io/devplayer0/perfgrade "/pipelines/$2"
