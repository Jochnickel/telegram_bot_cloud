def getButton(text, callback_data):
    return {"text": text,"callback_data": callback_data}

def getBackButton():
    return {"text": "⬅️ Back","callback_data": "/cd_dot_dot"}
    
def getUpButton():
    return {"text": "⬆️ Up", "callback_data": "/cd_dot_dot"}

def getHomeButton():
    return {"text": "🏠 Home", "callback_data": "/cd_root"}
   
def getDonateButton():
    return {"text": "💵 Donate", "callback_data": "/donate"}

def getBotlistButton():
    return {"text": "⭐️View in Botlist", "callback_data": "/botlist"}


def getNewFolderButton():
    return {
        "text": "🗂 New",
        "switch_inline_query_current_chat": "/newfolder 🗂New_Folder"
    }
    
def getDownloadButton(file_id):
    return {"text": "⬇️ Download","callback_data": "/download " + str(file_id)}

def getRenameButton(old_name):
    return {
        "text":
        "✍️ Rename",
        "switch_inline_query_current_chat":
        "/rename " + str(old_name)
    }

def getDeleteButton(folderId):
    return {
        "text": "🗑 Delete",
        "callback_data": "/delete " + str(folderId)
    }

def getDeleteYesButton(fileId):
    return {
        "text": "⚠️ Yes",
        "callback_data": "/delete_yes " + str(fileId)
    }
    
def getResetYesButton():
    return {
        "text": "⚠️ Yes",
        "callback_data": "/reset_yes"
    }
  
def getDeleteNoButton():
    return {
        "text": "No",
        "callback_data": "/ls"
    }

def getNoButton():
    return {
        "text": "No",
        "callback_data": "/ls"
    }

def getReplyMarkup(buttons_array_array):
    return {"inline_keyboard":buttons_array_array}
