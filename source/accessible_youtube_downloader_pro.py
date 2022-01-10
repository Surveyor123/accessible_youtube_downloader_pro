
# the main module 


import application
import pyperclip
import wx
import webbrowser
import os
os.chdir	(os.path.abspath(os.path.dirname(__file__)))
os.add_dll_directory(os.getcwd())
import subprocess
from utiles import youtube_regexp, check_for_updates, get_audio_stream, get_video_stream
from nvda_client.client import speak
import settings_handler
from gui.auto_detect_dialog import AutoDetectDialog
from gui.download_dialog import DownloadDialog
from gui.link_dlg import LinkDlg
from gui.settings_dialog import SettingsDialog
from gui.text_viewer import Viewer
from gui.custom_controls import CustomLabel
from gui.favorites import Favorites
from doc_handler import documentation_get
from language_handler import init_translation
from media_player.media_gui import MediaGui
from media_player.player import Player
from youtube_browser.browser import YoutubeBrowser
from threading import Thread
import database


settings_handler.config_initialization() # calling the config_initialization function which sets up the accessible_youtube_downloader_pro.ini file in the user appdata folder
init_translation("accessible_youtube_downloader") # program localization




class HomeScreen(wx.Frame):
	# the main class
	def __init__(self):
		wx.Frame.__init__(self, parent=None, title=application.name)
		self.Centre()
		self.SetSize(wx.DisplaySize())
		self.Maximize(True)
		panel = wx.Panel(self)
		self.instruction = CustomLabel(panel, -1, _("اضغط على مفتاح القوائم alt للوصول إلى خيارات البرنامج, أو تنقل بزر التاب للوصول سريعًا إلى أهم الخيارات المتاحة.")) # a breafe instruction message witch is shown by the custome StaticText to automaticly be focused when launching the app
		youtubeBrowseButton = wx.Button(panel, -1, _("البحث في youtube\tctrl+f"), name="tab")
		downloadFromLinkButton = wx.Button(panel, -1, _("التنزيل من خلال رابط\tctrl+d"), name="tab")
		playYoutubeLinkButton = wx.Button(panel, -1, _("تشغيل فيديو youtube من خلال الرابط\tctrl+y"), name="tab")
		favButton = wx.Button(panel, -1, _("الفيديوهات المفضلة	ctrl+shift+f"), name="tab")
		# quick access buttons
		sizer = wx.BoxSizer(wx.VERTICAL) # the main sizer
		sizer1 = wx.BoxSizer(wx.HORIZONTAL) # quick access buttons sizer
		for control in panel.GetChildren():
			if control.Name == "tab":
				sizer1.Add(control, 1) # adding quick access buttons using for loop sins that eatch button named by the "tab" word
		sizer.Add(self.instruction, 1)
		sizer.AddStretchSpacer()
		sizer.Add(sizer1, 1, wx.EXPAND)
		panel.SetSizer(sizer) # adding the sizer to the main panel
		menuBar = wx.MenuBar() # seting up the menu bar
		mainMenu = wx.Menu()
		searchItem = mainMenu.Append(-1, _("البحث في youtube\tctrl+f")) # search in youtube item
		downloadItem = mainMenu.Append(-1, _("التنزيل من خلال رابط\tctrl+d"))# download link item
		playItem = mainMenu.Append(-1, _("تشغيل فيديو youtube من خلال الرابط\tctrl+y")) # play youtube link item
		favoriteItem = mainMenu.Append(-1, _("الفيديوهات المفضلة	ctrl+shift+f"))
		openDownloadingPathItem = mainMenu.Append(-1, _("فتح مجلد التنزيل\tctrl+p")) # open downloading folder item
		settingsItem = mainMenu.Append(-1, _("الإعدادات...\talt+s")) # settings item
		exitItem = mainMenu.Append(-1, _("خروج\tctrl+w")) # quit item
		hotKeys = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord("F"), searchItem.GetId()),
			(wx.ACCEL_CTRL, ord("D"), downloadItem.GetId()),
			(wx.ACCEL_CTRL, ord("Y"), playItem.GetId()),
			(wx.ACCEL_CTRL+wx.ACCEL_SHIFT, ord("F"), favoriteItem.GetId()),
			(wx.ACCEL_CTRL, ord("P"), openDownloadingPathItem.GetId()),
			(wx.ACCEL_ALT, ord("S"), settingsItem.GetId()),
			(wx.ACCEL_CTRL, ord("W"), exitItem.GetId())
		])
		# the accelerator table asociated with the menu items
		self.SetAcceleratorTable(hotKeys) # adding the accelerator table to the frame
		menuBar.Append(mainMenu, _("القائمة الرئيسية")) # append the main menu to the menu bar
		aboutMenu = wx.Menu()
		userGuideItem = aboutMenu.Append(-1, _("دليل المستخدم...\tf1")) # userguide
		checkForUpdatesItem = aboutMenu.Append(-1, _("البحث عن التحديثات"))
		aboutItem = aboutMenu.Append(-1, _("عن البرنامج...")) # about item
		contactMenu = wx.Menu()
		emailItem = contactMenu.Append(-1, _("البريد الالكتروني..."))
		twitterItem = contactMenu.Append(-1, _("تويتر..."))
		aboutMenu.AppendSubMenu(contactMenu, _("تواصل معي"))
		menuBar.Append(aboutMenu, _("حول")) # append the about menu to the menu bar
		self.SetMenuBar(menuBar) # add the menu bar to the window
		# event bindings
		self.Bind(wx.EVT_MENU, self.onSearch, searchItem)
		youtubeBrowseButton.Bind(wx.EVT_BUTTON, self.onSearch)
		self.Bind(wx.EVT_MENU, self.onDownload, downloadItem)
		downloadFromLinkButton.Bind(wx.EVT_BUTTON, self.onDownload)
		self.Bind(wx.EVT_MENU, self.onPlay, playItem)
		playYoutubeLinkButton.Bind(wx.EVT_BUTTON, self.onPlay)
		self.Bind(wx.EVT_MENU, self.onFavorite, favoriteItem)
		favButton.Bind(wx.EVT_BUTTON, self.onFavorite)
		self.Bind(wx.EVT_MENU, self.onOpen, openDownloadingPathItem)
		self.Bind(wx.EVT_MENU, lambda event: SettingsDialog(self), settingsItem)
		self.Bind(wx.EVT_MENU, lambda event: wx.Exit(), exitItem)
		self.Bind(wx.EVT_MENU, self.onGuide, userGuideItem)
		self.Bind(wx.EVT_MENU, self.onCheckForUpdates, checkForUpdatesItem)
		self.Bind(wx.EVT_MENU, self.onAbout, aboutItem)
		self.Bind(wx.EVT_MENU, lambda event: webbrowser.open("mailto:Suleiman.alqusaimi@gmail.com"), emailItem)
		self.Bind(wx.EVT_MENU, lambda event: webbrowser.open("https://twitter.com/suleiman3ahmed"), twitterItem)
		self.Bind(wx.EVT_CHAR_HOOK, self.onHook)
		self.Bind(wx.EVT_SHOW, self.onShow)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Show()
		self.detectFromClipboard(settings_handler.config_get("autodetect"))
		if settings_handler.config_get("checkupdates"):
			Thread(target=check_for_updates, args=[True]).start()
	def onPlay(self, event): # the event function called when the play youtube link is clicked
		linkDlg = LinkDlg(self)
		data = linkDlg.data # get the link and playing format from the dialog
		url = data["link"]
		stream = get_video_stream(url) if not data["audio"] else get_audio_stream(url)
		gui = MediaGui(self, stream.title, stream, data["link"]) # initiating the media gui
		self.Hide()

	def onDownload(self, event): # the event function for the link downloading item to show the appropriate dialog
		dlg = DownloadDialog(self)
		dlg.Show()
	def onSearch(self, event): # showing the youtube browser window event function
		browser = YoutubeBrowser(self)
	def detectFromClipboard(self, config):
		if not config:
			return
		clip_content = pyperclip.paste() # get the clipboard content
		match = youtube_regexp(clip_content)
		if match is not None:
			AutoDetectDialog(self, clip_content)
	def onFavorite(self, event):
		Favorites(self)
		self.Hide()
	def onOpen(self, event):
		path = settings_handler.config_get("path")
		if not os.path.exists(path):
			os.mkdir(path)
		explorer = os.path.join(os.getenv("SYSTEMDRIVE"), "\\windows\\explorer")
		subprocess.call(f"{explorer} {path}")
	def onHook(self, event):
		if event.KeyCode == wx.WXK_F1:
			content = documentation_get()
			if content is None:
				event.Skip()
				return
			Viewer(self, _("دليل استخدام برنامج accessible youtube downloader pro"), content)
		event.Skip()
	def onShow(self, event):
		self.instruction.SetFocus()
	def onGuide(self, event):
		content = documentation_get()
		if content is None:
			return
		Viewer(self, _("دليل استخدام برنامج accessible youtube downloader pro"), content).ShowModal()
	def onCheckForUpdates(self, event):
		speak(_("جاري البحث عن التحديثات. يرجى الانتظار"))
		check_for_updates()

	def onAbout(self, event):
		about = f"""{_('اسم البرنامج')}: {application.name}.
{_('الإصدار')}: {application.version}.
{_('طُوِر بواسطة')}: {application.author}.
{_('الوصف: ')}{_(application.describtion)}."""
		wx.MessageBox(about, _("حول"), parent=self)
	def onClose(self, event):
		database.disconnect()
		wx.Exit()

app = wx.App()
HomeScreen()
app.MainLoop()
