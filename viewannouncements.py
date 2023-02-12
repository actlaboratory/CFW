#お知らせ詳細表示ダイアログ

import wx
from views import baseDialog, ViewCreator
from logging import getLogger

class Dialog(baseDialog.baseDialog):
    def __init__(self, announcement):
        self.announcement = announcement
        super().__init__("お知らせ詳細ダイアログ")

    def Initialize(self):
        self.log.debug("created")
        super().Initialize(self.app.hMainView.hFrame,_("お知らせ本文"))
        self.InstallControls()
        return True

    def InstallControls(self):
        """いろんなwidgetを設置する。"""
        self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
        body,data = self.creator.inputbox(_("お知らせ詳細"), None, self.announcement, stile=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_PROCESS_ENTER|wx.BORDER_RAISED, 500)
        body.Bind(wx.EVT_TEXT_ENTER,self.processEnter)
        self.escape = self.creator.closebutton(_("閉じる"), None)

    def processEnter(self,event):
        self.wnd.EndModal(wx.OK)
