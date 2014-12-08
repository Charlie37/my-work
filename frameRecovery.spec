# -*- mode: python -*-
a = Analysis(['FrameRecovery.py'],
             pathex=['C:\\Python27\\Lib\\site-packages\\PyQt4'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
# a.datas += [('FrameRecovery.gif', 'C:\\Python27\\Lib\\site-packages\\PyQt4\\FrameRecovery.gif', 'DATA')]
a.datas += [('FRAME_RecoveryTypo1.png', 'C:\\Python27\\Lib\\site-packages\\PyQt4\\FRAME_RecoveryTypo1.png', 'DATA')]
# a.datas += [('FRAME_RecoveryTypo2.png', 'C:\\Python27\\Lib\\site-packages\\PyQt4\\FRAME_RecoveryTypo2.png', 'DATA')]
# a.datas += [('FRAME_RecoveryTypo3.png', 'C:\\Python27\\Lib\\site-packages\\PyQt4\\FRAME_RecoveryTypo3.png', 'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='FrameRecovery.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon='FrameRecovery.ico')
