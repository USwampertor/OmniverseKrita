# Imported objects
from krita import (DockWidget, 
                   DockWidgetFactory, 
                   DockWidgetFactoryBase)
from PyQt5.QtCore import (Qt, QObject, 
                          QEvent, QThread, 
                          pyqtSignal)
from PyQt5.QtGui import (QImage)
from PyQt5.QtWidgets import (QWidget, QPushButton, 
                             QCheckBox, QStyle,
                             QDialog, QLineEdit, 
                             QDialogButtonBox,
                             QLabel, QHBoxLayout, 
                             QVBoxLayout, QMessageBox, 
                             QListWidgetItem,
                             QListWidget)

# Imported objects
import ctypes
import os
import sys
import time
import json

# Title
DOCKER_TITLE = 'Omniverse Docker'

# For experimental features activate this value
EXPERIMENTAL_FEATURES = True

# global variable declaration
if (sys.platform == "win32"):
  if EXPERIMENTAL_FEATURES:
    libname = "\windll\Debug\ovCLibraryd.dll"
  else:
    libname = "\windll\Release\ovCLibrary.dll"
else:
  if EXPERIMENTAL_FEATURES:
    libname = "/dll/Debug/ovCLibraryd.so"
  else:
    libname = "/dll/Release/ovCLibrary.so"

# This is a C to Python managed file from the omniverse
# file system
class OmniFolderEntry(ctypes.Structure):
  """
  This is a C to Python managed file from the omniverse

  The object lets us gather the information from the 
  Omniverse C DLL.
  A OmniFolderEntry is equivalent to a folder or file  
  """
  _fields_=[("relativePath", ctypes.c_char_p),
            ("access", ctypes.c_uint32),
            ("flags", ctypes.c_uint32),
            ("size", ctypes.c_uint64),
            ("modifiedTimeNs", ctypes.c_uint64),
            ("createdTimeNs", ctypes.c_uint64),
            ("modifiedBy", ctypes.c_char_p),
            ("createdBy", ctypes.c_char_p),
            ("version", ctypes.c_char_p),
            ("hash", ctypes.c_char_p),
            ("comment", ctypes.c_char_p),]
  
  """
  The content of the OmniFolder Entry is composed by

  :param relativePath: the path relative to the current folder of the entry

  :param access:

  :param flags:

  :param size:

  :param modifiedTimeNs:

  :param createdTimeNs:

  :param modifiedBy:

  :param createdBy:

  :param version:

  :param hash:

  :param comment:
  """
##########

class FolderFinderWorker(QObject):
  """
  A QObject in charge of connecting to
  new ips without it being blocking
  """
  finished = pyqtSignal()
  """FolderFinderWorker pyqtSignal when the task has finished"""

  progress = pyqtSignal()
  """FolderFinderWorker pyqtSignal when the task has finished a step in the loop"""
  
  newConnection = ""

  omniDocker = None

  def run(self):
    """
    Attempts to connect to the new IP in a  non-blocking way
    """
    
    self.connectingMsg = QMessageBox()
    self.connectingMsg.setWindowTitle("Wait a moment")
    self.connectingMsg.setText("Attempting to connect to %s" %(self.newConnection))
    self.connectingMsg.setWindowModality(Qt.NonModal)
    self.connectingMsg.show()

    omniDocker.refreshOmniverseFolder()
    self.finished.emit()
##########

# Class declaration
class LiveSyncWorker(QObject):
  """
  A QObject in charge of thread-saving files
  The time between each saving point can be set in the
  settings popup, but by default is set to 1 second 
  """
  finished = pyqtSignal()
  """LiveSyncWorker pyqtSignal when the task has finished"""

  progress = pyqtSignal()
  """LiveSyncWorker pyqtSignal when the task has finished a step in the loop"""
  
  isActive = False
  """LiveSyncWorker way to check if we are live sync saving or not"""

  def run(self):
    """
    run works as a loop that continues as long as the live sync checkbox is active
    :param self: the same worker
    """
    i = 0
    # We continue checking if we are still in live sync mode
    while self.isActive:
      time.sleep(1)
      self.progress.emit()
      i+=1
    self.finished.emit()
