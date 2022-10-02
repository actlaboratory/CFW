# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

from asyncio import events, selector_events
from email.quoprimime import body_check
from unittest import result
import winsound
import faulthandler
import pyperclip
from msilib.schema import File
from multiprocessing import context
from nturl2path import url2pathname
#from typing_extensions import Self
from api.classroom_users import UserCache
from views import authorizing
import wx
import CredentialManager

import constants
import globalVars
import menuItemsStore
import update
import webbrowser
import re
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from .base import *
from simpleDialog import *

from views import globalKeyConfig
from views import sample
from views import settingsDialog
from views import versionDialog
from views import announcementDialog

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800,400),
			self.app.config.getint(self.identifier,"sizeY",600,300),
			self.app.config.getint(self.identifier,"positionX",50,0),
			self.app.config.getint(self.identifier,"positionY",50,0)
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.service = self.getService()
		if not self.service:
			return

		self.getCourses()
		self.showCourses()

	def getCourses(self):
		service = self.getService()
		if not service:
			return
		try:
			response = self.getService().courses().list(pageToken=None, pageSize=None).execute()
			if response["courses"]:
				self.courses = response.get("courses", [])
		except HttpError as error:
			errorDialog(_("通信に失敗しました。インターネット接続を確認してください。"), self.hFrame)
			return

	def showCourses(self):
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_update"), False)
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_back"), False)
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_class_update"), False)
		self.lst, label = self.creator.virtualListCtrl(_("クラス一覧"))
		self.lst.AppendColumn(_("クラス名"))
		for i in self.courses:
			self.lst.append((i["name"], ))
			self.lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.events.on_class_CLICK)
			self.lst.Focus(0)
			self.lst.Select(0)

	def showTopics(self, courseId):
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_update"), True)
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_back"), True)
		response = self.getService().courses().topics().list(pageToken=None, pageSize=30, courseId=courseId).execute()
		self.topics = response.get("topic", [])
		response = self.getService().courses().courseWork().list(pageToken=None, pageSize=30, courseId=courseId).execute()
		self.workList = response.get("courseWork", [])
		self.Clear()
		self.tree, label = self.creator.treeCtrl("課題と資料")
		root = self.tree.AddRoot(_("課題"))
		for topic in self.topics:
			node = self.tree.AppendItem(root, topic["name"], )
		for work in self.workList:
			self.dsc = {}
			if "description" in work:
				self.dsc = {"description":work["description"]}
			node = self.tree.AppendItem(root, work["title"], data=self.dsc)
			for i in work["materials"]:
				if "form" in i:
					formInfo = {"formItem":i["form"]["formUrl"]}
					self.tree.AppendItem(node, i["form"]["title"], data=formInfo)
				if "driveFile" in i:
					drive = {"driveItems":i["driveFile"]["driveFile"]["alternateLink"]}
					self.tree.AppendItem(node, i["driveFile"]["driveFile"]["title"], data=drive)
				if "youtubeVideo" in i:
					video = {"youtube":i["youtubeVideo"]["alternateLink"]}
					self.tree.AppendItem(node, i["youtubeVideo"]["title"], data=video)
				if "link" in i:
					urls = {"url":i["link"]["url"]}
					self.tree.AppendItem(node, i["link"]["title"], data=urls)

	def showannouncements(self, courseId):
		response = self.getService().courses().announcements().list(courseId=courseId).execute()
		announcements = response.get("announcements", [])
		print(announcements)
		self.announcements = announcements

		self.announcementList, label = self.creator.virtualListCtrl(_("お知らせ一覧"))
		self.announcementList.AppendColumn(_("お知らせ"))
		self.announcementList.AppendColumn(_("作成日時"))
		self.announcementList.AppendColumn(_("更新者"))
		for i in announcements:
			self.text = i["text"]
			updatetime = i["updateTime"]
			#name = self.userCache.get(i["creatorUserId"], courseId)
			self.announcementList.append((self.text, updatetime))
		self.createButton = self.creator.button(_("クラスへの連絡事項を入力") + ("..."), self.events.announcementCreateDialog)
		self.announcementList.Bind(wx.EVT_CONTEXT_MENU, self.events.announcementContext)

	def tempFiles(self, courseId):
		response = self.getService().courses().courseWorkMaterials().list(courseId=courseId).execute()
		files = response.get("courseWorkMaterial", [])
		return files
	def workMaterials(self, materials):
		root = self.tree.GetRootItem()
		root = self.tree.AppendItem(root, ("資料"))
		for material in materials:
			node = self.tree.AppendItem(root, material["title"], data=self.dsc)
			for i in material["materials"]:
				if "driveFile" in i:
					if "title" in i["driveFile"]["driveFile"]:
						materialInfo = {"materials":i["driveFile"]["driveFile"]["alternateLink"]}
						self.tree.AppendItem(node, i["driveFile"]["driveFile"]["title"], data = materialInfo)
					else:
						self.tree.AppendItem(node, (_("不明なファイル")))
				elif "link" in i:
					info = {"url":i["link"]["url"]}
					self.tree.AppendItem(node, i["link"]["title"], data=info)
				elif "youtubeVideo" in i:
					videos = {"youtube":i["youtubeVideo"]["alternateLink"]}
					self.tree.AppendItem(node, i["youtubeVideo"]["title"], data=videos)

		info = self.tree.GetRootItem()
		self.tree.SetFocus()
		self.tree.ExpandAll()
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.events.alternate)
		self.DSC, label = self.creator.inputbox(_("説明"), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_PROCESS_ENTER)
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.events.onWorkSelected)

	def getService(self):
		if not self.app.credentialManager.isOK():
			errorDialog(_("利用可能なアカウントが見つかりませんでした。ファイルメニューから認証を実行してください。"), self.hFrame)
			self.dummy, empty = self.creator.virtualListCtrl(_("クラス一覧"))
			return

		self.app.credentialManager.refresh()
		self.app.credentialManager.Authorize()
		return build('classroom', 'v1', credentials=self.app.credentialManager.credential)

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニュー内容をいったんクリア
		self.hMenuBar=wx.MenuBar()

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hOptionMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()
		self.hAnnouncementListMenu=wx.Menu()


		#ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu,[
				"FILE_EXAMPLE",
				"FILE_ACCOUNT",
				"file_class_update",
				"file_update",
				"file_back",
				"file_exit"
		])

		#オプションメニュー
		self.RegisterMenuCommand(self.hOptionMenu,[
			"OPTION_OPTION",
			"OPTION_KEY_CONFIG",
		])

		#ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu,[
				"HELP_UPDATE",
				"HELP_VERSIONINFO",
		])

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル(&F))"))
		self.hMenuBar.Append(self.hOptionMenu,_("オプション(&O)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)
		if globalVars.app.credentialManager.isOK():
			self.hMenuBar.Enable(menuItemsStore.getRef("file_ACCOUNT"), False)


class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る
		if selected==menuItemsStore.getRef("FILE_EXAMPLE"):
			d = sample.Dialog()
			d.Initialize()
			r = d.Show()
			return
		if selected==menuItemsStore.getRef("FILE_ACCOUNT"):
			authorizeDialog = authorizing.authorizeDialog()
			authorizeDialog.Initialize()
			status = authorizeDialog.Show()

			if status==errorCodes.OK:
				self.parent.menu.hMenuBar.Enable(menuItemsStore.getRef("file_ACCOUNT"), False)
				self.parent.menu.hMenuBar.Enable(menuItemsStore.getRef("file_class_update"), True)
			elif status == errorCodes.CANCELED_BY_USER:
				dialog(_("認証結果"),_("キャンセルしました。"))
			elif status==errorCodes.IO_ERROR:
				dialog(_("認証に成功しましたが、ファイルの保存に失敗しました。ディレクトリのアクセス権限などを確認してください。"),_("認証結果"))
			elif status==errorCodes.CANCELED:
				dialog(_("ブラウザが閉じられたため、認証をキャンセルしました。"),_("認証結果"))
			elif status==errorCodes.NOT_AUTHORIZED:
				dialog(_("認証が拒否されました。"),_("認証結果"))
			else:
				dialog(_("不明なエラーが発生しました。"),_("エラー"))
			return
		if selected == menuItemsStore.getRef("file_update"):
			self.parent.announcementList.Destroy()
			self.parent.showannouncements(self.courseId)
			self.parent.announcementList.Focus(0)
			self.parent.announcementList.Select(0)
			return
		if selected == menuItemsStore.getRef("file_class_update"):
			self.parent.dummy.Destroy()
			self.parent.getCourses()
			self.parent.showCourses()

		if selected == menuItemsStore.getRef("file_back"):
			self.parent.Clear()
			self.parent.showCourses()
			self.parent.lst.Focus(0)
			self.parent.lst.Select(0)
			return
		if selected == menuItemsStore.getRef("file_exit"):
			self.parent.hFrame.Close()
			return
		if selected == menuItemsStore.getRef("OPTION_OPTION"):
			d = settingsDialog.Dialog()
			d.Initialize()
			d.Show()

			if self.setKeymap(self.parent.identifier,_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
				#ショートカットキーの変更適用とメニューバーの再描画
				self.parent.menu.InitShortcut()
				self.parent.menu.ApplyShortcut(self.parent.hFrame)
				self.parent.menu.Apply(self.parent.hFrame)

		if selected == menuItemsStore.getRef("HELP_UPDATE"):
			update.checkUpdate()

		if selected==menuItemsStore.getRef("HELP_VERSIONINFO"):
			d = versionDialog.dialog()
			d.Initialize()
			r = d.Show()
		if selected >= constants.MENU_URL_COPY:
			pyperclip.copy(self.i)
			dialog(_("url"),_("リンク先のコピーが完了しました。"))
			return
		if selected <= constants.MENU_URL_COPY:
			winsound.Beep(550, 750)
			webbrowser.open(self.i)

	def setKeymap(self, identifier,ttl, keymap=None,filter=None):
		if keymap:
			try:
				keys=keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		else:
			try:
				keys=self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		keyData={}
		menuData={}
		for refName in defaultKeymap.defaultKeymap[identifier].keys():
			title=menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title]=keys[refName]
			else:
				keyData[title]=_("なし")
			menuData[title]=refName

		d=globalKeyConfig.Dialog(keyData,menuData,[],filter)
		d.Initialize(ttl)
		if d.Show()==wx.ID_CANCEL: return False

		keyData,menuData=d.GetValue()

		#キーマップの既存設定を置き換える
		newMap=ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name,key in keyData.items():
			if key!=_("なし"):
				newMap[identifier.upper()][menuData[name]]=key
			else:
				newMap[identifier.upper()][menuData[name]]=""
		newMap.write()
		return True
	def on_class_CLICK(self, event):
		if event.GetIndex() == -1:
			return
		self.courseId = self.parent.courses[event.GetIndex()]["id"]
		self.parent.showTopics(self.courseId)
		self.parent.showannouncements(self.courseId)
		materials = self.parent.tempFiles(self.courseId)
		materials = self.parent.workMaterials(materials)

	def alternate(self, event):
		link = self.parent.tree.GetItemData(event.GetItem())
		if link == None:
			return
		if "url" in link:
			url = link["url"]
			webbrowser.open(url)
		elif "formItem" in link:
			form = link["formItem"]
			webbrowser.open(form)
		elif "driveItems" in link:
			items = link["driveItems"]
			webbrowser.open(items)
		elif "youtube" in link:
			stream = link["youtube"]
			webbrowser.open(stream)
		elif "materials" in link:
			files = link["materials"]
			webbrowser.open(files)

	def announcementCreateDialog(self, event):
		d = announcementDialog.dialog()
		d.Initialize()
		create = d.Show()
		if create == wx.ID_CANCEL: return
		response = self.parent.getService().courses().announcements().create(courseId = self.courseId, body = {"text":d.GetValue(),"state":"PUBLISHED"}).execute()

	def onWorkSelected(self, event):
		description = self.parent.tree.GetItemData(self.parent.tree.GetFocusedItem())
		if description == None:
			self.parent.DSC.Clear()
			self.parent.DSC.Disable()
			return
		if "description" in description:
			save = description["description"]
			self.parent.DSC.Enable()
			self.parent.DSC.SetValue(save)

	def announcementContext(self, event):
		focus = self.parent.announcementList.GetFocusedItem()
		if focus < 0:
			return
		text = self.parent.announcementList.GetItemText(focus, col=0)
		urlLists = re.findall(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", text)
		self.urlLists = urlLists
		context = wx.Menu()
		openSubMenu = wx.Menu()
		copySubMenu = wx.Menu()
		self.parent.menu.RegisterMenuCommand(context,"url_data", subMenu=openSubMenu)
		self.parent.menu.RegisterMenuCommand(context, "url_copy",subMenu=copySubMenu)
		for i,j in zip(urlLists, range(len(urlLists))):
			self.i = i
			self.j = j
			openSubMenu.Append(constants.MENU_URL_OPEN + j,i)
			copySubMenu.Append(constants.MENU_URL_COPY + j,i)
		self.parent.announcementList.PopupMenu(context, event)

