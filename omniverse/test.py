
import ctypes
import os
import sys
import time
import threading

class OmniFolderEntry(ctypes.Structure):
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

def main():
  lib = ctypes.WinDLL("D:/Projects/OmniverseCPP/OmniverseCPP/bin/Debug/ovCLibraryd.dll")
  destinationPath = b"omniverse://localhost/Projects/"

  lib.cPing.restype = ctypes.c_int
  lib.cInitialize.restype = ctypes.c_bool
  lib.cInitialize.argtypes = [ctypes.c_bool, ctypes.c_int]
  lib.cGetUsername.restype = ctypes.c_char_p
  lib.cGetUsername.argtypes = [ctypes.c_char_p]
  lib.cGetLogString.restype = ctypes.c_char_p
  lib.cCreateStage.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
  lib.cCreateStage.restype = ctypes.c_char_p
  lib.cDeleteStage.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
  lib.cDeleteStage.restype = ctypes.c_int
  lib.cTransferFile.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
  lib.cGetGlobalError.restype = ctypes.c_char_p
  lib.cIsValidURL.argtypes = [ctypes.c_char_p]
  lib.cIsValidURL.restype = ctypes.c_bool
  lib.cGetLocalFile.argtypes = [ctypes.c_char_p]
  lib.cGetLocalFile.restype = ctypes.c_char_p
  lib.cFetchFolderEntries.argtypes = [ctypes.c_char_p]
  lib.cFetchFileEntry.argtypes = [ctypes.c_int]
  lib.cFetchFileEntry.restype = ctypes.POINTER(OmniFolderEntry)
  lib.cGetFolderCount.restype = ctypes.c_int
  lib.cIsEntryFolder.restype = ctypes.c_bool
  lib.cIsEntryFolder.argtypes = [ctypes.c_int]

  if not lib.cPing():
    return -1

  if lib.cInitialize(True, 0):
    print("%s"%(lib.cGetUsername(destinationPath).decode()))
    print("%s"%(lib.cGetLogString().decode()))
    # stageName = lib.jsCreateStage(destinationPath, b"pyTest.usd")
    # print(str(stageName.decode()))

    # lib.jsTransferFile(b"C:/Users/Marco/Pictures/tlm.jpg", destinationPath + b"pyTestImage.jpg")
    # lib.jsTransferFile(destinationPath + b"pyTestImage.jpg", b"C:/Users/Marco/Pictures/tlm_2.jpg")
    lib.cFetchFolderEntries(destinationPath)
    tempVar = lib.cFetchFileEntry(0).contents.relativePath.decode()
    print(tempVar)

    lib.cShutdown()
  else:
    print("Error retrieving library %s"%(lib.cGetGlobalError()))
    return -1

  
  return 0


if __name__ == "__main__":
  main()