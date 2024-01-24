import PySimpleGUI as sg
from copy import deepcopy

sg.theme("DarkGrey2")


class ExportPopUp:
    LAYOUT = [
        [sg.Text("Where to Save?", font="_ 18")],
        [sg.Sizer(0, 5)],
        [
            sg.Text("File:"),
            sg.Push(),
            sg.Text("Name of file"),
            sg.FileSaveAs(
                button_text="Browse",
                file_types=(("JSON file", "*.json"),),
                default_extension=".json",
            ),
        ],
        [sg.Button("Save", key="save_to")],
    ]

    def __init__(self):
        self.window = sg.Window("Save as Window", deepcopy(self.LAYOUT), finalize=True)

    def start(self):
        self.handle()
        return {"file": self._ret_vals["Browse"]}

    def handle(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or (event == "save_to" and values["Browse"] != ""):
                self._ret_vals = values
                break

            if event == "save_to" and values["Browse"] == "":
                sg.popup_error("Nothing selected.", title="Error", keep_on_top=True)

        self.window.close()


if __name__ == "__main__":
    print(ExportPopUp().start())
