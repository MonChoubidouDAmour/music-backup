import PySimpleGUI as sg
from copy import deepcopy

sg.theme("DarkGrey2")

class AddAccount:
	ID_LEN = 32

	LAYOUT = [
		[sg.Text("Type your CLIENT_ID below:", font="_ 12", pad=(0, 0))],
		[sg.Input(key="client_id", s=(30, 1), font="_ 12", enable_events=True)],
		[sg.Button("Submit", key="submit", font="_ 12")]
	]


	def __init__(self, backend = None):
		self.backend = backend
		self.window = sg.Window("Add Account", deepcopy(self.LAYOUT), finalize=True)
		self.CLIENT_ID = None
		self.handle()

	def checkInput(self, client_id):
		error_messages = {
			"empty": "Client ID field is empty.",
			"length": "Client ID should be 32 characters long.",
		}

		if not client_id:
			error_key = "empty"
		elif len(client_id) != self.ID_LEN:
			error_key = "length"
		else:
			return True

		sg.popup_error(
			error_messages[error_key],
			title="Error",
			font="_ 12",
			keep_on_top=True
		)
		return False

	def handle(self):
		while True:
			event, values = self.window.read()

			# print(event, values) # for debugging

			if event in (sg.WIN_CLOSED, 'Cancel'):
				break

			if event == "client_id" and len(values[event]) > 32:
				self.window[event].update(value=values[event][:32])

			if event == "submit" and self.checkInput(values["client_id"]):
				self.CLIENT_ID = values["client_id"]
				break
		self.window.close()

if __name__ == "__main__":
	print(AddAccount().CLIENT_ID)