import os
import time
import TelegramApi
import Buttons
import FilesystemMySQL

RED_PIC = "https://raw.githubusercontent.com/Jochnickel/telegram_bot_cloud/main/delete.png"
BG_PIC = "https://cdn.pixabay.com/photo/2020/07/19/13/18/sky-5420026__340.jpg"
EMPTY_SKY = "https://cdn.pixabay.com/photo/2020/07/19/13/18/sky-5420026__340.jpg"
DONATE = "Paypal: joachim.redmi@gmail.com"
BOTS_ARCHIVE_LINK = "https://t.me/BotsArchive/1559"
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

msgAdmin = None  # To be injected
errorAdmin = None  #

api = TelegramApi.TelegramApi(TOKEN)
fs = FilesystemMySQL.FilesystemMySQL()


def sendPhoto(updateMsg, tgUserId, photo, caption, button_array_array):
    if updateMsg:
        info = api.editMessageMedia(
            chat_id=tgUserId,
            mediaType='photo',
            media=photo,
            message_id=updateMsg,
            button_array_array=button_array_array,
            caption=caption)
        
        if info[0] or info[1].count('are exactly the same'):
            return info
        # editMedia on voice message
        
    info = api.sendPhoto(
        chat_id=tgUserId,
        photo=photo,
        caption=caption,
        button_array_array=button_array_array)
        
    if info[0] and updateMsg:
        api.deleteMessage(tgUserId,updateMsg)
        
    return info


def updateMessage(updateMsg, tgUserId):
    fileId = fs.getCurrentFileId(tgUserId)
    tgFileId, fileName = fs.getTelegramFileIdAndFileNameById(tgUserId, fileId)
    fullPath = fs.getFullPath(tgUserId, fileId)
    
    if tgFileId:
        #File
        buttons = [[
            Buttons.getBackButton(),
            Buttons.getHomeButton(),
            Buttons.getRenameButton(fileName),
            Buttons.getDeleteButton(fileId)
        ]]
        if updateMsg:
            # Single File, update Message
            
            for t in ['document', 'photo', 'audio','video', 'animation']:
                info = api.editMessageMedia(
                    chat_id=tgUserId,
                    mediaType=t,
                    media=tgFileId,
                    message_id=updateMsg,
                    button_array_array=buttons,
                    caption=fullPath)
                # msgAdmin("info")
                # msgAdmin(info)
                if info[0]:
                    return info
            
            
            # voice after else
            info = api.sendVoice(
                chat_id=tgUserId,
                voice=tgFileId,
                caption=fullPath,
                button_array_array=[[Buttons.getDeleteButton(fileId)]])
            if info[0]:
                return info
                
            msgAdmin("Single File, update Message failed")
        
        # else:
        # Single File, new Message
        info = api.sendDocument(
            chat_id=tgUserId,
            document=tgFileId,
            caption=fullPath,
            button_array_array=buttons)
        if info[0]:
            return info
        msgAdmin("Single File new Message failed")
        
    else:
        #Folder
        buttons = []
        photo=BG_PIC
        
        folderContent = fs.getFolderContent(tgUserId, fileId)

        # dont rewrite fileId, fileName!!!
        for f_id, f_name, tg_f_id in folderContent:
            buttons.append(
                [Buttons.getButton(f_name, '/file ' + str(f_id))])

        if fileId:
            #subfolder
            if len(buttons) < 1:
                buttons.append([Buttons.getDeleteButton(fileId)])
                photo=EMPTY_SKY
            
            buttons.append([
                Buttons.getUpButton(),
                Buttons.getNewFolderButton(),
                Buttons.getRenameButton(fileName),
                Buttons.getHomeButton()
            ])
        else:
            #root folder
            buttons.append([
                Buttons.getHomeButton(),
                Buttons.getNewFolderButton(),
                Buttons.getDonateButton(),
                Buttons.getBotlistButton()
            ])
            
        
        caption = ("Files in Folder %s:" % (fullPath, ))
        return sendPhoto(
            updateMsg,
            tgUserId=tgUserId,
            photo=photo,
            caption=caption,
            button_array_array=buttons)

# api.setMyCommands

