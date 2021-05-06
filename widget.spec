# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['widget.py'],
             pathex=['/home/vlad/Development/QtProjects/OTATool'],
             binaries=[('deps/libdivsufsort.so', '.'), ('deps/libdivsufsort.so.1', '.'), ('deps/libdivsufsort.so.1.0.0', '.'), ('deps/bsdiff', '.'), ('deps/bspatch', '.'), ('deps/imgdiff', '.')],
             datas=[],
             hiddenimports=['deps/libdivsufsort.so'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='widget',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
