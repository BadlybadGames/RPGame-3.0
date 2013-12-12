import sys
import os
from cx_Freeze import Freezer, Executable

fp = os.path.abspath(os.path.join(os.curdir, "..", "src"))
script = os.path.abspath(os.path.join(fp, "RPGame.py"))
icon_fp = os.path.abspath(os.path.join(os.curdir,"..","icon.ico"))
sys.path.append(fp)
target_fp = os.path.join("build","RPGame")


executables = [Executable(script, "Console")]

freezer = Freezer(executables,
        createLibraryZip = True,
        appendScriptToExe = True,
        targetDir = target_fp,
        icon = icon_fp
)
freezer.Freeze()