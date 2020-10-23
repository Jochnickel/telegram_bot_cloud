import requests
import json

API_URL = "https://api.telegram.org/bot"
msgAdmin = None

class TelegramApi:
    _URL = ""
    
    def __init__(self, token):
        self._URL = API_URL + token + "/"
    
    def sendMessage(self,chat_id, text):
        request = requests.get(self._URL+"sendMessage",params = {"chat_id":chat_id, "text":json.dumps(text)})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
    
    def sendDocument(self, chat_id, document, caption=None, button_array_array=None):
        request = requests.get(self._URL+"sendDocument",params = {"chat_id":chat_id,"document":document, "caption" : caption, "reply_markup":json.dumps({"inline_keyboard":button_array_array})})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
    
    def sendPhoto(self, chat_id, photo, caption=None, button_array_array=None):
        request = requests.get(self._URL+"sendPhoto",params = {"chat_id":chat_id,"photo":photo, "caption" : caption, "reply_markup":json.dumps({"inline_keyboard":button_array_array})})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
        
    def sendVoice(self, chat_id, voice, caption=None, button_array_array=None):
        request = requests.get(self._URL+"sendVoice", params = {"chat_id":chat_id,"voice":voice, "caption" : caption, "reply_markup":json.dumps({"inline_keyboard":button_array_array})})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
        
    def sendChatAction(self, chat_id, action):
        request = requests.get(self._URL+"sendChatAction",params = {"chat_id":chat_id,"action":action})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
                
    def editMessageMedia(self, chat_id, mediaType, media, message_id, button_array_array, caption=None):
        request = requests.get(self._URL+"editMessageMedia",params = {"chat_id":chat_id,"media": json.dumps({"type":mediaType, "media":media, "caption":caption}),"message_id":message_id,"reply_markup":json.dumps({"inline_keyboard":button_array_array})})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url)) # must keep this way
        
    def answerCallbackQuery(self, callback_query_id, text=None, show_alert=False, url=None, cache_time=None,chat_id=None):
        request = requests.get(self._URL+"answerCallbackQuery",params = {"callback_query_id":callback_query_id,"text":text,"url":url,"show_alert":show_alert,"chat_id":chat_id})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
        #TODO chat_id ??
        
    def deleteMessage(self, chat_id, message_id):
        request = requests.get(self._URL+"deleteMessage",params = {"chat_id":chat_id,"message_id":message_id})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
        
    def setMyCommands(self, command_array):
        request = requests.get(self._URL+"setMyCommands",params = {"commands":json.dumps(command_array)})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
    
    def getFile(self, file_id):
        request = requests.get(self._URL+"getFile",params = {"file_id":file_id})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
    
    def pinChatMessage(self, chat_id, message_id, disable_notification=False):
        request = requests.get(self._URL+"pinChatMessage",params = {"chat_id":chat_id, "message_id":message_id, "disable_notification":disable_notification})
        ok = request.status_code == requests.codes.ok
        return (ok, request.text, str(request.url))
    
