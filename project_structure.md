The-Witcher-3-Mod-manager
├── .github
│   └── workflows
│       └── build.yml
├── api
│   ├── get_category
│   │   └── witcher3_categories.json
│   ├── api_key.txt
│   ├── get_category.py
│   ├── nexus_api.py
│   └── setup_api.py
├── build
│   └── exe.win-amd64-3.12
│       ├── lib
│       │   ├── asyncio
│       │   ├── charset_normalizer
│       │   │   ├── md.cp312-win_amd64.pyd
│       │   │   ├── md__mypyc.cp312-win_amd64.pyd
│       │   │   └── py.typed
│       │   ├── collections
│       │   ├── concurrent
│       │   │   └── futures
│       │   ├── ctypes
│       │   │   └── macholib
│       │   │       ├── fetch_macholib
│       │   │       ├── fetch_macholib.bat
│       │   │       └── README.ctypes
│       │   ├── email
│       │   │   ├── mime
│       │   │   └── architecture.rst
│       │   ├── encodings
│       │   ├── fasteners
│       │   │   └── pywin32
│       │   ├── http
│       │   ├── importlib
│       │   │   ├── metadata
│       │   │   └── resources
│       │   ├── json
│       │   ├── logging
│       │   ├── multiprocessing
│       │   │   └── dummy
│       │   ├── PySide6
│       │   │   ├── plugins
│       │   │   │   ├── generic
│       │   │   │   │   └── qtuiotouchplugin.dll
│       │   │   │   ├── iconengines
│       │   │   │   │   └── qsvgicon.dll
│       │   │   │   ├── imageformats
│       │   │   │   │   ├── qgif.dll
│       │   │   │   │   ├── qicns.dll
│       │   │   │   │   ├── qico.dll
│       │   │   │   │   ├── qjpeg.dll
│       │   │   │   │   ├── qpdf.dll
│       │   │   │   │   ├── qsvg.dll
│       │   │   │   │   ├── qtga.dll
│       │   │   │   │   ├── qtiff.dll
│       │   │   │   │   ├── qwbmp.dll
│       │   │   │   │   └── qwebp.dll
│       │   │   │   ├── networkinformation
│       │   │   │   │   └── qnetworklistmanager.dll
│       │   │   │   ├── platforminputcontexts
│       │   │   │   │   └── qtvirtualkeyboardplugin.dll
│       │   │   │   ├── platforms
│       │   │   │   │   ├── qdirect2d.dll
│       │   │   │   │   ├── qminimal.dll
│       │   │   │   │   ├── qoffscreen.dll
│       │   │   │   │   └── qwindows.dll
│       │   │   │   ├── styles
│       │   │   │   │   └── qmodernwindowsstyle.dll
│       │   │   │   └── tls
│       │   │   │       ├── qcertonlybackend.dll
│       │   │   │       ├── qopensslbackend.dll
│       │   │   │       └── qschannelbackend.dll
│       │   │   ├── translations
│       │   │   │   ├── qt_ar.qm
│       │   │   │   ├── qt_bg.qm
│       │   │   │   ├── qt_ca.qm
│       │   │   │   ├── qt_cs.qm
│       │   │   │   ├── qt_da.qm
│       │   │   │   ├── qt_de.qm
│       │   │   │   ├── qt_en.qm
│       │   │   │   ├── qt_es.qm
│       │   │   │   ├── qt_fa.qm
│       │   │   │   ├── qt_fi.qm
│       │   │   │   ├── qt_fr.qm
│       │   │   │   ├── qt_gd.qm
│       │   │   │   ├── qt_gl.qm
│       │   │   │   ├── qt_he.qm
│       │   │   │   ├── qt_hr.qm
│       │   │   │   ├── qt_hu.qm
│       │   │   │   ├── qt_it.qm
│       │   │   │   ├── qt_ja.qm
│       │   │   │   ├── qt_ka.qm
│       │   │   │   ├── qt_ko.qm
│       │   │   │   ├── qt_lt.qm
│       │   │   │   ├── qt_lv.qm
│       │   │   │   ├── qt_nl.qm
│       │   │   │   ├── qt_nn.qm
│       │   │   │   ├── qt_pl.qm
│       │   │   │   ├── qt_pt_BR.qm
│       │   │   │   ├── qt_pt_PT.qm
│       │   │   │   ├── qt_ru.qm
│       │   │   │   ├── qt_sk.qm
│       │   │   │   ├── qt_sl.qm
│       │   │   │   ├── qt_sv.qm
│       │   │   │   ├── qt_tr.qm
│       │   │   │   ├── qt_uk.qm
│       │   │   │   ├── qt_zh_CN.qm
│       │   │   │   ├── qt_zh_TW.qm
│       │   │   │   ├── qtbase_ar.qm
│       │   │   │   ├── qtbase_bg.qm
│       │   │   │   ├── qtbase_ca.qm
│       │   │   │   ├── qtbase_cs.qm
│       │   │   │   ├── qtbase_da.qm
│       │   │   │   ├── qtbase_de.qm
│       │   │   │   ├── qtbase_en.qm
│       │   │   │   ├── qtbase_es.qm
│       │   │   │   ├── qtbase_fa.qm
│       │   │   │   ├── qtbase_fi.qm
│       │   │   │   ├── qtbase_fr.qm
│       │   │   │   ├── qtbase_gd.qm
│       │   │   │   ├── qtbase_he.qm
│       │   │   │   ├── qtbase_hr.qm
│       │   │   │   ├── qtbase_hu.qm
│       │   │   │   ├── qtbase_it.qm
│       │   │   │   ├── qtbase_ja.qm
│       │   │   │   ├── qtbase_ka.qm
│       │   │   │   ├── qtbase_ko.qm
│       │   │   │   ├── qtbase_lv.qm
│       │   │   │   ├── qtbase_nl.qm
│       │   │   │   ├── qtbase_nn.qm
│       │   │   │   ├── qtbase_pl.qm
│       │   │   │   ├── qtbase_pt_BR.qm
│       │   │   │   ├── qtbase_ru.qm
│       │   │   │   ├── qtbase_sk.qm
│       │   │   │   ├── qtbase_tr.qm
│       │   │   │   ├── qtbase_uk.qm
│       │   │   │   ├── qtbase_zh_CN.qm
│       │   │   │   └── qtbase_zh_TW.qm
│       │   │   ├── pyside6.abi3.dll
│       │   │   ├── Qt6Core.dll
│       │   │   ├── Qt6Gui.dll
│       │   │   ├── Qt6Network.dll
│       │   │   ├── Qt6OpenGL.dll
│       │   │   ├── Qt6Pdf.dll
│       │   │   ├── Qt6Qml.dll
│       │   │   ├── Qt6QmlMeta.dll
│       │   │   ├── Qt6QmlModels.dll
│       │   │   ├── Qt6QmlWorkerScript.dll
│       │   │   ├── Qt6Quick.dll
│       │   │   ├── Qt6Svg.dll
│       │   │   ├── Qt6VirtualKeyboard.dll
│       │   │   ├── Qt6Widgets.dll
│       │   │   ├── QtCore.pyd
│       │   │   ├── QtGui.pyd
│       │   │   ├── QtNetwork.pyd
│       │   │   └── QtWidgets.pyd
│       │   ├── re
│       │   ├── urllib
│       │   ├── watchdog
│       │   │   ├── observers
│       │   │   ├── tricks
│       │   │   ├── utils
│       │   │   └── py.typed
│       │   ├── xml
│       │   │   ├── dom
│       │   │   ├── etree
│       │   │   ├── parsers
│       │   │   └── sax
│       │   ├── xmlrpc
│       │   ├── zipfile
│       │   │   └── _path
│       │   ├── _asyncio.pyd
│       │   ├── _bz2.pyd
│       │   ├── _ctypes.pyd
│       │   ├── _decimal.pyd
│       │   ├── _elementtree.pyd
│       │   ├── _hashlib.pyd
│       │   ├── _lzma.pyd
│       │   ├── _multiprocessing.pyd
│       │   ├── _overlapped.pyd
│       │   ├── _queue.pyd
│       │   ├── _socket.pyd
│       │   ├── _ssl.pyd
│       │   ├── _win32sysloader.pyd
│       │   ├── _wmi.pyd
│       │   ├── ffi-7.dll
│       │   ├── ffi-8.dll
│       │   ├── ffi.dll
│       │   ├── libbz2.dll
│       │   ├── libcrypto-3-x64.dll
│       │   ├── libexpat.dll
│       │   ├── liblzma.dll
│       │   ├── library.dat
│       │   ├── library.zip
│       │   ├── libssl-3-x64.dll
│       │   ├── pyexpat.pyd
│       │   ├── pywintypes312.dll
│       │   ├── select.pyd
│       │   ├── shiboken6.abi3.dll
│       │   ├── shiboken6.Shiboken.pyd
│       │   ├── unicodedata.pyd
│       │   └── win32api.pyd
│       ├── res
│       │   ├── Add.ico
│       │   ├── check.ico
│       │   ├── dlc.ico
│       │   ├── input.ico
│       │   ├── menu.ico
│       │   ├── mods.ico
│       │   ├── modset.ico
│       │   ├── qt.conf
│       │   ├── rem.ico
│       │   ├── settings.ico
│       │   ├── user.ico
│       │   ├── w3a.ico
│       │   └── xml.ico
│       ├── share
│       │   └── licenses
│       │       └── vc_redist
│       │           ├── LICENSE.RTF
│       │           └── LICENSE.txt
│       ├── tools
│       │   └── 7zip
│       │       ├── 7z.dll
│       │       ├── 7z.exe
│       │       └── License.txt
│       ├── translations
│       │   ├── Chinese.qm
│       │   ├── Deutsch.qm
│       │   ├── English.qm
│       │   ├── Polish.qm
│       │   ├── Russian.qm
│       │   ├── Srpski.qm
│       │   ├── Traditional Chinese.qm
│       │   └── Turkish.qm
│       ├── concrt140.dll
│       ├── frozen_application_license.txt
│       ├── LICENSE
│       ├── msvcp140.dll
│       ├── msvcp140_1.dll
│       ├── msvcp140_2.dll
│       ├── msvcp140_atomic_wait.dll
│       ├── msvcp140_codecvt_ids.dll
│       ├── python3.dll
│       ├── python312.dll
│       ├── qt.conf
│       ├── TheWitcher3ModManager.exe
│       ├── vcamp140.dll
│       ├── vccorlib140.dll
│       ├── vcomp140.dll
│       ├── vcruntime140.dll
│       ├── vcruntime140_1.dll
│       ├── vcruntime140_threads.dll
│       └── zlib.dll
├── mapping
│   └── category_mapping.yaml
├── res
│   ├── Add.ico
│   ├── check.ico
│   ├── dlc.ico
│   ├── input.ico
│   ├── menu.ico
│   ├── mods.ico
│   ├── modset.ico
│   ├── qt.conf
│   ├── rem.ico
│   ├── settings.ico
│   ├── user.ico
│   ├── w3a.ico
│   └── xml.ico
├── src
│   ├── configuration
│   │   ├── __init__.py
│   │   └── config.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── fetcher.py
│   │   ├── installer.py
│   │   └── model.py
│   ├── domain
│   │   ├── __init__.py
│   │   ├── key.py
│   │   ├── mod.py
│   │   └── usersetting.py
│   ├── globals
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   └── data.py
│   ├── gui
│   │   ├── __init__.py
│   │   ├── alerts.py
│   │   ├── category_dialog.py
│   │   ├── description_widget.py
│   │   ├── details_dialog.py
│   │   ├── dialog_preferences.py
│   │   ├── main_widget.py
│   │   ├── main_window.py
│   │   ├── themes.py
│   │   └── tree_widget.py
│   ├── util
│   │   ├── __init__.py
│   │   ├── mod_description_fetcher.py
│   │   ├── syntax.py
│   │   └── util.py
│   └── __init__.py
├── tools
│   └── 7zip
│       ├── 7z.dll
│       ├── 7z.exe
│       └── License.txt
├── translations
│   ├── Chinese.qm
│   ├── Deutsch.qm
│   ├── English.qm
│   ├── Polish.qm
│   ├── Russian.qm
│   ├── Srpski.qm
│   ├── Traditional Chinese.qm
│   └── Turkish.qm
├── .editorconfig
├── .gitignore
├── LICENSE
├── main.py
├── pdm.lock
├── project_structure.md
├── project_structure.txt
├── pyproject.toml
├── Readme.md
├── setup.cfg
├── setup.py
├── ts.pro
└── ts.py