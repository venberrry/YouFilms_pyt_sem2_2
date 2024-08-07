from flask_socketio import SocketIO, emit, Namespace
from transliterate import translit

class Chat(Namespace):

	def on_connect(self):
		print('connected!')

	def on_disconnect(self):
		print('disconnected!')

	def on_send_msg(self, data: dict):
		print('got it')
		if data['msg'] != "":
			length_msg = len(data['msg'])
			latin_msg = translit(data['msg'], "ru", reversed=True)
			new_dict = {}
			new_dict['length_msg'] = length_msg
			new_dict['latin_msg'] = latin_msg
			emit('mymsg', data['msg'], broadcast=True)
			emit('recv', new_dict, broadcast=True)

class MySocket(SocketIO):
	def __init__(self, app, **kwargs):
		super().__init__(app, **kwargs)
		self.on_namespace(Chat('/chat'))
