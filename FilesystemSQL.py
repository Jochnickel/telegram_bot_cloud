import sqlite3


class FilesystemSQL:
    _connection = None
    _msgAdmin = None
    
    def __init__(self, filename, msgAdmin = None):
        self._msgAdmin = msgAdmin
        self._connection = sqlite3.connect(filename)
        cursor = self._connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Folder (file_id INTEGER NOT NULL PRIMARY KEY, telegram_user_id INTEGER, parent_folder_id INTEGER, file_name TEXT, telegram_file_id TEXT);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS CurrentFolder (telegram_user_id INTEGER PRIMARY KEY, folder_id INTEGER);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS FileEnding (mime_type TEXT PRIMARY KEY, file_ending TEXT);"
        )
        self._connection.commit()

    def getFolderContent(self, tgUserId, folderId=None):
        if folderId:
            cursor = self._connection.cursor()
            cursor.execute("SELECT telegram_user_id, file_id, file_name, parent_folder_id, telegram_file_id FROM Folder WHERE telegram_user_id=? AND parent_folder_id=?",(tgUserId, folderId))
            rows = cursor.fetchall()
            return rows
        else:
            cursor = self._connection.cursor()
            cursor.execute(
                "SELECT telegram_user_id, file_id, file_name, parent_folder_id, telegram_file_id FROM Folder WHERE telegram_user_id=? AND parent_folder_id IS NULL",
                (tgUserId, ))
            rows = cursor.fetchall()
            return rows
            
    def getFileIdByName(self, tgUserId, fileName, parentFolderId):
        cursor = self._connection.cursor()
        if parentFolderId is None:
            cursor.execute(
                "SELECT file_id FROM Folder WHERE telegram_user_id=? AND file_name=? AND parent_folder_id IS NULL",
                (tgUserId, fileName))
        else:
            cursor.execute(
                "SELECT file_id FROM Folder WHERE telegram_user_id=? AND file_name=? AND parent_folder_id=?",
                (tgUserId, fileName, parentFolderId))
        rows = cursor.fetchall()
        return rows and rows[0] and rows[0][0] or None
            
            
    def deleteFile(self, tgUserId, fileId):
        cursor = self._connection.cursor()
        cursor.execute(
            "DELETE FROM Folder WHERE telegram_user_id=? and file_id=?",
            (tgUserId, fileId))
        self._connection.commit()
        
    def getTelegramFileId(self, tgUserId, fileId):
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT telegram_file_id FROM Folder WHERE telegram_user_id=? and file_id=?",
            (tgUserId, fileId))
        rows = cursor.fetchall()
        return rows and rows[0] and rows[0][0] or None

    def createFolder(self, tgUserId, folderName, parentFolderId=None):
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO Folder (telegram_user_id, file_name, parent_folder_id) VALUES (?,?,?)",
            (tgUserId, folderName, parentFolderId))
        rows = self._connection.commit()
        return rows

    def insertFile(self, tgUserId, fileName, tgFileId, parentFolderId=None):
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO Folder (telegram_user_id, file_name, telegram_file_id, parent_folder_id) VALUES (?,?,?,?)",
            (tgUserId, fileName, tgFileId, parentFolderId))
        rows = self._connection.commit()

    def debugUser(self, tgUserId):
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM Folder WHERE telegram_user_id=?",
                       (tgUserId, ))
        return str(cursor.fetchall())

    def setCurrentFolder(self, tgUserId, folderId):
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM CurrentFolder WHERE telegram_user_id=?",
                       (tgUserId, ))
        cursor.execute(
            "INSERT INTO CurrentFolder (telegram_user_id, folder_id) VALUES (?,?)",
            (tgUserId, folderId))
        self._connection.commit()

    def resetUser(self, tgUserId):
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM Folder WHERE telegram_user_id=?",
                       (tgUserId, ))
        self._connection.commit()
        self.setCurrentFolder(tgUserId, None)
    
    def getFullPath(self, tgUserId, fileId):
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT file_name, parent_folder_id FROM Folder WHERE telegram_user_id=? AND file_id=?",
            (tgUserId, fileId))
        rows = cursor.fetchall()
        name = rows and rows[0] and rows[0][0]
        parentId = name and rows[0][1]
        if name:
            return self.getFullPath(tgUserId,parentId)+"/"+str(name)
        else:
            return "Home"
        
    
    def moveUp(self, tgUserId):
      currentId = self.getCurrentFolderId(tgUserId)
      if currentId:
        cursor = self._connection.cursor()
        cursor.execute("SELECT parent_folder_id FROM Folder WHERE telegram_user_id=? and file_id=?",(tgUserId, currentId))
        rows = cursor.fetchall()
        self.setCurrentFolder(tgUserId,rows[0][0])


    def getCurrentFolderId(self, tgUserId):
      try:
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT folder_id FROM CurrentFolder WHERE telegram_user_id=? ",
            (tgUserId, ))
        rows = cursor.fetchall()
        return rows[0][0]
      except:
        return None