def handleBotCommand(updateMsg, tgUserId, cmd, halfString=None):
    cmd = cmd.split()[0]
    halfString = str(halfString).strip()
    if "/ls" == cmd:
        if halfString:
            fs.setCurrentFolder(tgUserId, halfString)
        return updateMessage(updateMsg, tgUserId)
    elif "/_f" == cmd:
        dump = fs._dumpFile(tgUserId, halfString)
        api.sendMessage(tgUserId, dump)
    elif "/_announce" == cmd:
        pass
        # allUsers = fs._getAllUsers(tgUserId)
        # for u in allUsers:
        #     api.sendMessage(u[0], halfString)
    elif "/_u" == cmd:
        dump = fs.dumpUser(halfString)
        api.sendMessage(tgUserId, dump)
    elif "/_delete_file" == cmd:
        fs._deleteFile(tgUserId, halfString)
        return updateMessage(updateMsg, tgUserId)
    elif "/_moveHome" == cmd:
        fs._moveHome(tgUserId, halfString)
        return updateMessage(updateMsg, tgUserId)
    elif "/_premium" == cmd:
        fs._makePremium(tgUserId, halfString)
        api.sendMessage(tgUserId, "made %s promium"%halfString)
    elif "/_unpremium" == cmd:
        fs._makePremium(tgUserId, halfString, False)
        api.sendMessage(tgUserId, "removed %s promium"%halfString)
    elif "/dump" == cmd:
        dump = fs.dumpUser(tgUserId)
        api.sendMessage(tgUserId, dump)
    elif "/f" == cmd:
        fileId = fs.getCurrentFileId(tgUserId)
        api.sendMessage(tgUserId, fileId)
    elif "/id" == cmd:
        api.sendMessage(tgUserId, tgUserId)
    elif "/tf" == cmd:
        fileId = fs.getCurrentFileId(tgUserId)
        tgFileId = fs.getTelegramFileId(tgUserId,fileId)
        api.sendMessage(tgUserId, tgFileId)
    elif "/clean" == cmd:
        messy = fs.cleanAbandonedFiles()
        api.sendMessage(tgUserId, messy)
    elif "/getFile" == cmd:
        fileInfo = api.getFile(halfString)
        api.sendMessage(tgUserId, fileInfo)
    elif "/stats" == cmd:
        stats = fs.getStats()
        api.sendMessage(tgUserId, "Users: %s, Total Files: %s"%stats)
    elif "/donate" == cmd:
        api.sendMessage(tgUserId, DONATE)
    elif "/delete" == cmd:
        fileId = halfString
        fileName = fs.getFileNameById(tgUserId, fileId)
        info = sendPhoto(
            updateMsg=updateMsg,
            tgUserId=tgUserId,
            photo=RED_PIC,
            caption=("Do you really want to delete %s?" % fileName),
            button_array_array=[[
                Buttons.getDeleteYesButton(fileId),
                Buttons.getNoButton()
            ]])
        if not info[0]:
            msgAdmin("sendPhoto failed")
            msgAdmin(info)
        return info
    elif "/delete_yes" == cmd:
        fs.moveUp(tgUserId)
        fs.deleteFile(tgUserId, halfString)
        return updateMessage(updateMsg, tgUserId)
    elif "/cd_dot_dot" == cmd:
        fs.moveUp(tgUserId)
        return updateMessage(updateMsg, tgUserId)
    elif "/cd_root" == cmd:
        fs.setCurrentFolder(tgUserId, None)
        return updateMessage(updateMsg, tgUserId)
    elif "/file" == cmd:
        fs.setCurrentFolder(tgUserId, halfString)
        return updateMessage(updateMsg, tgUserId)
    elif "/newfolder" == cmd:
        folderId = fs.getCurrentFolderId(tgUserId)
        fs.createFolder(tgUserId, halfString, folderId)
        return updateMessage(updateMsg, tgUserId)
    elif "/start" == cmd:
        fs.addUser(tgUserId)
        fs.setCurrentFolder(tgUserId, None)
        return updateMessage(updateMsg, tgUserId)
    elif "/rename" == cmd:
        fileId = fs.getCurrentFileId(tgUserId)
        fs.renameFile(tgUserId, fileId, halfString)
        updateMessage(updateMsg, tgUserId)
    elif "/reset" == cmd:
        return sendPhoto(
            updateMsg=updateMsg,
            tgUserId=tgUserId,
            photo=RED_PIC,
            caption=("Do you really want to delete all your files?"),
            button_array_array=[[
                Buttons.getResetYesButton(),
                Buttons.getNoButton()
            ]])
    elif "/reset_yes" == cmd:
        fs.resetUser(tgUserId)
        return updateMessage(updateMsg, tgUserId)
    elif "/botlist" == cmd:
        api.sendMessage(tgUserId, BOTS_ARCHIVE_LINK)
    else:
        msgAdmin("else")
        msgAdmin(cmd)
        return (None, None, None)


