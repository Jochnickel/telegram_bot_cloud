from botocore.vendored import requests

URL = "https://api.telegram.org/bot1057097448:AAEojH8infz-eemFpJTOBb8kwM-e-kSP-Po/"
ADMIN = "452549370"


def errorAdmin():
    requests.get(URL + 'sendMessage?chat_id=' + ADMIN +
                 '&text=%s' % (str(traceback.format_exc())))


def msgAdmin(text):
    requests.get(URL + 'sendMessage?chat_id=' + ADMIN + '&text=' + str(text) +
                 " ")


try:
    import json
    import traceback
    import urllib.parse

    import FilesystemSQL

    fs = FilesystemSQL.FilesystemSQL("/tmp/filesystem.db", msgAdmin)

    requests.get(URL + 'sendMessage?chat_id=' + ADMIN + '&text=starting_bot')

    def send_message(chat_id, text, parse_mode=""):
        str_text = str(text)
        query = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': str_text,
            'parse_mode': parse_mode
        })
        requests.get(URL + "sendMessage?" + query)

    def sendButtonMessage(chat_id,
                          text,
                          buttons=[[{
                              "text": "a",
                              "callback_data": "a"
                          }, {
                              "text": "b",
                              "callback_data": "b"
                          }]]):
        str_text = str(text)
        query = urllib.parse.urlencode({
            'chat_id':
            chat_id,
            'text':
            str_text,
            'reply_markup':
            json.dumps({
                "inline_keyboard": buttons
            })
        })
        requests.get(URL + "sendMessage?" + query)

    def sendFile(tgUserId, tgFileId):
        query = urllib.parse.urlencode({
            'chat_id': tgUserId,
            'document': tgFileId
        })
        requests.get(URL + "sendDocument?" + query)

    def sendRootFolderMessage(tgUserId):
        folder = fs.getFolderContent(tgUserId, None)
        if folder:
            send_message(tgUserId, str(folder))
        else:
            send_message(
                tgUserId,
                "You have no Files or Folders.\nCreate a Folder with /newfolder FolderName or send me files."
            )

    def sendFolderInfo(tgUserId, folderId):
        try:
            folderContent = fs.getFolderContent(tgUserId, folderId)
            buttons = folderId and [[{
                "text": "⬆️ Up",
                "callback_data": "/cd_dot_dot"
            }]] or [[]]
            buttons[0].extend([{
                "text": "🏠 Home",
                "callback_data": "/cd_root"
            }, {
                "text": "🗂 New",
                "switch_inline_query_current_chat": "/newfolder New_Folder"
            }, {
                "text": "❌ Delete",
                "callback_data": "/delete " + str(folderId)
            }])
            # msgAdmin("folderContent "+str(folderContent))
            for folder_info in folderContent:
                # msgAdmin("folder_info "+str(folderContent))
                fileId = folder_info[1]
                fileName = folder_info[2]
                buttons.append([{
                    "text": fileName,
                    "callback_data": "/cd " + str(fileId)
                }])
            sendButtonMessage(tgUserId, "Files in %s :"%(fs.getFullPath(tgUserId, folderId)), buttons)
        except:
            errorAdmin()
            send_message(tgUserId, "Folder not found")

    def sendFileInfo(tgUserId, file_id):

        tgFileId = fs.getTelegramFileId(tgUserId, file_id)
        if tgFileId:
            buttons = [[{
                "text": "Download",
                "callback_data": "/download " + str(tgFileId)
            }, {
                "text": "Delete",
                "callback_data": "/delete " + str(tgFileId)
            }]]
            sendButtonMessage(tgUserId, "File " + str(tgFileId), buttons)
        else:
            sendFolderInfo(tgUserId, file_id)

    def sendCurretFileInfo(tgUserId):
        currentId = fs.getCurrentFolderId(tgUserId)
        sendFileInfo(tgUserId, currentId)

    def handleMessage(message):
        if 'chat' in message and 'document' in message:
            chat_id = message['chat']['id']
            tg_file_id = message['document']['file_id']
            origin_filename = message['document']['file_name']
            origin_ending = origin_filename.count(
                ".") and origin_filename.split(".")[-1] or ""
            user_filename = 'caption' in message and message['caption'] or None
            user_full_filename = user_filename and (
                user_filename.count(".") and user_filename
                or user_filename + origin_ending) or None

            fs.insertFile(chat_id, (user_full_filename or origin_filename),
                          tg_file_id, fs.getCurrentFolderId(chat_id))
            sendCurretFileInfo(chat_id)

        elif 'chat' in message and 'text' in message:
            chat_id = message['chat']['id']
            text = message['text']
            if "@"==text[0]:
                #remove @botname from "@botname /something asd"
                text = text[text.find(" ")+1:]
            if '/start' == text[0:6]:
                fs.setCurrentFolder(chat_id, None)
            elif '/debug' == text[0:6]:
                send_message(chat_id, fs.debugUser(chat_id))
            elif '/reset' == text[0:6]:
                confirm = text[6:]
                if 'yes' == confirm:
                    fs.resetUser(chat_id)
                else:
                    sendButtonMessage(
                        chat_id, "Are you sure to delete all your files?",
                        [[{
                            "text": "Yes",
                            "callback_data": "/reset_yes"
                        }, {
                            "text": "No",
                            "callback_data": "/reset_no"
                        }]])
            elif '/cd' == text[0:3]:
                folderId = text[3:].strip()
                fs.setCurrentFolder(chat_id, folderId)
            elif '/ls' == text[0:3]:
                folderId = text[3:].strip() or fs.getCurrentFolderId(chat_id)
            elif '/file' == text[0:5]:
                fileId = text[5:].strip()
                if fileId:
                    try:
                        sendFileInfo(chat_id, fileId)
                    except:
                        send_message(chat_id, "File / Folder not found")
                else:
                    send_message(chat_id, "Please provide a file ID")
            elif '/newfolder' == text[0:10]:
                folderName = text[10:].strip()
                currentFolder = fs.getCurrentFolderId(chat_id)
                existingFolder = fs.getFileIdByName(chat_id, folderName, currentFolder)
                if existingFolder:
                    send_message(chat_id,"Folder already exists")
                elif folderName:
                    fs.createFolder(chat_id, str(folderName), currentFolder)
                else:
                    send_message(chat_id,
                                 "Please provide a name after /newfolder")
            else:
                send_message(chat_id, "You said: " + text)
            sendCurretFileInfo(chat_id)

    def handleCallbackQuery(callback_query):
        if 'from' in callback_query and 'data' in callback_query:
            from_chat = callback_query['from']
            data = callback_query['data']
            if 'id' in from_chat:
                from_chat_id = from_chat['id']
                if '/reset_yes' == data:
                    fs.resetUser(from_chat_id)
                elif '/cd_dot_dot' == data:
                    fs.moveUp(from_chat_id)
                elif '/cd_root' == data:
                    fs.setCurrentFolder(from_chat_id, None)
                elif '/cd' == data[:3]:
                    moveToId = data[3:].strip()
                    fs.setCurrentFolder(from_chat_id, moveToId)
                elif '/download' == data[:9]:
                    downloadId = data[9:].strip()
                    sendFile(from_chat_id, downloadId)
                elif '/delete_yes' == data[:11]:
                    fileId = data[11:].strip()
                    if fileId:
                        folderContent = fs.getFolderContent(from_chat_id, fileId)
                        if folderContent:
                            send_message(
                                from_chat_id,
                                "Cant delete folder containing files: ")
                        else:
                            fs.moveUp(from_chat_id)
                            fs.deleteFile(from_chat_id, fileId)
                elif '/delete' == data[:7]:
                    fileId = data[7:].strip()
                    sendButtonMessage(
                        from_chat_id, "Delete?",
                        [[{
                            "text": "Yes",
                            "callback_data": "/delete_yes " + str(fileId)
                        }, {
                            "text": "No",
                            "callback_data": "/delete_no"
                        }]])
                sendCurretFileInfo(from_chat_id)

    def lambda_handler(event, context):
        try:
            if 'body' in event:
                body = json.loads(event['body'])
               # send_message('452549370',json.dumps(body, sort_keys=True, indent=4))

                if 'callback_query' in body:
                    callback_query = body['callback_query']
                    handleCallbackQuery(callback_query)

                if 'message' in body:
                    message = body['message']
                    handleMessage(message)

            return {'statusCode': 200}
        except:
            errorAdmin()

except:
    errorAdmin()
