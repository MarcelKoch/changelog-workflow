#!/usr/bin/env bash

set -e

usage='usage: consolidate-relnotes.bash <new-release-version> <prev-release-version>'

die() {
    echo "$@" 1>&2; exit 1
}

test "$#" = 2 || die "$usage"

files="$(ls doc/release/dev/* | grep -v doc/release/dev/0-sample-topic.rst)"
title="Version $1 Release Notes"
underline="$(echo "$title" | sed 's/./*/g')"
echo "$title
$underline

.. only:: html

  .. contents::

Changes made since App $2 include the following." > doc/release/"$1".rst
tail -q -n +3 $files >> doc/release/"$1".rst
sed -i "/^   $2 / i\\
   $1 <$1>" doc/release/index.rst
rm $files
