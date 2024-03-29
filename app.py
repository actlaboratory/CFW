﻿# -*- coding: utf-8 -*-
#Application Main

import win32api
import win32event
import constants
import winerror
import AppBase
import update
import CredentialManager
import globalVars
import proxyUtil
import win32event
import win32api
import winerror

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()
	def OnInit(self):
		#多重起動防止
		globalVars.mutex = win32event.CreateMutex(None, 1, constants.APP_NAME)
		if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
			globalVars.mutex = None
			return False
		return True

	def initialize(self):
		self.setGlobalVars()
		# プロキシの設定を適用
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		self.setProxyEnviron()
		# タスクバーアイコンの準備
		import views.taskbar
		self.tb = views.taskbar.TaskbarIcon()
		# アップデートを実行
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)

		self.credentialManager=CredentialManager.CredentialManager()

		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		self.hMainView.Show()
		return True

	def setProxyEnviron(self):
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()

	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		# アップデート
		globalVars.update.runUpdate()

		#戻り値は無視される
		return 0
