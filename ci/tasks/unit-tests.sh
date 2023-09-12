#!/bin/sh

make -C $1 pip
make -C $1 pretty
make -C $1 pytest