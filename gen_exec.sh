#!/bin/bash

python3 -m PyInstaller                     \
	--add-binary="deps/libdivsufsort.so:." \
	--add-binary="deps/bsdiff:."      \
	--add-binary="deps/bspatch:."     \
	--add-binary="deps/imgdiff:."     \
	--onefile                                \
	--windowed                               \
	widget.py
