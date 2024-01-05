# announcementDialog
# Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import wx
import constants, update
from simpleDialog import errorDialog
from views import baseDialog, ViewCreator



class dialog(baseDialog.BaseDialog):
    def __init__(self):
        super().__init__("versionInfoDialog")

    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("クラスへのお知らせを入力"))
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.announcementCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, wx.VERTICAL, 10, style=wx.ALL, margin=20)
        self.textList = []
        self.textList.append("")
        self.info, dummy = self.announcementCreator.inputbox("", defaultValue="\r\n".join(self.textList), style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.BORDER_RAISED, sizerFlag=wx.EXPAND, x=750, textLayout=None)
        f = self.info.GetFont()
        f.SetPointSize((int)(f.GetPointSize() * (2/3)))
        self.info.SetFont(f)
        self.info.SetMinSize(wx.Size(750,240))

        # フッター
        footerCreator = ViewCreator.ViewCreator(self.viewMode, self.panel, self.sizer, style=wx.ALIGN_RIGHT | wx.ALL, margin=20)
        self.okBtn = footerCreator.okbutton(_("投稿"), self.onOkButton)
        self.okBtn.SetDefault()
        self.esc = footerCreator.cancelbutton(_("キャンセル"), None)

    def GetData(self):
        return self.info.GetValue()

    def onOkButton(self, event):
        #お知らせが未入力だったときの処理
        if len(self.info.GetValue().strip()) == 0:
            errorDialog(_("本文未入力で続行することはできません。"))
            return
        event.Skip()