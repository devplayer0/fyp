#!/bin/sh
set -e

die() {
    >&2 echo $@
    exit 1
}

[ $# -ne 1 ] && die "usage: $0 <pipeline>"

abs="$(realpath $1)"
vol="$(dirname $abs)"
pipeline="$(basename $abs)"

exec docker run --rm -ti --privileged -v /dev/bus/usb:/dev/bus/usb -v "$vol:/work" ghcr.io/devplayer0/perfgrade "/work/$pipeline"
