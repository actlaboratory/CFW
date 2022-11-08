# -*- coding: utf-8 -*-
#Application startup file

import os
import sys
import simpleDialog
import traceback
import winsound
#64bitのPythonでは起動させない
if sys.maxsize > (2 ** 32):
	print("64 bit環境では起動できません。")
	exit()

#カレントディレクトリを設定
if hasattr(sys,"frozen"): os.chdir(os.path.dirname(sys.executable))
else: os.chdir(os.path.abspath(os.path.dirname(__file__)))

def exchandler(type, exc, tb):
	msg=traceback.format_exception(type, exc, tb)
	print("".join(msg))
	winsound.PlaySound("beep.wav", winsound.SND_FILENAME)
	try:
		f=open("errorLog.txt", "a")
		f.writelines(msg)
		f.close()
	except:
		pass
	sys.exit(1)

sys.excepthook=exchandler

#Python3.8対応
#dllやモジュールをカレントディレクトリから読み込むように設定
if sys.version_info.major>=3 and sys.version_info.minor>=8:
	os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app as application
import globalVars

def main():
	try:
		if os.path.exists("errorLog.txt"):
			os.remove("errorLog.txt")
	except:
		pass
	app=application.Main()
	globalVars.app=app
	app.initialize()
	app.MainLoop()
	app.config.write()

#global schope
if __name__ == "__main__": main()