##########

# Class declaration
class DockerOmniverse(DockWidget):
  """
  A DockWidget for the Omniverse connector

  This docker lets you connect to the omniverse platform, save, load, and live sync
  textures, images, and files accepted by Krita for a faster game development pipeline 
  """

  # constructor
  def __init__(self):
    # base constructor
    """
    Constructor
    """
    super().__init__()

    self.buildUI()

    self.connectButton.setEnabled(False)
    self.setElements()

    self.reloadButton.clicked.connect(self.reloadWidget)
    self.loadDLL()

  ##########

  
  def buildUI(self):
    """ 
    Creates the main UI and all its content.
    Also connects and sets buttons to work as intended
    """

    # Main window
    self.mainWidget = QWidget()
    self.mainWidget.setLayout(QVBoxLayout())
    self.setWidget(self.mainWidget)
    
    # Declaring UI structure
    self.loadDLLButton = QPushButton("Load Omniverse", self.mainWidget)
    self.mainWidget.layout().addWidget(self.loadDLLButton)
    self.loadDLLButton.clicked.connect(self.loadDLL)
    self.isLoaded = False

    self.connectButton = QPushButton("Connect To Omniverse", self.mainWidget)
    self.mainWidget.layout().addWidget(self.connectButton)
    self.connectButton.clicked.connect(self.connectToOmniverse)
    self.isConnected = False
    
    self.omniFileInput = QLineEdit("", self.mainWidget)
    self.mainWidget.layout().addWidget(self.omniFileInput)
    self.omniFileInput.setPlaceholderText("Write the URL to save/load")
    
    self.basePathTextEdit = QLineEdit("", self.mainWidget)
    self.mainWidget.layout().addWidget(self.basePathTextEdit)
    self.basePathTextEdit.setPlaceholderText("")
    
    self.openButton = QPushButton("Open...", self.mainWidget)
    self.mainWidget.layout().addWidget(self.openButton)
    self.openButton.clicked.connect(self.openFileDialog)

    self.saveButton = QPushButton("Save", self.mainWidget)
    self.mainWidget.layout().addWidget(self.saveButton)
    self.saveButton.clicked.connect(self.saveFile)

    self.hLayout = QHBoxLayout()
    self.mainWidget.layout().addLayout(self.hLayout)

    self.liveSyncCheckbox = QCheckBox("Live Sync", self.mainWidget)
    self.hLayout.layout().addWidget(self.liveSyncCheckbox)
    self.liveSyncCheckbox.stateChanged.connect(self.setLiveSync)
    self.isLiveSyncing = False

    self.omniverseStatusLabel = QLabel(("Omniverse loaded" if self.isLoaded else "Omniverse not loaded"), self.mainWidget)
    self.mainWidget.layout().addWidget(self.omniverseStatusLabel)

    self.userLabel = QLabel("", self.mainWidget)
    self.mainWidget.layout().addWidget(self.userLabel)

    self.testLabel = QLabel("...", self.mainWidget)
    self.mainWidget.layout().addWidget(self.testLabel)


    self.debugList = QListWidget(self.mainWidget)
    self.mainWidget.layout().addWidget(self.debugList)

    self.settingsButton = QPushButton("Settings...", self.mainWidget)
    self.mainWidget.layout().addWidget(self.settingsButton)
    self.settingsButton.clicked.connect(self.openSettingsDialog)

    self.reloadButton = QPushButton("Reload Plugin", self.mainWidget)
    self.mainWidget.layout().addWidget(self.reloadButton)
    self.reloadButton.clicked.connect(self.reloadWidget)

    self.setWindowTitle(DOCKER_TITLE)

    # Finishing up stuff
    self.debugLog("Finished loading everything...")
  ##########

  # Sets the elements that allow you to connect to
  # omniverse to be interactable or not
  def setElements(self):
    """
    There are several ui items that should be only active
    when you have connected to Omniverse

    This sets them active or inactive based on the connection
    """

    setActive = self.isConnected
    self.omniFileInput.setEnabled(setActive)
    self.basePathTextEdit.setEnabled(setActive)
    self.openButton.setEnabled(setActive)
    self.saveButton.setEnabled(setActive)
    self.liveSyncCheckbox.setEnabled(setActive)
  ##########

  # Reloads the widget
  # TODO: Do this as a functional system
  def reloadWidget(self):
    """
    Attempts to reload the widget for quick debugging
    """
    self.debugLog("Reloading widget...")
    try:
      self.debugLog("Trying to reload widget")
      if (sys.platform == "win32"):
        sys.path.append(os.path.realpath(os.getenv('APPDATA') + "\\krita\\pykrita\\docker_omniverse"))
      else:
        sys.path.append("~/.local/share/krita/pykrita/docker_omniverse")
      if 'docker_omniverse' in sys.modules:
        self.debugLog("Widget was already in the modules, trying to reload")
        from importlib import reload
        # Reloading plugin
        reload(sys.modules['docker_omniverse'])
    except:
      self.debugLog("Error trying to reload")
      # Windows %APPDATA%\krita\pykrita\docker_omniverse
      # Linux ~/.local/share/krita/pykrita/docker_omniverse
      # Apple ~/Library/Application Support/Krita/pykrita/docker_omniverse
  ##########

  # This is to debug information if needed
  def debugLog(self, msg):
    """
    Adds a new item to the logging viewport
    """
    newItem = QListWidgetItem(msg, self.debugList)
    self.debugList.insertItem(self.debugList.count() + 1, newItem)
  ##########

  # This is to clear debug information if needed
  def clearLog(self):
    """
    Clears the log
    """
    self.debugList.clear()
  ##########

  # Loads the custom Omniverse DLL
  def loadDLL(self):
    """
    Attempts to load the Omniverse C DLL for file handling and live syncing with
    Omniverse
    """
    self.debugLog("Loading DLL...")
    if not self.isLoaded:
      try:
        # change this for os.path.dirname(os.path.abspath(__file__))
        location = (os.path.dirname(os.path.abspath(__file__)) + libname)        
        self.debugLog(location)
        # get the lib location
        self.lib = ctypes.CDLL(location)
        self.defaultDestinationPath = "omniverse://localhost/Projects/Krita/"
        
        self.isLoaded = not self.isLoaded
        
        # setting ctype objects from the library
        self.lib.cPing.restype = ctypes.c_int
        self.lib.cInitialize.restype = ctypes.c_bool
        self.lib.cInitialize.argtypes = [ctypes.c_bool, ctypes.c_int]
        self.lib.cGetUsername.restype = ctypes.c_char_p
        self.lib.cGetUsername.argtypes = [ctypes.c_char_p]
        self.lib.cGetLogString.restype = ctypes.c_char_p
        self.lib.cCreateStage.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.cCreateStage.restype = ctypes.c_char_p
        self.lib.cDeleteStage.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.cDeleteStage.restype = ctypes.c_int
        self.lib.cTransferFile.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.cGetGlobalError.restype = ctypes.c_char_p
        self.lib.cIsValidURL.argtypes = [ctypes.c_char_p]
        self.lib.cIsValidURL.restype = ctypes.c_bool
        self.lib.cURLObjectExists.argtypes = [ctypes.c_char_p]
        self.lib.cURLObjectExists.restype = ctypes.c_bool
        self.lib.cGetLocalFile.argtypes = [ctypes.c_char_p]
        self.lib.cGetLocalFile.restype = ctypes.c_char_p
        self.lib.cDeleteFile.argtypes = [ctypes.c_char_p]
        self.lib.cFetchFolderEntries.argtypes = [ctypes.c_char_p]
        self.lib.cFetchFileEntry.argtypes = [ctypes.c_int]
        self.lib.cFetchFileEntry.restype = ctypes.POINTER(OmniFolderEntry)
        self.lib.cGetFolderCount.restype = ctypes.c_int
        self.lib.cIsEntryFolder.restype = ctypes.c_bool
        self.lib.cIsEntryFolder.argtypes = [ctypes.c_int]
        self.lib.cForceConnect.argtypes = [ctypes.c_char_p]
        
        self.omniverseStatusLabel.setText("Omniverse loaded" 
                                          if self.isLoaded 
                                          else "Omniverse not loaded")
        self.loadDLLButton.setEnabled(False)
        self.connectButton.setEnabled(True)
        self.debugLog("Finished loading DLL...")

      # Handling error with the DLL either finding it or not being able to load it
      except OSError as e:
        self.debugLog("Error loading DLL...")
        self.debugLog("Error at %s" %(e))
        self.omniverseStatusLabel.setText("Error at %s" %(e))
    self.lib.cForceConnect(str.encode("omniverse://localhost/"))
    return self.isLoaded
  ##########

  # Loads the connections from the saved file
  def loadConnections(self):
    self.debugLog("Loading connections")
    fileName = (os.path.dirname(os.path.abspath(__file__)) + 
                ("\\" if sys.platform == "win32" else "/") + 
                "connections.json")
    f = open(fileName)
    self.debugLog("Loaded file with connections")
    self.connectionsJSON = json.load(f)
    if self.connectionsJSON is None:
      self.debugLog("Error getting connections")
    for i in self.connectionsJSON["connections"]:
      self.debugLog(i)
    self.debugLog("Loaded connections")
  ##########

  # Connects to the Omniverse platform
  # TODO: Handle errors better
  def connectToOmniverse(self):
    """
    Will attempt to connect to the omniverse platform
    
    Version 1.0 *NEEDS* you to have nucleus active and logged in

    TODO: There are few cases that still need to be handled correctly
    such as retrying the connection
    """
    self.debugLog("Trying to connect to omniverse")
    if not self.isConnected and self.isLoaded:
      self.debugLog("Connectiong")
      self.connectButton.setText("Connecting...")
      if self.lib.cInitialize(True, 0):
        self.debugLog("Omniverse initialized correctly")
        self.connectButton.setText("Disconnect")
        self.isConnected = True
        username = self.lib.cGetUsername(str.encode(self.defaultDestinationPath)).decode()
        self.userLabel.setText(username)
        self.basePathTextEdit.setPlaceholderText(self.defaultDestinationPath)
      else:
        self.userLabel.setText("undefined")
        self.debugLog("There was an error initializing omniverse: ")
        self.debugLog("Error %s " %(self.lib.cGetGlobalError().decode()))
    else:
      self.debugLog("Shutting down omniverse... ")
      self.connectButton.setText("Shutting down...")
      self.connectButton.setText("Connect to Omniverse")
      self.isConnected = False
      fileName = (os.path.dirname(os.path.abspath(__file__)) + 
                  ("\\" if sys.platform == "win32" else "/") + 
                  "connections.json")
      f = open(fileName, "w")
      f.write(json.dumps(self.connectionsJSON))
      f.close()
    self.setElements()
    self.loadConnections()
  ##########

  # Checks if the object still exists and opens it.
  def openOmniverseFile(self):
    """
    Tries to check first if the file exists, and if so, opens it for editing
    in the Krita application
    """
    fullPath = self.currentOmniFolder + self.currentOmniFile
    if (self.currentOmniFile == "" or 
        not self.lib.cURLObjectExists(str.encode(fullPath))):
      
      msgBox = QMessageBox()
      msgBox.setText("The file name is invalid/not selected")
      msgBox.exec()
      return False

    localPath = self.lib.cGetLocalFile(str.encode(fullPath)).decode()
    newFile = Krita.instance().openDocument(localPath)
    Krita.instance().activeWindow().addView(newFile)
    self.basePathTextEdit.setText(self.currentOmniFolder)
    self.omniFileInput.setText(os.path.splitext(self.currentOmniFile)[0])
    self.dlg.accept()
    return True
  ##########

  # Depending on the type of file, if it is new or where it is saved
  # Handles the way to save it, saves it and uploads it to omniverse or
  # updates it if needed
  def saveFile(self):
    """
    Depending on the type of file, if it is new or where it is saved
    Handles the way to save it, saves it and uploads it to omniverse or
    updates it if needed
    """
    currentDocument = Krita.instance().activeDocument()
    currentDocument.setBatchmode(True)
    
    pixelBytes = currentDocument.activeNode().pixelData(0, 
                                                        0, 
                                                        currentDocument.width(), 
                                                        currentDocument.height())
    imageData = QImage(pixelBytes, 
                       currentDocument.width(), 
                       currentDocument.height(), 
                       QImage.Format_RGBA8888).rgbSwapped()
    
    # imageData.save(localTemp)

    self.basePathTextEdit.setText(self.basePathTextEdit.text() 
                                  if self.basePathTextEdit.text() != "" 
                                  else self.defaultDestinationPath)
    fullPath = self.basePathTextEdit.text()

    # This means our file exists
    if(currentDocument.fileName() != ""):
      # Save the file locally
      imageData.save(currentDocument.fileName())
      # currentDocument.saveAs(currentDocument.fileName())

      self.omniFileInput.setText(self.omniFileInput.text() 
                                 if self.omniFileInput.text() != "" 
                                 else currentDocument.name())
      
      fullPath = fullPath + self.omniFileInput.text() + ".png"
      # First check if file is part of the cache folder
      defaultOVCachéPath = (os.getenv('LOCALAPPDATA') + 
                            ("\\" if (sys.platform == "win32") else "/") + 
                            "ov")
      
      # Case 1. The file is part of the caché. We should update the file IF the
      # omniverse path is still the same we used to open it
      if defaultOVCachéPath in currentDocument.fileName():
        
        # imageData.save(currentDocument.fileName())
        # currentDocument.saveAs(currentDocument.fileName())
        
        # self.lib.cDeleteFile(str.encode(fullPath))
        self.lib.cTransferFile(str.encode(currentDocument.fileName()), 
                               str.encode(fullPath))
        #Case 1.1 Check if the omniverse path is still the same 
        if ((self.basePathTextEdit.text() != self.currentOmniFolder) or 
            (self.omniFileInput.text() != os.path.splitext(self.currentOmniFile)[0])):
          #if not we should get the new cached version
          localPath = self.lib.cGetLocalFile(str.encode(fullPath)).decode()
          currentDocument.close()

          newFile = Krita.instance().openDocument(localPath)
          Krita.instance().activeWindow().addView(newFile)
          self.currentOmniFolder = self.basePathTextEdit.text()
          self.currentOmniFile = self.omniFileInput.text() + ".png"
      # Case 2. The file is not part of the caché
      else:
        # We should upload the object and start using the cachéd version
        # imageData.save(currentDocument.fileName())
        # currentDocument.saveAs(currentDocument.fileName())

        # self.lib.cDeleteFile(str.encode(fullPath))
        self.lib.cTransferFile(str.encode(currentDocument.fileName()), 
                               str.encode(fullPath))
        
        localPath = self.lib.cGetLocalFile(str.encode(fullPath)).decode()
        currentDocument.close()

        newFile = Krita.instance().openDocument(localPath)
        Krita.instance().activeWindow().addView(newFile)
        self.currentOmniFolder = self.basePathTextEdit.text()
        self.currentOmniFile = self.omniFileInput.text() + ".png"
    # This is a new file and should be saved first locally, even temporarily
    else:  
      #We should check if the defaultName doesn't magically override an existing file
      self.omniFileInput.setText(self.omniFileInput.text() 
                                 if self.omniFileInput.text() != "" 
                                 else "newFile")

      tempFile = fullPath + self.omniFileInput.text()
      if self.lib.cURLObjectExists(str.encode(tempFile + ".png")):
        i = 1
        while self.lib.cURLObjectExists(str.encode(tempFile + "_" + str(i) + ".png")):
          i = i + 1
        fullPath = tempFile + "_" + str(i) + ".png"
      else:
        fullPath = tempFile + ".png"
      localTemp = os.path.expanduser("~/Desktop/tmpOVFile.png")

      imageData.save(localTemp)
      currentDocument.saveAs(localTemp)
      currentDocument.close()

      # self.lib.cDeleteFile(str.encode(fullPath))
      self.lib.cTransferFile(str.encode(localTemp), str.encode(fullPath))

      localPath = self.lib.cGetLocalFile(str.encode(fullPath)).decode()

      newFile = Krita.instance().openDocument(localPath)
      Krita.instance().activeWindow().addView(newFile)
      self.currentOmniFolder = self.basePathTextEdit.text()
      self.currentOmniFile = self.omniFileInput.text() + ".png"
      
      os.remove(localTemp)
      os.remove(localTemp + "~")
  ##########

  # Live syncs the file
  def setLiveSync(self):
    """
    Sets the saving system to live sync.
    This means that for ever n second set in the docker settings (1 second default)
    The docker will try to save the file and update the information in the cloud
    This way you can edit real time textures and see them in applications
    such as Create or Maya or UE4
    """
    if self.liveSyncCheckbox.isChecked() and not self.isLiveSyncing:
      self.isLiveSyncing = True
      self.thread = QThread()
      self.worker = LiveSyncWorker()
      self.worker.isActive = self.isLiveSyncing
      self.worker.moveToThread(self.thread)
      self.thread.started.connect(self.worker.run)
      self.worker.finished.connect(self.thread.quit)
      self.worker.finished.connect(self.worker.deleteLater)
      self.thread.finished.connect(self.thread.deleteLater)
      self.worker.progress.connect(self.reportProgress)
      self.thread.finished.connect(
        lambda: self.testLabel.setText("Live sync not active")
      )
      self.thread.start()
    elif not self.liveSyncCheckbox.isChecked() and self.isLiveSyncing:
      self.isLiveSyncing = False
      self.worker.isActive = self.isLiveSyncing
      # self.thread.quit()
  ##########

  def reportProgress(self):
    """
    The function that runs when the signal of progress is sent by the live sync worker.

    Right now the only thing that does is set the last time the syystem saved progress
    """
    self.testLabel.setText(f"Last saved at:" + time.strftime("%Y/%m/%d %H:%M:%S"))
    self.saveFile()
  ##########

  # Clears the list of files and takes the current omniverse folder and lists all items
  def refreshOmniverseFolder(self):
    self.debugLog("Trying to reload connection %s" %(self.currentOmniFolder))
    self.dlg.dlgPath1.setText(self.currentOmniFolder)
    self.lib.cFetchFolderEntries(str.encode(self.currentOmniFolder))

    self.dlg.fileList.setCurrentItem(None)
    self.dlg.fileList.clear()
    
    # This is to check if we are in the root of the connection or not
    if self.currentOmniFolder.count('/') > 3:
      rootItem = QListWidgetItem("...", self.dlg.fileList)
      rootItem.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
      self.dlg.fileList.insertItem(0, rootItem)
    
    count = self.lib.cGetFolderCount()
    
    # Add an item per fetched object
    for i in range(count):
      newItem = QListWidgetItem(self.lib.cFetchFileEntry(i).contents.relativePath.decode(), self.dlg.fileList)
    
      # krita icons
      icon = Krita.instance().icon('folder' if self.lib.cIsEntryFolder(i) else 'folder-pictures')
      newItem.setIcon(icon)
      self.dlg.fileList.insertItem(i + 1, newItem)
    return True
  ##########

  # Opens the dialog popup to select a file, connection or add a connection to
  # the list of files
  def openFileDialog(self):
    self.dlg = QDialog()
    self.dlg.setWindowTitle("Choose File")
    self.dlg.setWindowModality(Qt.ApplicationModal)

    vLayout = QVBoxLayout()
    self.dlg.setLayout(vLayout)
    
    self.currentOmniFolder = "omniverse://localhost/Projects/"
    self.currentOmniFile = ""

    hLayout1 = QHBoxLayout()
    vLayout.addLayout(hLayout1)

    self.dlg.dlgPath1 = QLineEdit(self.currentOmniFolder, self.dlg)
    self.dlg.dlgPath1.setPlaceholderText("")

    hLayout1.addWidget(self.dlg.dlgPath1)

    hLayout2 = QHBoxLayout()
    vLayout.addLayout(hLayout2)

    self.dlg.connections = QListWidget()
    self.dlg.connections.setMaximumWidth(self.frameGeometry().width() / 3)
    self.dlg.fileList = QListWidget()

    hLayout2.addWidget(self.dlg.connections)
    hLayout2.addWidget(self.dlg.fileList)

    defaultConnection = QListWidgetItem("localhost", self.dlg.connections)
    defaultConnection.setIcon(Krita.instance().icon('drive-harddisk'))

    for jsonConnection in self.connectionsJSON["connections"]:
      newConnection = QListWidgetItem(jsonConnection, self.dlg.connections)
      newConnection.setIcon(Krita.instance().icon('drive-harddisk'))

    addConnection = QListWidgetItem("Add...", self.dlg.connections)
    addConnection.setIcon(Krita.instance().icon('addlayer'))
    
    # self.dlg.fileList.insertItem(0, defaultConnection)
    # self.dlg.fileList.insertItem(1, addConnection)

    hLayout3 = QHBoxLayout()
    vLayout.addLayout(hLayout3)

    self.dlg.dlgPath2 = QLineEdit(self.currentOmniFile, self.dlg)
    loadButton = QPushButton("Load File", self.dlg)
    
    loadButton.clicked.connect(self.openOmniverseFile)

    hLayout3.addWidget(self.dlg.dlgPath2)
    hLayout3.addWidget(loadButton)

    self.dlg.fileList.itemDoubleClicked.connect(self.onDoubleClickedItem)
    self.dlg.fileList.itemClicked.connect(self.onClickedItem)
    self.dlg.connections.itemClicked.connect(self.onClickedConnection)

    self.dlg.installEventFilter(self)

    self.refreshOmniverseFolder()
    return self.dlg.exec_() == QDialog.Accepted
  ##########

  # When you click an item from the connection list
  def onClickedConnection(self, item):
    """
    A function that triggers when you click an item from the connections
    list
    """
    if item.text() == "Add...":
      self.debugLog("Adding a new connection...")
      connectionDialog = QDialog(self)
      connectionDialog.setWindowTitle("Add connection...")
      connectionDialog.setWindowModality(Qt.ApplicationModal)
      connectionDialog.vLayout = QVBoxLayout()
      connectionDialog.setLayout(connectionDialog.vLayout)

      connectionDialog.connectionInput = QLineEdit("", connectionDialog)
      connectionDialog.connectionInput.setPlaceholderText("Add an ip...")
      
      QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
      connectionDialog.buttonBox = QDialogButtonBox(QBtn, connectionDialog)
      connectionDialog.buttonBox.accepted.connect(connectionDialog.accept)
      connectionDialog.buttonBox.rejected.connect(connectionDialog.reject)

      connectionDialog.vLayout.addWidget(connectionDialog.connectionInput)
      connectionDialog.vLayout.addWidget(connectionDialog.buttonBox)

      if connectionDialog.exec():
        newConnectionText = connectionDialog.connectionInput.text()
        if newConnectionText != "":
          self.debugLog("Trying to load connection %s" 
                        %(newConnectionText))

          self.lib.cForceConnect(str.encode("omniverse://" + 
                                            newConnectionText + 
                                            "/"))
          
          newConnection = QListWidgetItem(newConnectionText)
          newConnection.setIcon(Krita.instance().icon('drive-harddisk'))

          self.dlg.connections.insertItem(self.dlg.connections.count() - 1, 
                                          newConnection)
          if self.lib.cIsValidURL(str.encode("omniverse://" + newConnectionText + "/")):

            self.currentOmniFolder = "omniverse://" + newConnectionText + "/"
            self.currentConnection = newConnectionText
            self.connectionsJSON["connections"].append(newConnectionText)
            # old blocking version
            self.refreshOmniverseFolder()
           
    elif self.lib.cIsValidURL(str.encode("omniverse://" + item.text() + "/")):
      self.currentOmniFolder = "omniverse://" + item.text() + "/"
      self.currentConnection = item.text()
      self.refreshOmniverseFolder()
  ##########

  # When clicking an item from the file list
  def onClickedItem(self, item):
    """
    A function that triggers when you click an item from the folder
    list
    """
    if item.text() != "...":
      index = self.dlg.fileList.indexFromItem(item).row()
      if self.dlg.fileList.item(0).text() == "...":
        index =  index - 1
      self.currentOmniFile = (item.text() 
                              if not self.lib.cIsEntryFolder(index) 
                              else "")
      self.dlg.dlgPath2.setText(self.currentOmniFile)
    else:
      self.currentOmniFile = ""
      self.dlg.dlgPath2.setText(self.currentOmniFile)
  ##########

  # When double clicking an item from the file list
  def onDoubleClickedItem(self, item):
    """
    A function that triggers when you double click an item from the folder
    list
    """
    # self.testLabel = item.text()
    if item.text() == "...":
      self.currentOmniFolder = self.currentOmniFolder.rsplit("/", 2)[0]
      self.currentOmniFolder = (self.currentOmniFolder + "/")
      self.refreshOmniverseFolder()
    else:
      index = self.dlg.fileList.indexFromItem(item).row()
      if self.dlg.fileList.item(0).text() == "...":
        index =  index - 1
      if self.lib.cIsEntryFolder(index):
        self.currentOmniFolder = (self.currentOmniFolder + 
                                  item.text() + 
                                  "/")
        self.refreshOmniverseFolder()
      else:
        # This should handle getting the file
        self.currentOmniFile = item.text()
        self.dlg.dlgPath2.setText(self.currentOmniFile)
        self.openOmniverseFile()
  ##########

  # Event filter for the custom dialog file viewer
  def eventFilter(self, obj, event):
    """
    To handle clicks and Enter and Esc buttons in the file viewer dialog,
    this event filter is installed so it behaves like any file explorer
    """
    if obj is self.dlg:
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, 
                               Qt.Key_Enter,):
                if self.dlg.dlgPath1.hasFocus():
                  if self.lib.cURLObjectExists(str.encode(self.dlg.dlgPath1.text())):
                    self.currentOmniFolder = self.dlg.dlgPath1.text()
                    if not self.currentOmniFolder.endswith('/'):
                      self.currentOmniFolder = (self.currentOmniFolder + '/')
                    self.refreshOmniverseFolder()
                  else:
                    self.dlg.dlgPath1.setText(self.currentOmniFolder)
                    msgBox = QMessageBox()
                    msgBox.setText("The path in the search bar is invalid!")
                    msgBox.exec()
                return True
    return super(DockerOmniverse, self).eventFilter(obj, event)
  ##########

  # opens up the settings dialog
  def openSettingsDialog(self):
    """
    Opens this docker's settings
    """
    self.settingsDlg = QDialog()
    self.settingsDlg.setWindowTitle("Settings")
    self.settingsDlg.setWindowModality(Qt.ApplicationModal)

    vLayout = QVBoxLayout()
    self.settingsDlg.setLayout(vLayout)

    self.experimentalCheckbox = QCheckBox("Activate experimental features", self.mainWidget)
    vLayout.layout().addWidget(self.experimentalCheckbox)
    self.experimentalCheckbox.stateChanged.connect(self.setExperimental)

    self.debugEnabledCheckbox = QCheckBox("Enable debug logging", self.mainWidget)
    vLayout.layout().addWidget(self.debugEnabledCheckbox)
    self.debugEnabledCheckbox.setChecked(self.debugList.isVisible())
    self.debugEnabledCheckbox.stateChanged.connect(self.setDebugEnabled)

    return self.settingsDlg.exec_() == QDialog.Accepted
  ##########

  # sets the debug logger enabled or disabled
  def setDebugEnabled(self):
    """
    Makes the debug logger visible or not, depending on the active
    value of the checkbox
    """
    self.debugList.setVisible(self.debugEnabledCheckbox.isChecked())

  # sets experimental features
  def setExperimental(self):
    """
    TODO: Sets the experimental features 
    """
    if self.experimentalCheckbox.isChecked():
      self.debugLog("Adding experimental features")
    elif not self.experimentalCheckbox.isChecked():
      self.debugLog("Removing experimental features")
    
  # notifies when views are added or removed
  # 'pass' means do not do anything
  def canvasChanged(self, canvas):
    """
    notifies when views are added or removed
    
    'pass' means do not do anything

    This function is just overriden so docker does not
    send a handling exception
    """
    pass
  ##########