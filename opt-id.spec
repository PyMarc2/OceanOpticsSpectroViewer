# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['opt-id.py'],
             pathex=['C:\\Users\\marc-\\Documents\\Github\\DCC\\Optics-ID'],
             binaries=[],
             datas=[('gui/modules/*', 'gui/modules/'), ('gui/dialog/*', 'gui/dialog/'),
             ('gui/views/*', 'gui/views/'), ('gui/widgets/*', 'gui/widgets/'),
             ('gui/windows/*', 'gui/windows/'), ('gui/misc/logo/*', 'gui/misc/logo/')],
             hiddenimports=[],
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
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='C:\\Users\\marc-\\Documents\\Github\\DCC\\Optics-ID\\gui\\misc\\logo\\logo3.ico')