def searchFileNames(chat_id, string):
    rows = fs.searchFileByName(chat_id, string)
    for row in rows:
        fullPath = fs.getFullPath(chat_id, row[0])
        api.sendMessage(chat_id, "Found %s"%(fullPath,))


def getCmdsInMessage(message):
    if not 'entities' in message:
        return None
    entities = message['entities']
    cmds = []
    for e in entities:
        if 'bot_command' == e['type']:
            text = message['text']
            offset = e['offset']
            length = e['length']
            cmd = text[offset:offset + length]
            halfString = text[offset + length:]
            cmds.append((cmd, halfString))
    return cmds

# Buttons (only?)
def handleCallbackQuery(callback_query):
    if 'data' in callback_query and 'message' in callback_query:
        callback_query_id = callback_query['id']

        message = callback_query['message']
        message_id = message['message_id']
        chat = message['chat']
        chat_id = chat['id']
        data = callback_query['data'].strip()
        
        fs.setUserMessageId(chat_id, message_id)

        cmd = data.split()[0]
        stringHalf = data[len(cmd):]
        handleBotCommand(message_id, chat_id, cmd, stringHalf)
    
    else:
        
        msgAdmin("No data and message in callback_query")

    api.answerCallbackQuery(callback_query_id)


def handleMessage(message):
    #Non Optional Values
    chat = message['chat']
    message_id = message['message_id']
    chat_id = chat['id']
    
    # msgAdmin("message")
    
    if 'document' in message:
        document = message['document']
        fileName = document['file_name']
        fileId = document['file_id']
        # caption
        currentFolder = fs.getCurrentFolderId(chat_id)
        
        fs.insertFile(chat_id, fileName, fileId, currentFolder)
        api.deleteMessage(chat_id, message_id)
        updateMessage(None, chat_id)
        
    elif 'photo' in message:
        photo = message['photo']
        timestamp = str(time.ctime())
        fileId = photo.pop()['file_id']
        currentFolder = fs.getCurrentFolderId(chat_id)
        
        fs.insertFile(chat_id, '🖼'+timestamp, fileId, currentFolder)
        api.deleteMessage(chat_id, message_id)
        updateMessage(None, chat_id)
        
    elif 'audio' in message:
        audio = message['audio']
        fileId = audio['file_id']
        title = 'title' in audio and audio['title'] or 'Audiofile'
        currentFolder = fs.getCurrentFolderId(chat_id)
        
        fs.insertFile(chat_id, '🎵'+title, fileId, currentFolder)
        api.deleteMessage(chat_id, message_id)
        updateMessage(None, chat_id)
        
    elif 'voice' in message:
        voice = message['voice']
        fileId = voice['file_id']
        date = message['date']
        title = '🎙Voicemessage'+str(date)
        currentFolder = fs.getCurrentFolderId(chat_id)
        
        fs.insertFile(chat_id, title, fileId, currentFolder)
        api.deleteMessage(chat_id, message_id)
        updateMessage(None, chat_id)
        
    elif 'text' in message:
        text = message['text']
        if '@' == text[0]:
            text = text[text.find(" ") + 1]

        bot_commands = getCmdsInMessage(message)

        if bot_commands:
            for cmd, halfString in bot_commands:
                info = handleBotCommand(None, chat_id, cmd, halfString)
                if info:
                    if info[0]:
                        api.deleteMessage(chat_id, message_id)
                        oldMsgId = fs.getUserMessageId(chat_id)
                        if oldMsgId:
                            api.deleteMessage(chat_id, oldMsgId)
                    else:
                        msgAdmin("api.send? error")
                        msgAdmin(info)
        else:
            results = searchFileNames(chat_id, text)
