# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2021 yamahubuki <itiro.ishino@gmail.com>

import winsound
import faulthandler
import pyperclip
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
		self.courses = []
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
		self.lst, label = self.creator.virtualListCtrl(_("クラス一覧"), proportion=1, sizerFlag=wx.EXPAND)
		self.lst.AppendColumn(_("クラス名"), width=600)
		for i in self.courses:
			self.lst.Append((i["name"], ))
		self.lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.events.on_class_CLICK)
		self.lst.Focus(0)
		self.lst.Select(0)

	def showTopics(self, courseId):
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_update"), True)
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_back"), True)
		response = self.getService().courses().topics().list(pageToken=None, pageSize=30, courseId=courseId).execute()
		self.topics = response.get("topic", [])
		self.Clear(20)
		self.tree, label = self.creator.treeCtrl("課題と資料", proportion=1,sizerFlag=wx.EXPAND)
		root = self.tree.AddRoot(self.events.data)
		self.topicNodes = {}
		self.topicNode = self.tree.AppendItem(root, ("トピックなし"))
		topicId = 0
		if topicId not in self.topicNodes:
			self.topicNodes[0] = self.topicNode
		for topic in self.topics:
			if "topicId" in topic:
				self.topicNode = self.tree.AppendItem(root, topic["name"])
				#topicIdとnodeのもドリチを辞書に格納
				topicId = topic["topicId"]
				self.topicNodes[topicId]= self.topicNode

	def works(self,courseId):
		root = self.tree.GetRootItem()
		response = self.getService().courses().courseWork().list(pageToken=None, pageSize=30, courseId=courseId).execute()
		self.workList = response.get("courseWork", [])
		self.dsc = {}
		workNodes = {}
		drive = {}
		video = {}
		urls = {}
		formInfo = {}
		for work in self.workList:
			if "topicId" in work:
				topicId = work["topicId"]
			else:
				#topicIdがなかった場合
				topicId = 0
			if topicId not in workNodes:
				workNodes[topicId] = self.topicNode
				node = self.tree.AppendItem(workNodes[topicId],("課題"))
				nodes = self.tree.AppendItem(node, work["title"])
			if "description" in work:
				self.dsc["description"] = work["description"]
				self.tree.AppendItem(nodes, work["title"], data=self.dsc)
			if "materials" in work:
				for i in work["materials"]:
					if "form" in i:
						if "title" in i["form"]:
							formInfo["url"] = i["form"]["formUrl"]
							self.tree.AppendItem(nodes, i["form"]["title"], data=formInfo)
				if "driveFile" in i:
					drive["url"] = i["driveFile"]["driveFile"]["alternateLink"]
					self.tree.AppendItem(nodes, i["driveFile"]["driveFile"]["title"], data=drive)
				if "youtubeVideo" in i:
					video["url"] = i["youtubeVideo"]["alternateLink"]
					self.tree.AppendItem(nodes, i["youtubeVideo"]["title"], data=video)
				if "link" in i:
					urls["url"] = i["link"]["url"]
					self.tree.AppendItem(nodes, i["link"]["title"], data=urls)
		self.tree.SetFocus()
		self.tree.Expand(root)
		self.tree.SelectItem(root, select=True)

	def announcementListCtrl(self):
		self.announcementList, label = self.creator.virtualListCtrl(_("お知らせ一覧"), proportion=1, sizerFlag=wx.EXPAND)
		self.announcementList.AppendColumn(_("お知らせ"), width=500)
		self.announcementList.AppendColumn(_("作成日時"), width=300)
		self.announcementList.AppendColumn(_("更新者"), width=200)

	def showannouncements(self, courseId):
		self.menu.hMenuBar.Enable(menuItemsStore.getRef("file_class_update"), False)
		response = self.getService().courses().announcements().list(courseId=courseId).execute()
		announcements = response.get("announcements", [])
		self.announcements = announcements
		if not announcements:
			return

		self.announcementData = []
		for announcement in self.announcements:
			self.text = announcement["text"]
			updatetime = announcement["updateTime"]
			#name = self.userCache.get(i["creatorUserId"], courseId)
			self.announcementList.append((self.text, updatetime))
			#添付ファイルと一緒に投稿されたお知らせへの対応
			materials = []
			if "materials" in announcement:
				for i in announcement["materials"]:
					if "driveFile" in i:
						if "alternateLink" in i["driveFile"]["driveFile"]:
							#driveFileのalternatelinkやtitleなどを辞書に格納
							file = {"alternate":i["driveFile"]["driveFile"]["alternateLink"],"name":i["driveFile"]["driveFile"]["title"]}
							#お知らせ一つに付き一つのリストに格納しているので先程作ったからのmaterialsにアペンドして辞書が入ったリストを作る
							materials.append(file)
					if "link" in i:
						link = {"alternate":i["link"]["url"],"name":i["link"]["title"]}
						materials.append(link)
					if "youtubeVideo"in i:
						videos = {"alternate":i["youtubeVideo"]["alternateLink"],"name":i["youtubeVideo"]["title"]}
						materials.append(videos)
						#辞書が入ったリストを格納するためのリストを作る
			self.announcementData.append(materials)
		self.announcementList.Bind(wx.EVT_CONTEXT_MENU, self.events.announcementContext)

	def announcementCreateButton(self):
		self.createButton = self.creator.button(_("クラスへの連絡事項を入力") + ("..."), self.events.announcementCreateDialog)

	def tempFiles(self, courseId):
		response = self.getService().courses().courseWorkMaterials().list(courseId=courseId).execute()
		files = response.get("courseWorkMaterial", [])
		return files

	def workMaterials(self, materials):
		root = self.tree.GetRootItem()
		root = self.tree.AppendItem(self.topicNode, ("資料"))
		self.dsc = {}
		materialInfo = {}
		info = {}
		videos = {}

		for material in materials:
			node = self.tree.AppendItem(root, material["title"], data=self.dsc)
			if "materials" not in material:
				return
			for i in material["materials"]:
				if "driveFile" in i:
					if "title" in i["driveFile"]["driveFile"]:
						materialInfo["url"] = i["driveFile"]["driveFile"]["alternateLink"]
						self.tree.AppendItem(node, i["driveFile"]["driveFile"]["title"], data = materialInfo)
					else:
						self.tree.AppendItem(node, (_("不明なファイル")))
				elif "link" in i:
					info["url"] = i["link"]["url"]
					self.tree.AppendItem(node, i["link"]["title"], data=info)
				elif "youtubeVideo" in i:
					videos["url"] = i["youtubeVideo"]["alternateLink"]
					self.tree.AppendItem(node, i["youtubeVideo"]["title"], data=videos)
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.events.alternate)
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.events.onWorkSelected)

	def description_data(self):
		self.DSCBOX, label = self.creator.inputbox(_("説明"), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_PROCESS_ENTER)

	def getService(self):
		if not self.app.credentialManager.isOK():
			errorDialog(_("利用可能なアカウントが見つかりませんでした。ファイルメニューから認証を実行してください。"), self.hFrame)
			self.showCourses()
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
				return

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
			self.parent.announcementList.clear()
			self.parent.showannouncements(self.courseId)
			return
		if selected == menuItemsStore.getRef("file_class_update"):
			self.parent.lst.Destroy()
			self.parent.getCourses()
			self.parent.showCourses()
			return
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
			return
		if selected==menuItemsStore.getRef("HELP_VERSIONINFO"):
			d = versionDialog.dialog()
			d.Initialize()
			r = d.Show()
			return
		if selected >= constants.MENU_MATERIAL_OPEN:
			obj = event.GetEventObject()
			#定めた定数から-してクリックされたメニューの項目の位置を取得
			index = (selected - 12000)
			#取得されたインデックス番号に対応するurlを開く
			webbrowser.open(self.parent.announcementData[self.focus][index]["alternate"])
			return
		if selected >= constants.MENU_URL_COPY:
			obj = event.GetEventObject()
			pyperclip.copy(obj.GetLabel(selected))
			dialog(_("url"),_("リンク先のコピーが完了しました。"))
			return
		if selected <= constants.MENU_URL_COPY:
			winsound.Beep(550, 750)
			obj = event.GetEventObject()
			webbrowser.open(obj.GetLabel(selected))
			return

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
		focus = self.parent.lst.GetFocusedItem()
		self.data = self.parent.lst.GetItemText(focus, col=0)
		print(self.data)
		self.parent.showTopics(self.courseId)
		self.parent.works(self.courseId)
		self.parent.announcementListCtrl()
		self.parent.showannouncements(self.courseId)
		self.parent.announcementCreateButton()
		materials = self.parent.tempFiles(self.courseId)
		materials = self.parent.workMaterials(materials)
		self.parent.creator.GetPanel().Layout()

	def alternate(self, event):
		link = self.parent.tree.GetItemData(event.GetItem())
		if link == None:
			return
		if "url" in link:
			url = link["url"]
			webbrowser.open(url)

	def announcementCreateDialog(self, event):
		d = announcementDialog.dialog()
		d.Initialize()
		create = d.Show()
		if create == wx.ID_CANCEL: return
		#お知らせ作成ダイアログで入力された情報をもとにお知らせを作成
		response = self.parent.getService().courses().announcements().create(courseId = self.courseId, body = {"text":d.GetValue(),"state":"PUBLISHED"}).execute()

	def onWorkSelected(self, event):
		self.parent.description_data()
		description = self.parent.tree.GetItemData(self.parent.tree.GetFocusedItem())
		if description is None:
			description = ""
			self.parent.DSCBOX.Clear()
			self.parent.DSCBOX.Disable()
			return
		if "description" in description:
			self.parent.DSCBOX.Enable()
			self.parent.DSCBOX.SetValue(description["description"])

	def announcementContext(self, event):
		focus = self.parent.announcementList.GetFocusedItem()
		self.focus = focus
		if focus < 0:
			return
		text = self.parent.announcementList.GetItemText(focus, col=0)
		urlLists = re.findall(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", text)
		self.urlLists = urlLists
		context = wx.Menu()
		openSubMenu = wx.Menu()
		copySubMenu = wx.Menu()
		tmp= wx.Menu()
		self.parent.menu.RegisterMenuCommand(context,"url_data", subMenu=openSubMenu)
		self.parent.menu.RegisterMenuCommand(context, "url_copy",subMenu=copySubMenu)
		self.parent.menu.RegisterMenuCommand(context, "tempFile_open", subMenu=tmp)
		for i,j in zip(urlLists, range(len(urlLists))):
			self.i = i
			openSubMenu.Append(constants.MENU_URL_OPEN + j,i)
			copySubMenu.Append(constants.MENU_URL_COPY + j,i)
			#アナウンスメントデーターをお知らせ分繰り返す
		for k,l in zip(self.parent.announcementData[focus], range(len(self.parent.announcementData))):
			#announcementDataの中の辞書が格納されたリストにアクセスできるのでmaterialsにアペンドされた辞書を取り出すことができる
			tmp.Append(constants.MENU_MATERIAL_OPEN + l,k["name"])
		self.parent.announcementList.PopupMenu(context, event)
