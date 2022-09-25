﻿# -*- coding: utf-8 -*-
#error codes

OK=0				#成功(エラーなし)
NOT_SUPPORTED=1		#サポートされていない呼び出し
FILE_NOT_FOUND=2
PARSING_FAILED=3
IO_ERROR=4 			#ファイル入出力エラー
ACCESS_DENIED=5
WAITING_USER=6		#ユーザの操作待ち
NOT_AUTHORIZED=8	#グーグルで認証していない
CANCELED_BY_USER = 11

CONNECT_TIMEOUT = 12
UPDATER_NEED_UPDATE = 200# アップデートが必要
UPDATER_LATEST = 204# アップデートが無い
UPDATER_VISIT_SITE = 205
UPDATER_BAD_PARAM = 400# パラメーターが不正
UPDATER_NOT_FOUND = 404# アプリケーションが存在しない

UNKNOWN=99999
