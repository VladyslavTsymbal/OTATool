#!/bin/bash

python3 -m PyInstaller                         \
	--hidden-import=deps/libdivsufsort.so        \
	--add-binary="deps/libdivsufsort.so:."       \
	--add-binary="deps/libdivsufsort.so.1:."     \
	--add-binary="deps/libdivsufsort.so.1.0.0:." \
	--add-binary="deps/bsdiff:."                 \
	--add-binary="deps/bspatch:."                \
	--add-binary="deps/imgdiff:."                \
	--onefile                                    \
	--windowed                                   \
	widget.py
