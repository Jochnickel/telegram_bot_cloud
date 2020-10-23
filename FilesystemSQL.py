import os
import pymysql

RDS_USER = os.environ["RDS_USER"]
RDS_PASSWD = os.environ["RDS_PASSWD"]
RDS_URL = os.environ["RDS_URL"]

msgAdmin = None


class FilesystemMySQL:
    __connection = None

    def __init__(self):
        self.__connection = pymysql.connect(
            host=RDS_URL, user=RDS_USER, passwd=RDS_PASSWD)
        cursor = self.__connection.cursor()
        cursor.execute("USE Filesystem")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS Folder (file_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, telegram_user_id INTEGER, parent_folder_id INTEGER, file_name TEXT, telegram_file_id TEXT);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS User (telegram_user_id INTEGER PRIMARY KEY, message_id INTEGER, current_file_id INTEGER, premium BOOL, admin BOOL);"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS KnownMessage (telegram_user_id INTEGER, message_id INTEGER, PRIMARY KEY (telegram_user_id, message_id));"
        )
        self.__connection.commit()
        
    def isAdmin(self, tgUserId):
        cursor = self.__connection.cursor()
        cursor.execute(
            "SELECT admin FROM User WHERE telegram_user_id=%s",
            (tgUserId, ))
        rows = cursor.fetchall()
        return rows and rows[0] and rows[0][0] or False
    
    #admin commands start with _
    
    def _dumpFile(self, admin_id, fileId):
        if self.isAdmin(admin_id):
            cursor = self.__connection.cursor()
            cursor.execute(
                "SELECT * FROM Folder WHERE file_id=%s",
                (fileId, ))
            rows = cursor.fetchall()
            return rows
        return None
        
    def _deleteFile(self, admin_id, fileId):
        if self.isAdmin(admin_id):
            cursor = self.__connection.cursor()
            cursor.execute(
                "DELETE FROM Folder WHERE file_id=%s",
                (fileId, ))
            return self.__connection.commit()
        return None
        
    def _moveHome(self, admin_id, fileId):
        if self.isAdmin(admin_id):
            cursor = self.__connection.cursor()
            cursor.execute(
                "UPDATE Folder SET parent_folder_id=Null WHERE file_id=%s",
                (fileId, ))
            rows = cursor.fetchall()
            return rows
        return None
    
    def _makePremium(self, admin_id, userId, premium=True):
        if self.isAdmin(admin_id):
            cursor = self.__connection.cursor()
            self.addUser(userId)
            cursor.execute(
                "UPDATE User SET premium=%s WHERE telegram_user_id=%s",
                (premium, userId))
            self.__connection.commit()
        return None

    def _getAllUsers(self, admin_id):
        if self.isAdmin(admin_id):
            cursor = self.__connection.cursor()
            cursor.execute("SELECT telegram_user_id FROM User")
            rows = cursor.fetchall()
            return rows
        return None

        
    
    def getUserMessageId(self, tgUserId):
        cursor = self.__connection.cursor()
        cursor.execute(
            "SELECT message_id FROM User WHERE telegram_user_id=%s",
            (tgUserId, ))
        rows = cursor.fetchall()
        return rows and rows[0] and rows[0][0] or None
   
    def setUserMessageId(self, tgUserId, messageId):
        cursor = self.__connection.cursor()
        self.addUser(tgUserId)
        cursor.execute(
            "UPDATE User SET message_id=%s WHERE telegram_user_id=%s",
            (messageId, tgUserId))
        self.__connection.commit()
    
    def getFolderContent(self, tgUserId, folderId=None):
        if folderId:
            cursor = self.__connection.cursor()
            cursor.execute(
                "SELECT file_id, file_name, telegram_file_id FROM Folder WHERE telegram_user_id=%s AND parent_folder_id=%s",
                (tgUserId, folderId))
            rows = cursor.fetchall()
            return rows
        else:
            cursor = self.__connection.cursor()
            cursor.execute(
                "SELECT file_id, file_name, telegram_file_id FROM Folder WHERE telegram_user_id=%s AND parent_folder_id IS NULL",
                (tgUserId, ))
            rows = cursor.fetchall()
            return rows

    def getFileIdByLocation(self, tgUserId, fileName, parentFolderId):
        cursor = self.__connection.cursor()
        if parentFolderId is None:
            cursor.execute(
                "SELECT file_id FROM Folder WHERE telegram_user_id=%s AND file_name=%s AND parent_folder_id IS NULL",
                (tgUserId, fileName))
        else:
            cursor.execute(
                "SELECT file_id FROM Folder WHERE telegram_user_id=%s AND file_name=%s AND parent_folder_id=%s",
                (tgUserId, fileName, parentFolderId))
        rows = cursor.fetchall()
        return rows and rows[0] and rows[0][0] or None

    def deleteFile(self, tgUserId, fileId):
        folderContent = self.getFolderContent(tgUserId, fileId)
        for f_id, f_name, tg_f_id in folderContent:
            self.deleteFile(tgUserId, f_id)
        cursor = self.__connection.cursor()
        cursor.execute(
            "DELETE FROM Folder WHERE telegram_user_id=%s and file_id=%s",
            (tgUserId, fileId))
        self.__connection.commit()

    def getTelegramFileId(self, tgUserId, fileId):
        cursor = self.__connection.cursor()
        cursor.execute(
            "SELECT telegram_file_id FROM Folder WHERE telegram_user_id=%s and file_id=%s",
            (tgUserId, fileId))
        rows = cursor.fetchall()
        return rows and rows[0] and rows[0][0] or None

    def insertFile(self, tgUserId, fileName, tgFileId, parentFolderId=None):
        cursor = self.__connection.cursor()
        cursor.execute(
            "INSERT INTO Folder (telegram_user_id, file_name, telegram_file_id, parent_folder_id) VALUES (%s,%s,%s,%s)",
            (tgUserId, fileName, tgFileId, parentFolderId))
        self.__connection.commit()

    def createFolder(self, tgUserId, folderName, parentFolderId=None):
        return self.insertFile(tgUserId, folderName, None, parentFolderId)
        
    def searchFileByName(self, tgUserId, searchString):
        cursor = self.__connection.cursor()
        cursor.execute("SELECT file_id FROM Folder WHERE telegram_user_id=%s AND file_name LIKE %s",
                       (tgUserId, '%'+searchString+'%'))
        rows = cursor.fetchall()
        return rows
    
    def getTelegramFileIdAndParentFolderId(self, tgUserId, fileId):
        cursor = self.__connection.cursor()
        cursor.execute(
            "SELECT telegram_file_id, parent_folder_id FROM Folder WHERE telegram_user_id=%s and file_id=%s",
            (tgUserId, fileId))
        rows = cursor.fetchall()
        return rows and rows[0] or (None, None)
        
    
    def dumpUser(self, tgUserId):
        cursor = self.__connection.cursor()
        out = "Files : "
        cursor.execute(
            "SELECT file_id FROM Folder WHERE telegram_user_id=%s",
            (tgUserId, ))
        out += str(cursor.fetchall())
        out += "\n User:"
        cursor.execute(
            "SELECT * FROM User WHERE telegram_user_id=%s",
            (tgUserId, ))
        out += str(cursor.fetchall())
        return out

    def addUser(self, tgUserId):
        cursor = self.__connection.cursor()
        cursor.execute("INSERT IGNORE INTO User (telegram_user_id) VALUES (%s)",
                       (tgUserId, ))
        self.__connection.commit()
        
    def setCurrentFolder(self, tgUserId, folderId):
        cursor = self.__connection.cursor()
        self.addUser(tgUserId)
        cursor.execute(
            "UPDATE User SET current_file_id=%s WHERE telegram_user_id=%s",
            (folderId, tgUserId))
        self.__connection.commit()

    def getFileNameAndParentFolderById(self, tgUserId, fileId):
        cursor = self.__connection.cursor()
        cursor.execute(
            "SELECT file_name, parent_folder_id FROM Folder WHERE telegram_user_id=%s AND file_id=%s",
            (tgUserId, fileId))
        rows = cursor.fetchall()
        return rows and rows[0] or (None, None)
    
    def getTelegramFileIdAndFileNameById(self, tgUserId, fileId):
        cursor = self.__connection.cursor()
        cursor.execute(
            "SELECT telegram_file_id, file_name FROM Folder WHERE telegram_user_id=%s AND file_id=%s",
            (tgUserId, fileId))
        rows = cursor.fetchall()
        return rows and rows[0] or (None, None)

    def getFileNameById(self, tgUserId, fileId):
        filename, parentId = self.getFileNameAndParentFolderById(
            tgUserId, fileId)
        return filename

    def getFullPath(self, tgUserId, fileId):
        filename, parentId = self.getFileNameAndParentFolderById(
            tgUserId, fileId)
        if filename:
            return self.getFullPath(tgUserId, parentId) + "/" + filename
        else:
            return "Home"

    def moveUp(self, tgUserId):
        currentId = self.getCurrentFileId(tgUserId)
        if currentId:
            cursor = self.__connection.cursor()
            cursor.execute(
                "SELECT parent_folder_id FROM Folder WHERE telegram_user_id=%s and file_id=%s",
                (tgUserId, currentId))
            rows = cursor.fetchall()
            parentFolderId = rows and rows[0] and rows[0][0] or None
            self.setCurrentFolder(tgUserId, parentFolderId)

    def getCurrentFolderId(self, tgUserId):
        currentFile = self.getCurrentFileId(tgUserId)
        tgFileId, parent = self.getTelegramFileIdAndParentFolderId(tgUserId, currentFile)
        if tgFileId:
            return parent
        else:
            return currentFile
            
    def getCurrentFileId(self, tgUserId):
        try:
            cursor = self.__connection.cursor()
            cursor.execute(
                "SELECT current_file_id FROM User WHERE telegram_user_id=%s",
                (tgUserId, ))
            rows = cursor.fetchall()
            return rows and rows[0] and rows[0][0] or None
        except:
            return None

    def resetUser(self, tgUserId):
        cursor = self.__connection.cursor()
        cursor.execute("DELETE FROM Folder WHERE telegram_user_id=%s",
                       (tgUserId, ))
        self.__connection.commit()
        self.setCurrentFolder(tgUserId, None)
        
    def renameFile(self, tgUserId, fileId, newName):
        cursor = self.__connection.cursor()
        cursor.execute("UPDATE Folder SET file_name=%s WHERE telegram_user_id=%s AND file_id=%s",
                       (newName, tgUserId, fileId))
        self.__connection.commit()
        
    def getStats(self):
        cursor = self.__connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT telegram_user_id), COUNT(DISTINCT file_id) FROM Folder")
        rows = cursor.fetchall()
        return rows and rows[0]
        
    def cleanAbandonedFiles(self):
        cursor = self.__connection.cursor()
        
        cursor.execute("SELECT file_id, telegram_user_id, parent_folder_id FROM Folder")
        allFiles = cursor.fetchall()
        
        
        ALL_IDS = []
        allIds = {}
        
        for f_id, tg_usr_id, pr_f_id in allFiles:
           allIds[f_id] = pr_f_id
           ALL_IDS.append(f_id)
           
        out = []
        
        for f_id in ALL_IDS:
            while allIds[f_id] in allIds:
                allIds[f_id] = allIds[allIds[f_id]]
            if allIds[f_id]:
                del allIds[f_id]
                out.append(f_id)
                cursor.execute("UPDATE Folder SET parent_folder_id=Null WHERE file_id=%s",(f_id,))
                
        self.__connection.commit()
        return out
