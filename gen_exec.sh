#!/bin/bash

python3 -m PyInstaller --add-binary="deps/libdivsufsort.so:lib" --onefile --windowed widget.py
