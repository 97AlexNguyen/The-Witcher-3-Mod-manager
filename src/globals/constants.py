'''Global constants'''
# pylint: disable=invalid-name

from PySide6.QtCore import QCoreApplication

translate = QCoreApplication.translate

VERSION = "0.9.4-beta.3"
TITLE = translate("GLOBALS", "The Witcher 3 Mod Manager")
AUTHORS = [
    "Stefan Kostic (stefan3372)", 
    "Christian Sdunek (Systemcluster)",
    "Adam Sunderman (madman asunder)", 
    "Henry Hsieh (henry-hsieh)", 
    "George Burduli (burdulixda)",
    "Vincent (97nguyenvuquocan)" 
]
AUTHORS_MAIL = ["stekos@live.com", "me@systemcluster.me",
                "amsunderman@gmail.com", "r901042004@yahoo.com.tw", "burduli01@pm.me",
                "97nguyenvuquocan@gmail.com"]
URL_WEB = "https://www.nexusmods.com/witcher3/mods/2678"
URL_GIT = "https://github.com/Systemcluster/The-Witcher-3-Mod-manager.git"
URL_GIT_CLONE = "https://github.com/97AlexNguyen/The-Witcher-3-Mod-manager"
