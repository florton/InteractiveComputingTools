# -*- mode: python -*-

block_cipher = None

extra_data = [('gatePics/*.png','gatePics'),('gatePics/freesansbold.ttf','gatePics')]

a = Analysis(['InteractiveLogic.py'],
             pathex=['C:\\Users\\F\\Documents\\GitHub\\InteractiveComputingTools\\InteractiveLogic'],
             binaries=None,
             datas=extra_data,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='InteractiveLogic',
          debug=False,
          strip=False,
          upx=True,
          console=False )
