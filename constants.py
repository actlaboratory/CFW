# -*- coding: utf-8 -*-
#constant values
#Copyright (C) 2021 obaramayumi <mayumiobara089@gmail.com>

import wx

#アプリケーション基本情報
APP_FULL_NAME = "Classroom for Windows"#アプリケーションの完全な名前
APP_NAME="CFW"#アプリケーションの名前
APP_ICON = "cfw.ico"
APP_VERSION="1.0.1"
APP_LAST_RELEASE_DATE="2023-05-06"
APP_COPYRIGHT_YEAR="2023"
APP_LICENSE="Apache License 2.0"
APP_DEVELOPERS="mayumiPc, ACT laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL="https://actlab.org/software/CFW"
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All lights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

SUPPORTING_LANGUAGE={"ja-JP": "日本語","en-US": "English"}

#各種ファイル名
LOG_PREFIX="CFW"
LOG_FILE_NAME="cfw.log"
SETTING_FILE_NAME="settings.ini"
CACHE_FILE_NAME = "cache.ini"
KEYMAP_FILE_NAME="keymap.ini"



#フォントの設定可能サイズ範囲
FONT_MIN_SIZE=5
FONT_MAX_SIZE=35

#３ステートチェックボックスの状態定数
NOT_CHECKED=wx.CHK_UNCHECKED
HALF_CHECKED=wx.CHK_UNDETERMINED
FULL_CHECKED=wx.CHK_CHECKED
#メニュー
MENU_URL_OPEN=10000
MENU_URL_COPY=11000
MENU_MATERIAL_OPEN = 12000

#build関連定数
BASE_PACKAGE_URL = None
PACKAGE_CONTAIN_ITEMS = ("cfw.ico", )#パッケージに含めたいファイルやfolderがあれば指定
NEED_HOOKS = ()#pyinstallerのhookを追加したい場合は指定
STARTUP_FILE = "cfw.py"#起動用ファイルを指定
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_VERSION = "1.0.0"
UPDATER_WAKE_WORD = "hello"

GOOGLE_DIR = ".credential"
GOOGLE_FILE_NAME = "credential.json"
GOOGLE_CLIENT_ID = "817291682056-b8f5t2diae2qo78dtobbcli2b03ko06a.apps.googleusercontent.com"
GOOGLE_NEED_SCOPES = [
	"https://www.googleapis.com/auth/classroom.coursework.me",
	"https://www.googleapis.com/auth/classroom.courses.readonly",
	"https://www.googleapis.com/auth/classroom.topics.readonly",
	"https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
	"https://www.googleapis.com/auth/classroom.announcements",
	"https://www.googleapis.com/auth/classroom.rosters.readonly"
]
GOOGLE_CALLBACK_URL = "http://localhost:8080"
GOOGLE_CLIENT_SECRET = '{"installed":{"client_id":"817291682056-b8f5t2diae2qo78dtobbcli2b03ko06a.apps.googleusercontent.com","project_id":"classroom-for-windows","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}'
