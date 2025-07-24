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
│       │   ├── api
│       │   ├── asyncio
│       │   ├── backports
│       │   │   └── tarfile
│       │   │       └── compat
│       │   ├── bs4
│       │   │   ├── builder
│       │   │   ├── tests
│       │   │   │   └── fuzz
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-4670634698080256.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-4818336571064320.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-4999465949331456.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5000587759190016.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5167584867909632.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5270998950477824.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5375146639360000.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5492400320282624.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5703933063462912.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5843991618256896.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-5984173902397440.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-6124268085182464.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-6241471367348224.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-6306874195312640.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-6450958476902400.testcase
│       │   │   │       ├── clusterfuzz-testcase-minimized-bs4_fuzzer-6600557255327744.testcase
│       │   │   │       ├── crash-0d306a50c8ed8bcd0785b67000fcd5dea1d33f08.testcase
│       │   │   │       └── crash-ffbdfa8a2b26f13537b68d3794b0478a4090ee4a.testcase
│       │   │   └── py.typed
│       │   ├── certifi
│       │   │   ├── cacert.pem
│       │   │   └── py.typed
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
│       │   ├── html
│       │   ├── http
│       │   ├── idna
│       │   │   └── py.typed
│       │   ├── importlib
│       │   │   ├── metadata
│       │   │   └── resources
│       │   ├── jaraco
│       │   │   ├── functools
│       │   │   │   ├── __init__.pyi
│       │   │   │   └── py.typed
│       │   │   └── text
│       │   │       └── Lorem ipsum.txt
│       │   ├── json
│       │   ├── logging
│       │   ├── logs
│       │   ├── lxml
│       │   │   ├── html
│       │   │   │   ├── _difflib.cp312-win_amd64.pyd
│       │   │   │   └── diff.cp312-win_amd64.pyd
│       │   │   ├── includes
│       │   │   │   ├── extlibs
│       │   │   │   │   ├── zconf.h
│       │   │   │   │   └── zlib.h
│       │   │   │   ├── libexslt
│       │   │   │   │   ├── exslt.h
│       │   │   │   │   ├── exsltconfig.h
│       │   │   │   │   ├── exsltexports.h
│       │   │   │   │   └── libexslt.h
│       │   │   │   ├── libxml
│       │   │   │   │   ├── c14n.h
│       │   │   │   │   ├── catalog.h
│       │   │   │   │   ├── chvalid.h
│       │   │   │   │   ├── debugXML.h
│       │   │   │   │   ├── dict.h
│       │   │   │   │   ├── encoding.h
│       │   │   │   │   ├── entities.h
│       │   │   │   │   ├── globals.h
│       │   │   │   │   ├── hash.h
│       │   │   │   │   ├── HTMLparser.h
│       │   │   │   │   ├── HTMLtree.h
│       │   │   │   │   ├── list.h
│       │   │   │   │   ├── nanoftp.h
│       │   │   │   │   ├── nanohttp.h
│       │   │   │   │   ├── parser.h
│       │   │   │   │   ├── parserInternals.h
│       │   │   │   │   ├── pattern.h
│       │   │   │   │   ├── relaxng.h
│       │   │   │   │   ├── SAX.h
│       │   │   │   │   ├── SAX2.h
│       │   │   │   │   ├── schemasInternals.h
│       │   │   │   │   ├── schematron.h
│       │   │   │   │   ├── threads.h
│       │   │   │   │   ├── tree.h
│       │   │   │   │   ├── uri.h
│       │   │   │   │   ├── valid.h
│       │   │   │   │   ├── xinclude.h
│       │   │   │   │   ├── xlink.h
│       │   │   │   │   ├── xmlautomata.h
│       │   │   │   │   ├── xmlerror.h
│       │   │   │   │   ├── xmlexports.h
│       │   │   │   │   ├── xmlIO.h
│       │   │   │   │   ├── xmlmemory.h
│       │   │   │   │   ├── xmlmodule.h
│       │   │   │   │   ├── xmlreader.h
│       │   │   │   │   ├── xmlregexp.h
│       │   │   │   │   ├── xmlsave.h
│       │   │   │   │   ├── xmlschemas.h
│       │   │   │   │   ├── xmlschemastypes.h
│       │   │   │   │   ├── xmlstring.h
│       │   │   │   │   ├── xmlunicode.h
│       │   │   │   │   ├── xmlversion.h
│       │   │   │   │   ├── xmlwriter.h
│       │   │   │   │   ├── xpath.h
│       │   │   │   │   ├── xpathInternals.h
│       │   │   │   │   └── xpointer.h
│       │   │   │   ├── libxslt
│       │   │   │   │   ├── attributes.h
│       │   │   │   │   ├── documents.h
│       │   │   │   │   ├── extensions.h
│       │   │   │   │   ├── extra.h
│       │   │   │   │   ├── functions.h
│       │   │   │   │   ├── imports.h
│       │   │   │   │   ├── keys.h
│       │   │   │   │   ├── libxslt.h
│       │   │   │   │   ├── namespaces.h
│       │   │   │   │   ├── numbersInternals.h
│       │   │   │   │   ├── preproc.h
│       │   │   │   │   ├── security.h
│       │   │   │   │   ├── templates.h
│       │   │   │   │   ├── transform.h
│       │   │   │   │   ├── trio.h
│       │   │   │   │   ├── triodef.h
│       │   │   │   │   ├── variables.h
│       │   │   │   │   ├── win32config.h
│       │   │   │   │   ├── xslt.h
│       │   │   │   │   ├── xsltconfig.h
│       │   │   │   │   ├── xsltexports.h
│       │   │   │   │   ├── xsltInternals.h
│       │   │   │   │   ├── xsltlocale.h
│       │   │   │   │   └── xsltutils.h
│       │   │   │   ├── __init__.pxd
│       │   │   │   ├── c14n.pxd
│       │   │   │   ├── config.pxd
│       │   │   │   ├── dtdvalid.pxd
│       │   │   │   ├── etree_defs.h
│       │   │   │   ├── etreepublic.pxd
│       │   │   │   ├── htmlparser.pxd
│       │   │   │   ├── lxml-version.h
│       │   │   │   ├── relaxng.pxd
│       │   │   │   ├── schematron.pxd
│       │   │   │   ├── tree.pxd
│       │   │   │   ├── uri.pxd
│       │   │   │   ├── xinclude.pxd
│       │   │   │   ├── xmlerror.pxd
│       │   │   │   ├── xmlparser.pxd
│       │   │   │   ├── xmlschema.pxd
│       │   │   │   ├── xpath.pxd
│       │   │   │   └── xslt.pxd
│       │   │   ├── isoschematron
│       │   │   │   └── resources
│       │   │   │       ├── rng
│       │   │   │       │   └── iso-schematron.rng
│       │   │   │       └── xsl
│       │   │   │           ├── iso-schematron-xslt1
│       │   │   │           │   ├── iso_abstract_expand.xsl
│       │   │   │           │   ├── iso_dsdl_include.xsl
│       │   │   │           │   ├── iso_schematron_message.xsl
│       │   │   │           │   ├── iso_schematron_skeleton_for_xslt1.xsl
│       │   │   │           │   ├── iso_svrl_for_xslt1.xsl
│       │   │   │           │   └── readme.txt
│       │   │   │           ├── RNG2Schtrn.xsl
│       │   │   │           └── XSD2Schtrn.xsl
│       │   │   ├── _elementpath.cp312-win_amd64.pyd
│       │   │   ├── apihelpers.pxi
│       │   │   ├── builder.cp312-win_amd64.pyd
│       │   │   ├── classlookup.pxi
│       │   │   ├── cleanup.pxi
│       │   │   ├── debug.pxi
│       │   │   ├── docloader.pxi
│       │   │   ├── dtd.pxi
│       │   │   ├── etree.cp312-win_amd64.pyd
│       │   │   ├── etree.h
│       │   │   ├── etree.pyx
│       │   │   ├── etree_api.h
│       │   │   ├── extensions.pxi
│       │   │   ├── iterparse.pxi
│       │   │   ├── lxml.etree.h
│       │   │   ├── lxml.etree_api.h
│       │   │   ├── nsclasses.pxi
│       │   │   ├── objectify.cp312-win_amd64.pyd
│       │   │   ├── objectify.pyx
│       │   │   ├── objectpath.pxi
│       │   │   ├── parser.pxi
│       │   │   ├── parsertarget.pxi
│       │   │   ├── proxy.pxi
│       │   │   ├── public-api.pxi
│       │   │   ├── readonlytree.pxi
│       │   │   ├── relaxng.pxi
│       │   │   ├── sax.cp312-win_amd64.pyd
│       │   │   ├── saxparser.pxi
│       │   │   ├── schematron.pxi
│       │   │   ├── serializer.pxi
│       │   │   ├── xinclude.pxi
│       │   │   ├── xmlerror.pxi
│       │   │   ├── xmlid.pxi
│       │   │   ├── xmlschema.pxi
│       │   │   ├── xpath.pxi
│       │   │   ├── xslt.pxi
│       │   │   └── xsltext.pxi
│       │   ├── mapping
│       │   │   ├── category_mapping.yaml
│       │   │   └── update_status.json
│       │   ├── more_itertools
│       │   │   ├── __init__.pyi
│       │   │   ├── more.pyi
│       │   │   ├── py.typed
│       │   │   └── recipes.pyi
│       │   ├── multiprocessing
│       │   │   └── dummy
│       │   ├── packaging
│       │   │   ├── licenses
│       │   │   └── py.typed
│       │   ├── pkg_resources
│       │   │   ├── api_tests.txt
│       │   │   └── py.typed
│       │   ├── platformdirs
│       │   │   └── py.typed
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
│       │   ├── pytz
│       │   │   └── zoneinfo
│       │   │       ├── Africa
│       │   │       │   ├── Abidjan
│       │   │       │   ├── Accra
│       │   │       │   ├── Addis_Ababa
│       │   │       │   ├── Algiers
│       │   │       │   ├── Asmara
│       │   │       │   ├── Asmera
│       │   │       │   ├── Bamako
│       │   │       │   ├── Bangui
│       │   │       │   ├── Banjul
│       │   │       │   ├── Bissau
│       │   │       │   ├── Blantyre
│       │   │       │   ├── Brazzaville
│       │   │       │   ├── Bujumbura
│       │   │       │   ├── Cairo
│       │   │       │   ├── Casablanca
│       │   │       │   ├── Ceuta
│       │   │       │   ├── Conakry
│       │   │       │   ├── Dakar
│       │   │       │   ├── Dar_es_Salaam
│       │   │       │   ├── Djibouti
│       │   │       │   ├── Douala
│       │   │       │   ├── El_Aaiun
│       │   │       │   ├── Freetown
│       │   │       │   ├── Gaborone
│       │   │       │   ├── Harare
│       │   │       │   ├── Johannesburg
│       │   │       │   ├── Juba
│       │   │       │   ├── Kampala
│       │   │       │   ├── Khartoum
│       │   │       │   ├── Kigali
│       │   │       │   ├── Kinshasa
│       │   │       │   ├── Lagos
│       │   │       │   ├── Libreville
│       │   │       │   ├── Lome
│       │   │       │   ├── Luanda
│       │   │       │   ├── Lubumbashi
│       │   │       │   ├── Lusaka
│       │   │       │   ├── Malabo
│       │   │       │   ├── Maputo
│       │   │       │   ├── Maseru
│       │   │       │   ├── Mbabane
│       │   │       │   ├── Mogadishu
│       │   │       │   ├── Monrovia
│       │   │       │   ├── Nairobi
│       │   │       │   ├── Ndjamena
│       │   │       │   ├── Niamey
│       │   │       │   ├── Nouakchott
│       │   │       │   ├── Ouagadougou
│       │   │       │   ├── Porto-Novo
│       │   │       │   ├── Sao_Tome
│       │   │       │   ├── Timbuktu
│       │   │       │   ├── Tripoli
│       │   │       │   ├── Tunis
│       │   │       │   └── Windhoek
│       │   │       ├── America
│       │   │       │   ├── Argentina
│       │   │       │   │   ├── Buenos_Aires
│       │   │       │   │   ├── Catamarca
│       │   │       │   │   ├── ComodRivadavia
│       │   │       │   │   ├── Cordoba
│       │   │       │   │   ├── Jujuy
│       │   │       │   │   ├── La_Rioja
│       │   │       │   │   ├── Mendoza
│       │   │       │   │   ├── Rio_Gallegos
│       │   │       │   │   ├── Salta
│       │   │       │   │   ├── San_Juan
│       │   │       │   │   ├── San_Luis
│       │   │       │   │   ├── Tucuman
│       │   │       │   │   └── Ushuaia
│       │   │       │   ├── Indiana
│       │   │       │   │   ├── Indianapolis
│       │   │       │   │   ├── Knox
│       │   │       │   │   ├── Marengo
│       │   │       │   │   ├── Petersburg
│       │   │       │   │   ├── Tell_City
│       │   │       │   │   ├── Vevay
│       │   │       │   │   ├── Vincennes
│       │   │       │   │   └── Winamac
│       │   │       │   ├── Kentucky
│       │   │       │   │   ├── Louisville
│       │   │       │   │   └── Monticello
│       │   │       │   ├── North_Dakota
│       │   │       │   │   ├── Beulah
│       │   │       │   │   ├── Center
│       │   │       │   │   └── New_Salem
│       │   │       │   ├── Adak
│       │   │       │   ├── Anchorage
│       │   │       │   ├── Anguilla
│       │   │       │   ├── Antigua
│       │   │       │   ├── Araguaina
│       │   │       │   ├── Aruba
│       │   │       │   ├── Asuncion
│       │   │       │   ├── Atikokan
│       │   │       │   ├── Atka
│       │   │       │   ├── Bahia
│       │   │       │   ├── Bahia_Banderas
│       │   │       │   ├── Barbados
│       │   │       │   ├── Belem
│       │   │       │   ├── Belize
│       │   │       │   ├── Blanc-Sablon
│       │   │       │   ├── Boa_Vista
│       │   │       │   ├── Bogota
│       │   │       │   ├── Boise
│       │   │       │   ├── Buenos_Aires
│       │   │       │   ├── Cambridge_Bay
│       │   │       │   ├── Campo_Grande
│       │   │       │   ├── Cancun
│       │   │       │   ├── Caracas
│       │   │       │   ├── Catamarca
│       │   │       │   ├── Cayenne
│       │   │       │   ├── Cayman
│       │   │       │   ├── Chicago
│       │   │       │   ├── Chihuahua
│       │   │       │   ├── Ciudad_Juarez
│       │   │       │   ├── Coral_Harbour
│       │   │       │   ├── Cordoba
│       │   │       │   ├── Costa_Rica
│       │   │       │   ├── Coyhaique
│       │   │       │   ├── Creston
│       │   │       │   ├── Cuiaba
│       │   │       │   ├── Curacao
│       │   │       │   ├── Danmarkshavn
│       │   │       │   ├── Dawson
│       │   │       │   ├── Dawson_Creek
│       │   │       │   ├── Denver
│       │   │       │   ├── Detroit
│       │   │       │   ├── Dominica
│       │   │       │   ├── Edmonton
│       │   │       │   ├── Eirunepe
│       │   │       │   ├── El_Salvador
│       │   │       │   ├── Ensenada
│       │   │       │   ├── Fort_Nelson
│       │   │       │   ├── Fort_Wayne
│       │   │       │   ├── Fortaleza
│       │   │       │   ├── Glace_Bay
│       │   │       │   ├── Godthab
│       │   │       │   ├── Goose_Bay
│       │   │       │   ├── Grand_Turk
│       │   │       │   ├── Grenada
│       │   │       │   ├── Guadeloupe
│       │   │       │   ├── Guatemala
│       │   │       │   ├── Guayaquil
│       │   │       │   ├── Guyana
│       │   │       │   ├── Halifax
│       │   │       │   ├── Havana
│       │   │       │   ├── Hermosillo
│       │   │       │   ├── Indianapolis
│       │   │       │   ├── Inuvik
│       │   │       │   ├── Iqaluit
│       │   │       │   ├── Jamaica
│       │   │       │   ├── Jujuy
│       │   │       │   ├── Juneau
│       │   │       │   ├── Knox_IN
│       │   │       │   ├── Kralendijk
│       │   │       │   ├── La_Paz
│       │   │       │   ├── Lima
│       │   │       │   ├── Los_Angeles
│       │   │       │   ├── Louisville
│       │   │       │   ├── Lower_Princes
│       │   │       │   ├── Maceio
│       │   │       │   ├── Managua
│       │   │       │   ├── Manaus
│       │   │       │   ├── Marigot
│       │   │       │   ├── Martinique
│       │   │       │   ├── Matamoros
│       │   │       │   ├── Mazatlan
│       │   │       │   ├── Mendoza
│       │   │       │   ├── Menominee
│       │   │       │   ├── Merida
│       │   │       │   ├── Metlakatla
│       │   │       │   ├── Mexico_City
│       │   │       │   ├── Miquelon
│       │   │       │   ├── Moncton
│       │   │       │   ├── Monterrey
│       │   │       │   ├── Montevideo
│       │   │       │   ├── Montreal
│       │   │       │   ├── Montserrat
│       │   │       │   ├── Nassau
│       │   │       │   ├── New_York
│       │   │       │   ├── Nipigon
│       │   │       │   ├── Nome
│       │   │       │   ├── Noronha
│       │   │       │   ├── Nuuk
│       │   │       │   ├── Ojinaga
│       │   │       │   ├── Panama
│       │   │       │   ├── Pangnirtung
│       │   │       │   ├── Paramaribo
│       │   │       │   ├── Phoenix
│       │   │       │   ├── Port-au-Prince
│       │   │       │   ├── Port_of_Spain
│       │   │       │   ├── Porto_Acre
│       │   │       │   ├── Porto_Velho
│       │   │       │   ├── Puerto_Rico
│       │   │       │   ├── Punta_Arenas
│       │   │       │   ├── Rainy_River
│       │   │       │   ├── Rankin_Inlet
│       │   │       │   ├── Recife
│       │   │       │   ├── Regina
│       │   │       │   ├── Resolute
│       │   │       │   ├── Rio_Branco
│       │   │       │   ├── Rosario
│       │   │       │   ├── Santa_Isabel
│       │   │       │   ├── Santarem
│       │   │       │   ├── Santiago
│       │   │       │   ├── Santo_Domingo
│       │   │       │   ├── Sao_Paulo
│       │   │       │   ├── Scoresbysund
│       │   │       │   ├── Shiprock
│       │   │       │   ├── Sitka
│       │   │       │   ├── St_Barthelemy
│       │   │       │   ├── St_Johns
│       │   │       │   ├── St_Kitts
│       │   │       │   ├── St_Lucia
│       │   │       │   ├── St_Thomas
│       │   │       │   ├── St_Vincent
│       │   │       │   ├── Swift_Current
│       │   │       │   ├── Tegucigalpa
│       │   │       │   ├── Thule
│       │   │       │   ├── Thunder_Bay
│       │   │       │   ├── Tijuana
│       │   │       │   ├── Toronto
│       │   │       │   ├── Tortola
│       │   │       │   ├── Vancouver
│       │   │       │   ├── Virgin
│       │   │       │   ├── Whitehorse
│       │   │       │   ├── Winnipeg
│       │   │       │   ├── Yakutat
│       │   │       │   └── Yellowknife
│       │   │       ├── Antarctica
│       │   │       │   ├── Casey
│       │   │       │   ├── Davis
│       │   │       │   ├── DumontDUrville
│       │   │       │   ├── Macquarie
│       │   │       │   ├── Mawson
│       │   │       │   ├── McMurdo
│       │   │       │   ├── Palmer
│       │   │       │   ├── Rothera
│       │   │       │   ├── South_Pole
│       │   │       │   ├── Syowa
│       │   │       │   ├── Troll
│       │   │       │   └── Vostok
│       │   │       ├── Arctic
│       │   │       │   └── Longyearbyen
│       │   │       ├── Asia
│       │   │       │   ├── Aden
│       │   │       │   ├── Almaty
│       │   │       │   ├── Amman
│       │   │       │   ├── Anadyr
│       │   │       │   ├── Aqtau
│       │   │       │   ├── Aqtobe
│       │   │       │   ├── Ashgabat
│       │   │       │   ├── Ashkhabad
│       │   │       │   ├── Atyrau
│       │   │       │   ├── Baghdad
│       │   │       │   ├── Bahrain
│       │   │       │   ├── Baku
│       │   │       │   ├── Bangkok
│       │   │       │   ├── Barnaul
│       │   │       │   ├── Beirut
│       │   │       │   ├── Bishkek
│       │   │       │   ├── Brunei
│       │   │       │   ├── Calcutta
│       │   │       │   ├── Chita
│       │   │       │   ├── Choibalsan
│       │   │       │   ├── Chongqing
│       │   │       │   ├── Chungking
│       │   │       │   ├── Colombo
│       │   │       │   ├── Dacca
│       │   │       │   ├── Damascus
│       │   │       │   ├── Dhaka
│       │   │       │   ├── Dili
│       │   │       │   ├── Dubai
│       │   │       │   ├── Dushanbe
│       │   │       │   ├── Famagusta
│       │   │       │   ├── Gaza
│       │   │       │   ├── Harbin
│       │   │       │   ├── Hebron
│       │   │       │   ├── Ho_Chi_Minh
│       │   │       │   ├── Hong_Kong
│       │   │       │   ├── Hovd
│       │   │       │   ├── Irkutsk
│       │   │       │   ├── Istanbul
│       │   │       │   ├── Jakarta
│       │   │       │   ├── Jayapura
│       │   │       │   ├── Jerusalem
│       │   │       │   ├── Kabul
│       │   │       │   ├── Kamchatka
│       │   │       │   ├── Karachi
│       │   │       │   ├── Kashgar
│       │   │       │   ├── Kathmandu
│       │   │       │   ├── Katmandu
│       │   │       │   ├── Khandyga
│       │   │       │   ├── Kolkata
│       │   │       │   ├── Krasnoyarsk
│       │   │       │   ├── Kuala_Lumpur
│       │   │       │   ├── Kuching
│       │   │       │   ├── Kuwait
│       │   │       │   ├── Macao
│       │   │       │   ├── Macau
│       │   │       │   ├── Magadan
│       │   │       │   ├── Makassar
│       │   │       │   ├── Manila
│       │   │       │   ├── Muscat
│       │   │       │   ├── Nicosia
│       │   │       │   ├── Novokuznetsk
│       │   │       │   ├── Novosibirsk
│       │   │       │   ├── Omsk
│       │   │       │   ├── Oral
│       │   │       │   ├── Phnom_Penh
│       │   │       │   ├── Pontianak
│       │   │       │   ├── Pyongyang
│       │   │       │   ├── Qatar
│       │   │       │   ├── Qostanay
│       │   │       │   ├── Qyzylorda
│       │   │       │   ├── Rangoon
│       │   │       │   ├── Riyadh
│       │   │       │   ├── Saigon
│       │   │       │   ├── Sakhalin
│       │   │       │   ├── Samarkand
│       │   │       │   ├── Seoul
│       │   │       │   ├── Shanghai
│       │   │       │   ├── Singapore
│       │   │       │   ├── Srednekolymsk
│       │   │       │   ├── Taipei
│       │   │       │   ├── Tashkent
│       │   │       │   ├── Tbilisi
│       │   │       │   ├── Tehran
│       │   │       │   ├── Tel_Aviv
│       │   │       │   ├── Thimbu
│       │   │       │   ├── Thimphu
│       │   │       │   ├── Tokyo
│       │   │       │   ├── Tomsk
│       │   │       │   ├── Ujung_Pandang
│       │   │       │   ├── Ulaanbaatar
│       │   │       │   ├── Ulan_Bator
│       │   │       │   ├── Urumqi
│       │   │       │   ├── Ust-Nera
│       │   │       │   ├── Vientiane
│       │   │       │   ├── Vladivostok
│       │   │       │   ├── Yakutsk
│       │   │       │   ├── Yangon
│       │   │       │   ├── Yekaterinburg
│       │   │       │   └── Yerevan
│       │   │       ├── Atlantic
│       │   │       │   ├── Azores
│       │   │       │   ├── Bermuda
│       │   │       │   ├── Canary
│       │   │       │   ├── Cape_Verde
│       │   │       │   ├── Faeroe
│       │   │       │   ├── Faroe
│       │   │       │   ├── Jan_Mayen
│       │   │       │   ├── Madeira
│       │   │       │   ├── Reykjavik
│       │   │       │   ├── South_Georgia
│       │   │       │   ├── St_Helena
│       │   │       │   └── Stanley
│       │   │       ├── Australia
│       │   │       │   ├── ACT
│       │   │       │   ├── Adelaide
│       │   │       │   ├── Brisbane
│       │   │       │   ├── Broken_Hill
│       │   │       │   ├── Canberra
│       │   │       │   ├── Currie
│       │   │       │   ├── Darwin
│       │   │       │   ├── Eucla
│       │   │       │   ├── Hobart
│       │   │       │   ├── LHI
│       │   │       │   ├── Lindeman
│       │   │       │   ├── Lord_Howe
│       │   │       │   ├── Melbourne
│       │   │       │   ├── North
│       │   │       │   ├── NSW
│       │   │       │   ├── Perth
│       │   │       │   ├── Queensland
│       │   │       │   ├── South
│       │   │       │   ├── Sydney
│       │   │       │   ├── Tasmania
│       │   │       │   ├── Victoria
│       │   │       │   ├── West
│       │   │       │   └── Yancowinna
│       │   │       ├── Brazil
│       │   │       │   ├── Acre
│       │   │       │   ├── DeNoronha
│       │   │       │   ├── East
│       │   │       │   └── West
│       │   │       ├── Canada
│       │   │       │   ├── Atlantic
│       │   │       │   ├── Central
│       │   │       │   ├── Eastern
│       │   │       │   ├── Mountain
│       │   │       │   ├── Newfoundland
│       │   │       │   ├── Pacific
│       │   │       │   ├── Saskatchewan
│       │   │       │   └── Yukon
│       │   │       ├── Chile
│       │   │       │   ├── Continental
│       │   │       │   └── EasterIsland
│       │   │       ├── Etc
│       │   │       │   ├── GMT
│       │   │       │   ├── GMT+0
│       │   │       │   ├── GMT+1
│       │   │       │   ├── GMT+10
│       │   │       │   ├── GMT+11
│       │   │       │   ├── GMT+12
│       │   │       │   ├── GMT+2
│       │   │       │   ├── GMT+3
│       │   │       │   ├── GMT+4
│       │   │       │   ├── GMT+5
│       │   │       │   ├── GMT+6
│       │   │       │   ├── GMT+7
│       │   │       │   ├── GMT+8
│       │   │       │   ├── GMT+9
│       │   │       │   ├── GMT-0
│       │   │       │   ├── GMT-1
│       │   │       │   ├── GMT-10
│       │   │       │   ├── GMT-11
│       │   │       │   ├── GMT-12
│       │   │       │   ├── GMT-13
│       │   │       │   ├── GMT-14
│       │   │       │   ├── GMT-2
│       │   │       │   ├── GMT-3
│       │   │       │   ├── GMT-4
│       │   │       │   ├── GMT-5
│       │   │       │   ├── GMT-6
│       │   │       │   ├── GMT-7
│       │   │       │   ├── GMT-8
│       │   │       │   ├── GMT-9
│       │   │       │   ├── GMT0
│       │   │       │   ├── Greenwich
│       │   │       │   ├── UCT
│       │   │       │   ├── Universal
│       │   │       │   ├── UTC
│       │   │       │   └── Zulu
│       │   │       ├── Europe
│       │   │       │   ├── Amsterdam
│       │   │       │   ├── Andorra
│       │   │       │   ├── Astrakhan
│       │   │       │   ├── Athens
│       │   │       │   ├── Belfast
│       │   │       │   ├── Belgrade
│       │   │       │   ├── Berlin
│       │   │       │   ├── Bratislava
│       │   │       │   ├── Brussels
│       │   │       │   ├── Bucharest
│       │   │       │   ├── Budapest
│       │   │       │   ├── Busingen
│       │   │       │   ├── Chisinau
│       │   │       │   ├── Copenhagen
│       │   │       │   ├── Dublin
│       │   │       │   ├── Gibraltar
│       │   │       │   ├── Guernsey
│       │   │       │   ├── Helsinki
│       │   │       │   ├── Isle_of_Man
│       │   │       │   ├── Istanbul
│       │   │       │   ├── Jersey
│       │   │       │   ├── Kaliningrad
│       │   │       │   ├── Kiev
│       │   │       │   ├── Kirov
│       │   │       │   ├── Kyiv
│       │   │       │   ├── Lisbon
│       │   │       │   ├── Ljubljana
│       │   │       │   ├── London
│       │   │       │   ├── Luxembourg
│       │   │       │   ├── Madrid
│       │   │       │   ├── Malta
│       │   │       │   ├── Mariehamn
│       │   │       │   ├── Minsk
│       │   │       │   ├── Monaco
│       │   │       │   ├── Moscow
│       │   │       │   ├── Nicosia
│       │   │       │   ├── Oslo
│       │   │       │   ├── Paris
│       │   │       │   ├── Podgorica
│       │   │       │   ├── Prague
│       │   │       │   ├── Riga
│       │   │       │   ├── Rome
│       │   │       │   ├── Samara
│       │   │       │   ├── San_Marino
│       │   │       │   ├── Sarajevo
│       │   │       │   ├── Saratov
│       │   │       │   ├── Simferopol
│       │   │       │   ├── Skopje
│       │   │       │   ├── Sofia
│       │   │       │   ├── Stockholm
│       │   │       │   ├── Tallinn
│       │   │       │   ├── Tirane
│       │   │       │   ├── Tiraspol
│       │   │       │   ├── Ulyanovsk
│       │   │       │   ├── Uzhgorod
│       │   │       │   ├── Vaduz
│       │   │       │   ├── Vatican
│       │   │       │   ├── Vienna
│       │   │       │   ├── Vilnius
│       │   │       │   ├── Volgograd
│       │   │       │   ├── Warsaw
│       │   │       │   ├── Zagreb
│       │   │       │   ├── Zaporozhye
│       │   │       │   └── Zurich
│       │   │       ├── Indian
│       │   │       │   ├── Antananarivo
│       │   │       │   ├── Chagos
│       │   │       │   ├── Christmas
│       │   │       │   ├── Cocos
│       │   │       │   ├── Comoro
│       │   │       │   ├── Kerguelen
│       │   │       │   ├── Mahe
│       │   │       │   ├── Maldives
│       │   │       │   ├── Mauritius
│       │   │       │   ├── Mayotte
│       │   │       │   └── Reunion
│       │   │       ├── Mexico
│       │   │       │   ├── BajaNorte
│       │   │       │   ├── BajaSur
│       │   │       │   └── General
│       │   │       ├── Pacific
│       │   │       │   ├── Apia
│       │   │       │   ├── Auckland
│       │   │       │   ├── Bougainville
│       │   │       │   ├── Chatham
│       │   │       │   ├── Chuuk
│       │   │       │   ├── Easter
│       │   │       │   ├── Efate
│       │   │       │   ├── Enderbury
│       │   │       │   ├── Fakaofo
│       │   │       │   ├── Fiji
│       │   │       │   ├── Funafuti
│       │   │       │   ├── Galapagos
│       │   │       │   ├── Gambier
│       │   │       │   ├── Guadalcanal
│       │   │       │   ├── Guam
│       │   │       │   ├── Honolulu
│       │   │       │   ├── Johnston
│       │   │       │   ├── Kanton
│       │   │       │   ├── Kiritimati
│       │   │       │   ├── Kosrae
│       │   │       │   ├── Kwajalein
│       │   │       │   ├── Majuro
│       │   │       │   ├── Marquesas
│       │   │       │   ├── Midway
│       │   │       │   ├── Nauru
│       │   │       │   ├── Niue
│       │   │       │   ├── Norfolk
│       │   │       │   ├── Noumea
│       │   │       │   ├── Pago_Pago
│       │   │       │   ├── Palau
│       │   │       │   ├── Pitcairn
│       │   │       │   ├── Pohnpei
│       │   │       │   ├── Ponape
│       │   │       │   ├── Port_Moresby
│       │   │       │   ├── Rarotonga
│       │   │       │   ├── Saipan
│       │   │       │   ├── Samoa
│       │   │       │   ├── Tahiti
│       │   │       │   ├── Tarawa
│       │   │       │   ├── Tongatapu
│       │   │       │   ├── Truk
│       │   │       │   ├── Wake
│       │   │       │   ├── Wallis
│       │   │       │   └── Yap
│       │   │       ├── US
│       │   │       │   ├── Alaska
│       │   │       │   ├── Aleutian
│       │   │       │   ├── Arizona
│       │   │       │   ├── Central
│       │   │       │   ├── East-Indiana
│       │   │       │   ├── Eastern
│       │   │       │   ├── Hawaii
│       │   │       │   ├── Indiana-Starke
│       │   │       │   ├── Michigan
│       │   │       │   ├── Mountain
│       │   │       │   ├── Pacific
│       │   │       │   └── Samoa
│       │   │       ├── CET
│       │   │       ├── CST6CDT
│       │   │       ├── Cuba
│       │   │       ├── EET
│       │   │       ├── Egypt
│       │   │       ├── Eire
│       │   │       ├── EST
│       │   │       ├── EST5EDT
│       │   │       ├── Factory
│       │   │       ├── GB
│       │   │       ├── GB-Eire
│       │   │       ├── GMT
│       │   │       ├── GMT+0
│       │   │       ├── GMT-0
│       │   │       ├── GMT0
│       │   │       ├── Greenwich
│       │   │       ├── Hongkong
│       │   │       ├── HST
│       │   │       ├── Iceland
│       │   │       ├── Iran
│       │   │       ├── iso3166.tab
│       │   │       ├── Israel
│       │   │       ├── Jamaica
│       │   │       ├── Japan
│       │   │       ├── Kwajalein
│       │   │       ├── leapseconds
│       │   │       ├── Libya
│       │   │       ├── MET
│       │   │       ├── MST
│       │   │       ├── MST7MDT
│       │   │       ├── Navajo
│       │   │       ├── NZ
│       │   │       ├── NZ-CHAT
│       │   │       ├── Poland
│       │   │       ├── Portugal
│       │   │       ├── PRC
│       │   │       ├── PST8PDT
│       │   │       ├── ROC
│       │   │       ├── ROK
│       │   │       ├── Singapore
│       │   │       ├── Turkey
│       │   │       ├── tzdata.zi
│       │   │       ├── UCT
│       │   │       ├── Universal
│       │   │       ├── UTC
│       │   │       ├── W-SU
│       │   │       ├── WET
│       │   │       ├── zone.tab
│       │   │       ├── zone1970.tab
│       │   │       ├── zonenow.tab
│       │   │       └── Zulu
│       │   ├── re
│       │   ├── requests
│       │   ├── schedule
│       │   │   └── py.typed
│       │   ├── soupsieve
│       │   │   └── py.typed
│       │   ├── sqlite3
│       │   ├── urllib
│       │   ├── urllib3
│       │   │   ├── contrib
│       │   │   │   └── emscripten
│       │   │   │       └── emscripten_fetch_worker.js
│       │   │   ├── http2
│       │   │   ├── util
│       │   │   └── py.typed
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
│       │   ├── yaml
│       │   │   └── _yaml.cp312-win_amd64.pyd
│       │   ├── zipfile
│       │   │   └── _path
│       │   ├── zstandard
│       │   │   ├── __init__.pyi
│       │   │   ├── _cffi.cp312-win_amd64.pyd
│       │   │   ├── backend_c.cp312-win_amd64.pyd
│       │   │   └── py.typed
│       │   ├── _asyncio.pyd
│       │   ├── _brotli.cp312-win_amd64.pyd
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
│       │   ├── _sqlite3.pyd
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
│       │   ├── sqlite3.dll
│       │   ├── unicodedata.pyd
│       │   ├── win32api.pyd
│       │   └── win32evtlog.pyd
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
│       │   ├── licenses
│       │   │   └── vc_redist
│       │   │       ├── LICENSE.RTF
│       │   │       └── LICENSE.txt
│       │   └── zoneinfo
│       │       ├── Africa
│       │       │   ├── Abidjan
│       │       │   ├── Accra
│       │       │   ├── Addis_Ababa
│       │       │   ├── Algiers
│       │       │   ├── Asmara
│       │       │   ├── Asmera
│       │       │   ├── Bamako
│       │       │   ├── Bangui
│       │       │   ├── Banjul
│       │       │   ├── Bissau
│       │       │   ├── Blantyre
│       │       │   ├── Brazzaville
│       │       │   ├── Bujumbura
│       │       │   ├── Cairo
│       │       │   ├── Casablanca
│       │       │   ├── Ceuta
│       │       │   ├── Conakry
│       │       │   ├── Dakar
│       │       │   ├── Dar_es_Salaam
│       │       │   ├── Djibouti
│       │       │   ├── Douala
│       │       │   ├── El_Aaiun
│       │       │   ├── Freetown
│       │       │   ├── Gaborone
│       │       │   ├── Harare
│       │       │   ├── Johannesburg
│       │       │   ├── Juba
│       │       │   ├── Kampala
│       │       │   ├── Khartoum
│       │       │   ├── Kigali
│       │       │   ├── Kinshasa
│       │       │   ├── Lagos
│       │       │   ├── Libreville
│       │       │   ├── Lome
│       │       │   ├── Luanda
│       │       │   ├── Lubumbashi
│       │       │   ├── Lusaka
│       │       │   ├── Malabo
│       │       │   ├── Maputo
│       │       │   ├── Maseru
│       │       │   ├── Mbabane
│       │       │   ├── Mogadishu
│       │       │   ├── Monrovia
│       │       │   ├── Nairobi
│       │       │   ├── Ndjamena
│       │       │   ├── Niamey
│       │       │   ├── Nouakchott
│       │       │   ├── Ouagadougou
│       │       │   ├── Porto-Novo
│       │       │   ├── Sao_Tome
│       │       │   ├── Timbuktu
│       │       │   ├── Tripoli
│       │       │   ├── Tunis
│       │       │   └── Windhoek
│       │       ├── America
│       │       │   ├── Argentina
│       │       │   │   ├── Buenos_Aires
│       │       │   │   ├── Catamarca
│       │       │   │   ├── ComodRivadavia
│       │       │   │   ├── Cordoba
│       │       │   │   ├── Jujuy
│       │       │   │   ├── La_Rioja
│       │       │   │   ├── Mendoza
│       │       │   │   ├── Rio_Gallegos
│       │       │   │   ├── Salta
│       │       │   │   ├── San_Juan
│       │       │   │   ├── San_Luis
│       │       │   │   ├── Tucuman
│       │       │   │   └── Ushuaia
│       │       │   ├── Indiana
│       │       │   │   ├── Indianapolis
│       │       │   │   ├── Knox
│       │       │   │   ├── Marengo
│       │       │   │   ├── Petersburg
│       │       │   │   ├── Tell_City
│       │       │   │   ├── Vevay
│       │       │   │   ├── Vincennes
│       │       │   │   └── Winamac
│       │       │   ├── Kentucky
│       │       │   │   ├── Louisville
│       │       │   │   └── Monticello
│       │       │   ├── North_Dakota
│       │       │   │   ├── Beulah
│       │       │   │   ├── Center
│       │       │   │   └── New_Salem
│       │       │   ├── Adak
│       │       │   ├── Anchorage
│       │       │   ├── Anguilla
│       │       │   ├── Antigua
│       │       │   ├── Araguaina
│       │       │   ├── Aruba
│       │       │   ├── Asuncion
│       │       │   ├── Atikokan
│       │       │   ├── Atka
│       │       │   ├── Bahia
│       │       │   ├── Bahia_Banderas
│       │       │   ├── Barbados
│       │       │   ├── Belem
│       │       │   ├── Belize
│       │       │   ├── Blanc-Sablon
│       │       │   ├── Boa_Vista
│       │       │   ├── Bogota
│       │       │   ├── Boise
│       │       │   ├── Buenos_Aires
│       │       │   ├── Cambridge_Bay
│       │       │   ├── Campo_Grande
│       │       │   ├── Cancun
│       │       │   ├── Caracas
│       │       │   ├── Catamarca
│       │       │   ├── Cayenne
│       │       │   ├── Cayman
│       │       │   ├── Chicago
│       │       │   ├── Chihuahua
│       │       │   ├── Ciudad_Juarez
│       │       │   ├── Coral_Harbour
│       │       │   ├── Cordoba
│       │       │   ├── Costa_Rica
│       │       │   ├── Coyhaique
│       │       │   ├── Creston
│       │       │   ├── Cuiaba
│       │       │   ├── Curacao
│       │       │   ├── Danmarkshavn
│       │       │   ├── Dawson
│       │       │   ├── Dawson_Creek
│       │       │   ├── Denver
│       │       │   ├── Detroit
│       │       │   ├── Dominica
│       │       │   ├── Edmonton
│       │       │   ├── Eirunepe
│       │       │   ├── El_Salvador
│       │       │   ├── Ensenada
│       │       │   ├── Fort_Nelson
│       │       │   ├── Fort_Wayne
│       │       │   ├── Fortaleza
│       │       │   ├── Glace_Bay
│       │       │   ├── Godthab
│       │       │   ├── Goose_Bay
│       │       │   ├── Grand_Turk
│       │       │   ├── Grenada
│       │       │   ├── Guadeloupe
│       │       │   ├── Guatemala
│       │       │   ├── Guayaquil
│       │       │   ├── Guyana
│       │       │   ├── Halifax
│       │       │   ├── Havana
│       │       │   ├── Hermosillo
│       │       │   ├── Indianapolis
│       │       │   ├── Inuvik
│       │       │   ├── Iqaluit
│       │       │   ├── Jamaica
│       │       │   ├── Jujuy
│       │       │   ├── Juneau
│       │       │   ├── Knox_IN
│       │       │   ├── Kralendijk
│       │       │   ├── La_Paz
│       │       │   ├── Lima
│       │       │   ├── Los_Angeles
│       │       │   ├── Louisville
│       │       │   ├── Lower_Princes
│       │       │   ├── Maceio
│       │       │   ├── Managua
│       │       │   ├── Manaus
│       │       │   ├── Marigot
│       │       │   ├── Martinique
│       │       │   ├── Matamoros
│       │       │   ├── Mazatlan
│       │       │   ├── Mendoza
│       │       │   ├── Menominee
│       │       │   ├── Merida
│       │       │   ├── Metlakatla
│       │       │   ├── Mexico_City
│       │       │   ├── Miquelon
│       │       │   ├── Moncton
│       │       │   ├── Monterrey
│       │       │   ├── Montevideo
│       │       │   ├── Montreal
│       │       │   ├── Montserrat
│       │       │   ├── Nassau
│       │       │   ├── New_York
│       │       │   ├── Nipigon
│       │       │   ├── Nome
│       │       │   ├── Noronha
│       │       │   ├── Nuuk
│       │       │   ├── Ojinaga
│       │       │   ├── Panama
│       │       │   ├── Pangnirtung
│       │       │   ├── Paramaribo
│       │       │   ├── Phoenix
│       │       │   ├── Port-au-Prince
│       │       │   ├── Port_of_Spain
│       │       │   ├── Porto_Acre
│       │       │   ├── Porto_Velho
│       │       │   ├── Puerto_Rico
│       │       │   ├── Punta_Arenas
│       │       │   ├── Rainy_River
│       │       │   ├── Rankin_Inlet
│       │       │   ├── Recife
│       │       │   ├── Regina
│       │       │   ├── Resolute
│       │       │   ├── Rio_Branco
│       │       │   ├── Rosario
│       │       │   ├── Santa_Isabel
│       │       │   ├── Santarem
│       │       │   ├── Santiago
│       │       │   ├── Santo_Domingo
│       │       │   ├── Sao_Paulo
│       │       │   ├── Scoresbysund
│       │       │   ├── Shiprock
│       │       │   ├── Sitka
│       │       │   ├── St_Barthelemy
│       │       │   ├── St_Johns
│       │       │   ├── St_Kitts
│       │       │   ├── St_Lucia
│       │       │   ├── St_Thomas
│       │       │   ├── St_Vincent
│       │       │   ├── Swift_Current
│       │       │   ├── Tegucigalpa
│       │       │   ├── Thule
│       │       │   ├── Thunder_Bay
│       │       │   ├── Tijuana
│       │       │   ├── Toronto
│       │       │   ├── Tortola
│       │       │   ├── Vancouver
│       │       │   ├── Virgin
│       │       │   ├── Whitehorse
│       │       │   ├── Winnipeg
│       │       │   ├── Yakutat
│       │       │   └── Yellowknife
│       │       ├── Antarctica
│       │       │   ├── Casey
│       │       │   ├── Davis
│       │       │   ├── DumontDUrville
│       │       │   ├── Macquarie
│       │       │   ├── Mawson
│       │       │   ├── McMurdo
│       │       │   ├── Palmer
│       │       │   ├── Rothera
│       │       │   ├── South_Pole
│       │       │   ├── Syowa
│       │       │   ├── Troll
│       │       │   └── Vostok
│       │       ├── Arctic
│       │       │   └── Longyearbyen
│       │       ├── Asia
│       │       │   ├── Aden
│       │       │   ├── Almaty
│       │       │   ├── Amman
│       │       │   ├── Anadyr
│       │       │   ├── Aqtau
│       │       │   ├── Aqtobe
│       │       │   ├── Ashgabat
│       │       │   ├── Ashkhabad
│       │       │   ├── Atyrau
│       │       │   ├── Baghdad
│       │       │   ├── Bahrain
│       │       │   ├── Baku
│       │       │   ├── Bangkok
│       │       │   ├── Barnaul
│       │       │   ├── Beirut
│       │       │   ├── Bishkek
│       │       │   ├── Brunei
│       │       │   ├── Calcutta
│       │       │   ├── Chita
│       │       │   ├── Choibalsan
│       │       │   ├── Chongqing
│       │       │   ├── Chungking
│       │       │   ├── Colombo
│       │       │   ├── Dacca
│       │       │   ├── Damascus
│       │       │   ├── Dhaka
│       │       │   ├── Dili
│       │       │   ├── Dubai
│       │       │   ├── Dushanbe
│       │       │   ├── Famagusta
│       │       │   ├── Gaza
│       │       │   ├── Harbin
│       │       │   ├── Hebron
│       │       │   ├── Ho_Chi_Minh
│       │       │   ├── Hong_Kong
│       │       │   ├── Hovd
│       │       │   ├── Irkutsk
│       │       │   ├── Istanbul
│       │       │   ├── Jakarta
│       │       │   ├── Jayapura
│       │       │   ├── Jerusalem
│       │       │   ├── Kabul
│       │       │   ├── Kamchatka
│       │       │   ├── Karachi
│       │       │   ├── Kashgar
│       │       │   ├── Kathmandu
│       │       │   ├── Katmandu
│       │       │   ├── Khandyga
│       │       │   ├── Kolkata
│       │       │   ├── Krasnoyarsk
│       │       │   ├── Kuala_Lumpur
│       │       │   ├── Kuching
│       │       │   ├── Kuwait
│       │       │   ├── Macao
│       │       │   ├── Macau
│       │       │   ├── Magadan
│       │       │   ├── Makassar
│       │       │   ├── Manila
│       │       │   ├── Muscat
│       │       │   ├── Nicosia
│       │       │   ├── Novokuznetsk
│       │       │   ├── Novosibirsk
│       │       │   ├── Omsk
│       │       │   ├── Oral
│       │       │   ├── Phnom_Penh
│       │       │   ├── Pontianak
│       │       │   ├── Pyongyang
│       │       │   ├── Qatar
│       │       │   ├── Qostanay
│       │       │   ├── Qyzylorda
│       │       │   ├── Rangoon
│       │       │   ├── Riyadh
│       │       │   ├── Saigon
│       │       │   ├── Sakhalin
│       │       │   ├── Samarkand
│       │       │   ├── Seoul
│       │       │   ├── Shanghai
│       │       │   ├── Singapore
│       │       │   ├── Srednekolymsk
│       │       │   ├── Taipei
│       │       │   ├── Tashkent
│       │       │   ├── Tbilisi
│       │       │   ├── Tehran
│       │       │   ├── Tel_Aviv
│       │       │   ├── Thimbu
│       │       │   ├── Thimphu
│       │       │   ├── Tokyo
│       │       │   ├── Tomsk
│       │       │   ├── Ujung_Pandang
│       │       │   ├── Ulaanbaatar
│       │       │   ├── Ulan_Bator
│       │       │   ├── Urumqi
│       │       │   ├── Ust-Nera
│       │       │   ├── Vientiane
│       │       │   ├── Vladivostok
│       │       │   ├── Yakutsk
│       │       │   ├── Yangon
│       │       │   ├── Yekaterinburg
│       │       │   └── Yerevan
│       │       ├── Atlantic
│       │       │   ├── Azores
│       │       │   ├── Bermuda
│       │       │   ├── Canary
│       │       │   ├── Cape_Verde
│       │       │   ├── Faeroe
│       │       │   ├── Faroe
│       │       │   ├── Jan_Mayen
│       │       │   ├── Madeira
│       │       │   ├── Reykjavik
│       │       │   ├── South_Georgia
│       │       │   ├── St_Helena
│       │       │   └── Stanley
│       │       ├── Australia
│       │       │   ├── ACT
│       │       │   ├── Adelaide
│       │       │   ├── Brisbane
│       │       │   ├── Broken_Hill
│       │       │   ├── Canberra
│       │       │   ├── Currie
│       │       │   ├── Darwin
│       │       │   ├── Eucla
│       │       │   ├── Hobart
│       │       │   ├── LHI
│       │       │   ├── Lindeman
│       │       │   ├── Lord_Howe
│       │       │   ├── Melbourne
│       │       │   ├── North
│       │       │   ├── NSW
│       │       │   ├── Perth
│       │       │   ├── Queensland
│       │       │   ├── South
│       │       │   ├── Sydney
│       │       │   ├── Tasmania
│       │       │   ├── Victoria
│       │       │   ├── West
│       │       │   └── Yancowinna
│       │       ├── Brazil
│       │       │   ├── Acre
│       │       │   ├── DeNoronha
│       │       │   ├── East
│       │       │   └── West
│       │       ├── Canada
│       │       │   ├── Atlantic
│       │       │   ├── Central
│       │       │   ├── Eastern
│       │       │   ├── Mountain
│       │       │   ├── Newfoundland
│       │       │   ├── Pacific
│       │       │   ├── Saskatchewan
│       │       │   └── Yukon
│       │       ├── Chile
│       │       │   ├── Continental
│       │       │   └── EasterIsland
│       │       ├── Etc
│       │       │   ├── GMT
│       │       │   ├── GMT+0
│       │       │   ├── GMT+1
│       │       │   ├── GMT+10
│       │       │   ├── GMT+11
│       │       │   ├── GMT+12
│       │       │   ├── GMT+2
│       │       │   ├── GMT+3
│       │       │   ├── GMT+4
│       │       │   ├── GMT+5
│       │       │   ├── GMT+6
│       │       │   ├── GMT+7
│       │       │   ├── GMT+8
│       │       │   ├── GMT+9
│       │       │   ├── GMT-0
│       │       │   ├── GMT-1
│       │       │   ├── GMT-10
│       │       │   ├── GMT-11
│       │       │   ├── GMT-12
│       │       │   ├── GMT-13
│       │       │   ├── GMT-14
│       │       │   ├── GMT-2
│       │       │   ├── GMT-3
│       │       │   ├── GMT-4
│       │       │   ├── GMT-5
│       │       │   ├── GMT-6
│       │       │   ├── GMT-7
│       │       │   ├── GMT-8
│       │       │   ├── GMT-9
│       │       │   ├── GMT0
│       │       │   ├── Greenwich
│       │       │   ├── UCT
│       │       │   ├── Universal
│       │       │   ├── UTC
│       │       │   └── Zulu
│       │       ├── Europe
│       │       │   ├── Amsterdam
│       │       │   ├── Andorra
│       │       │   ├── Astrakhan
│       │       │   ├── Athens
│       │       │   ├── Belfast
│       │       │   ├── Belgrade
│       │       │   ├── Berlin
│       │       │   ├── Bratislava
│       │       │   ├── Brussels
│       │       │   ├── Bucharest
│       │       │   ├── Budapest
│       │       │   ├── Busingen
│       │       │   ├── Chisinau
│       │       │   ├── Copenhagen
│       │       │   ├── Dublin
│       │       │   ├── Gibraltar
│       │       │   ├── Guernsey
│       │       │   ├── Helsinki
│       │       │   ├── Isle_of_Man
│       │       │   ├── Istanbul
│       │       │   ├── Jersey
│       │       │   ├── Kaliningrad
│       │       │   ├── Kiev
│       │       │   ├── Kirov
│       │       │   ├── Kyiv
│       │       │   ├── Lisbon
│       │       │   ├── Ljubljana
│       │       │   ├── London
│       │       │   ├── Luxembourg
│       │       │   ├── Madrid
│       │       │   ├── Malta
│       │       │   ├── Mariehamn
│       │       │   ├── Minsk
│       │       │   ├── Monaco
│       │       │   ├── Moscow
│       │       │   ├── Nicosia
│       │       │   ├── Oslo
│       │       │   ├── Paris
│       │       │   ├── Podgorica
│       │       │   ├── Prague
│       │       │   ├── Riga
│       │       │   ├── Rome
│       │       │   ├── Samara
│       │       │   ├── San_Marino
│       │       │   ├── Sarajevo
│       │       │   ├── Saratov
│       │       │   ├── Simferopol
│       │       │   ├── Skopje
│       │       │   ├── Sofia
│       │       │   ├── Stockholm
│       │       │   ├── Tallinn
│       │       │   ├── Tirane
│       │       │   ├── Tiraspol
│       │       │   ├── Ulyanovsk
│       │       │   ├── Uzhgorod
│       │       │   ├── Vaduz
│       │       │   ├── Vatican
│       │       │   ├── Vienna
│       │       │   ├── Vilnius
│       │       │   ├── Volgograd
│       │       │   ├── Warsaw
│       │       │   ├── Zagreb
│       │       │   ├── Zaporozhye
│       │       │   └── Zurich
│       │       ├── Indian
│       │       │   ├── Antananarivo
│       │       │   ├── Chagos
│       │       │   ├── Christmas
│       │       │   ├── Cocos
│       │       │   ├── Comoro
│       │       │   ├── Kerguelen
│       │       │   ├── Mahe
│       │       │   ├── Maldives
│       │       │   ├── Mauritius
│       │       │   ├── Mayotte
│       │       │   └── Reunion
│       │       ├── Mexico
│       │       │   ├── BajaNorte
│       │       │   ├── BajaSur
│       │       │   └── General
│       │       ├── Pacific
│       │       │   ├── Apia
│       │       │   ├── Auckland
│       │       │   ├── Bougainville
│       │       │   ├── Chatham
│       │       │   ├── Chuuk
│       │       │   ├── Easter
│       │       │   ├── Efate
│       │       │   ├── Enderbury
│       │       │   ├── Fakaofo
│       │       │   ├── Fiji
│       │       │   ├── Funafuti
│       │       │   ├── Galapagos
│       │       │   ├── Gambier
│       │       │   ├── Guadalcanal
│       │       │   ├── Guam
│       │       │   ├── Honolulu
│       │       │   ├── Johnston
│       │       │   ├── Kanton
│       │       │   ├── Kiritimati
│       │       │   ├── Kosrae
│       │       │   ├── Kwajalein
│       │       │   ├── Majuro
│       │       │   ├── Marquesas
│       │       │   ├── Midway
│       │       │   ├── Nauru
│       │       │   ├── Niue
│       │       │   ├── Norfolk
│       │       │   ├── Noumea
│       │       │   ├── Pago_Pago
│       │       │   ├── Palau
│       │       │   ├── Pitcairn
│       │       │   ├── Pohnpei
│       │       │   ├── Ponape
│       │       │   ├── Port_Moresby
│       │       │   ├── Rarotonga
│       │       │   ├── Saipan
│       │       │   ├── Samoa
│       │       │   ├── Tahiti
│       │       │   ├── Tarawa
│       │       │   ├── Tongatapu
│       │       │   ├── Truk
│       │       │   ├── Wake
│       │       │   ├── Wallis
│       │       │   └── Yap
│       │       ├── US
│       │       │   ├── Alaska
│       │       │   ├── Aleutian
│       │       │   ├── Arizona
│       │       │   ├── Central
│       │       │   ├── East-Indiana
│       │       │   ├── Eastern
│       │       │   ├── Hawaii
│       │       │   ├── Indiana-Starke
│       │       │   ├── Michigan
│       │       │   ├── Mountain
│       │       │   ├── Pacific
│       │       │   └── Samoa
│       │       ├── CET
│       │       ├── CST6CDT
│       │       ├── Cuba
│       │       ├── EET
│       │       ├── Egypt
│       │       ├── Eire
│       │       ├── EST
│       │       ├── EST5EDT
│       │       ├── Factory
│       │       ├── GB
│       │       ├── GB-Eire
│       │       ├── GMT
│       │       ├── GMT+0
│       │       ├── GMT-0
│       │       ├── GMT0
│       │       ├── Greenwich
│       │       ├── Hongkong
│       │       ├── HST
│       │       ├── Iceland
│       │       ├── Iran
│       │       ├── iso3166.tab
│       │       ├── Israel
│       │       ├── Jamaica
│       │       ├── Japan
│       │       ├── Kwajalein
│       │       ├── leapseconds
│       │       ├── Libya
│       │       ├── MET
│       │       ├── MST
│       │       ├── MST7MDT
│       │       ├── Navajo
│       │       ├── NZ
│       │       ├── NZ-CHAT
│       │       ├── Poland
│       │       ├── Portugal
│       │       ├── PRC
│       │       ├── PST8PDT
│       │       ├── ROC
│       │       ├── ROK
│       │       ├── Singapore
│       │       ├── Turkey
│       │       ├── tzdata.zi
│       │       ├── UCT
│       │       ├── Universal
│       │       ├── UTC
│       │       ├── W-SU
│       │       ├── WET
│       │       ├── zone.tab
│       │       ├── zone1970.tab
│       │       ├── zonenow.tab
│       │       └── Zulu
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
├── logs
├── mapping
│   ├── category_mapping.yaml
│   └── update_status.json
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
│   │   ├── text_sanitize.py
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
├── ts.py
└── witcher mod manager.png