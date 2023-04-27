
import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"file_update":_("最新のお知らせを取得"),
	"file_class_update":_("最新のクラス一覧を取得"),
	"FILE_ACCOUNT":_("アカウントと連携する") + "...",
	"file_back":_("クラス選択画面へ戻る"),
	"file_hide":_("ウィンドウを隠す(&h)"),

	"OPTION_OPTION":_("設定(&S)")+"...",
	"OPTION_KEY_CONFIG":_("ショートカットキーの設定(&K)")+"...",

	"HELP_UPDATE":_("最新バージョンを確認(&U)")+"...",
	"HELP_VERSIONINFO":_("バージョン情報(&V)")+"...",

	"url_data":_("リンクを開く") ,
	"url_copy":_("リンクをコピー"),
	"tempFile_open":_("添付ファイルを開く"),
	"view_announcements":_("お知らせの詳細を表示"),

	"SHOW":_("ウィンドウを表示(&s)"),
	"EXIT":_("終了(&X)"),
}
