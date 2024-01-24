from os.path import exists, expanduser
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from enum import auto

import PySimpleGUI as sg
import json

from .addaccount_popup import AddAccount
from .export_popup import ExportPopUp

sg.theme("DarkGrey2")


@dataclass(frozen=True)
class PlaylistID:
    name: str
    id: str


@dataclass(frozen=True)
class TrackID:
    playlist: PlaylistID
    name: str
    album: str
    artist: str
    id: str


SAVED_ACCOUNT_PATH = "~/.accounts.json"
LIBRARY_UID = PlaylistID("library", auto())

SYMBOL_GO = "GO"


class MainGUI:

    TDATA = sg.TreeData()

    # https://www.pysimplegui.org/en/latest/call%20reference/
    BODY = [
        [
            sg.Frame(
                "Accounts",
                [
                    [
                        sg.Combo(
                            [],
                            default_value="Please select...",
                            s=(95, 1),
                            readonly=True,
                            key="accounts",
                        ),
                        sg.Button(
                            SYMBOL_GO,
                            disabled_button_color="gray",
                            key="account_selection",
                        ),
                        sg.Button("+", key="new_account", disabled_button_color="gray"),
                    ]
                ],
                key="backup",
            )
        ],
        [
            sg.Frame(
                "Tracks",
                [
                    [
                        sg.Tree(
                            data=TDATA,
                            key="tree",
                            headings=[""],
                            col_widths=[3],
                            col0_width=86,
                            expand_x=True,
                            expand_y=True,
                            enable_events=True,
                            auto_size_columns=False,
                            num_rows=20,
                        )
                    ]
                ],
            )
        ],
        [
            sg.Frame(
                "Actions",
                [
                    [
                        sg.Button(
                            "Save As",
                            key="save_to",
                            disabled=True,
                            disabled_button_color="gray",
                        ),
                    ]
                ],
            )
        ],
    ]

    FOOTER = [
        [sg.StatusBar("Nothing Happening", key="status", s=(100, 1))],
    ]

    LAYOUT = [*BODY, *FOOTER]

    UNFOCUS_TARGET = ["accounts", "account_selection", "new_account", "save_to"]

    def __init__(self, backend=None):
        self.backend = backend
        self._selected = None

        self.window = sg.Window("Music Backup", self.LAYOUT, finalize=True)
        self.window["tree"].Widget.configure(show="tree")
        self.TDATA.insert("", LIBRARY_UID, "Liked Songs", ["OK"])

        self.refresh()
        self.loadAccounts()
        self.handle()

    def loadAccounts(self):
        if not exists(expanduser(SAVED_ACCOUNT_PATH)):
            return

        try:
            storage = open(expanduser(SAVED_ACCOUNT_PATH), "r")
            accounts = json.load(storage)
            assert isinstance(accounts, list), "Error loading the file"
        except Exception:
            exit(1)

        self.window["accounts"].update(values=accounts, value="Choose an account")
        storage.close()

    def saveAccounts(self):
        accounts = self.getAccounts()
        if len(accounts) == 0:
            return

        try:
            storage = open(expanduser(SAVED_ACCOUNT_PATH), "w")
        except Exception as ex:
            sg.popup_error_with_traceback("Error while saving account:", ex)
            exit(1)

        json.dump(accounts, storage)
        storage.flush()
        storage.close()

    def addAccount(self, client_id):
        accounts = self.getAccounts()
        if client_id in accounts:
            sg.popup_error(
                "Duplicate account!",
                title="Error",
                font="_ 12",
                keep_on_top=True,
            )
            return
        accounts.append(client_id)
        self.window["accounts"].update(values=accounts)

        if len(accounts) == 1:
            self.window["accounts"].update(value=accounts[0])
        self.saveAccounts()

    def newAddAccount(self):
        setup = AddAccount()
        client_id = setup.CLIENT_ID
        if client_id == None:
            return
        self.addAccount(client_id)
        del setup

    def getAccounts(self):
        # Unofficial way
        return self.window["accounts"].Values

    def loadTracklist(self):
        track_count = 0

        self.setStatus("Loading Playlists")
        playlists = self.SpotipyAPI.getPlaylists()

        sleep(1)
        self.setStatus("Loading Liked Songs")
        library = self.SpotipyAPI.getSavedTracks()

        for playlist in playlists:
            name = playlist["name"]
            id = playlist["id"]
            tracks = playlist["tracks"]
            uid = PlaylistID(name, id)

            self.TDATA.insert("", uid, f"{name}", ["OK"])
            for i, trackinfo in enumerate(tracks):
                display = f"{trackinfo['name']} - {trackinfo['artist']}"
                self.TDATA.insert(
                    uid,
                    TrackID(
                        uid,
                        trackinfo["name"],
                        trackinfo["album"],
                        trackinfo["artist"],
                        trackinfo["id"],
                    ),
                    f"{display}",
                    ["OK"],
                )
                track_count += 1

        for i, trackinfo in enumerate(library):
            display = f"{trackinfo['name']} - {trackinfo['artist']}"
            self.TDATA.insert(
                LIBRARY_UID,
                TrackID(
                    LIBRARY_UID,
                    trackinfo["name"],
                    trackinfo["album"],
                    trackinfo["artist"],
                    trackinfo["id"],
                ),
                f"{display}",
                ["OK"],
            )
            track_count += 1
        self.updateElement("tree", values=self.TDATA)
        self.setStatus(f"Retrieved {track_count} tracks.")


    def refresh(self):
        self.window.refresh()

    def setStatus(self, msg: str):
        self.window["status"].update(msg)
        self.window.refresh()

    def updateElement(self, e, *args, **kwargs):
        self.window[e].update(*args, **kwargs)


    def _findPlaylistTracks(self, playlist_uid):
        """Yield tracks from the specified playlist."""
        for entry in self.TDATA.tree_dict.keys():
            if isinstance(entry, TrackID):
                if entry.playlist == playlist_uid:
                    yield entry


    def getGUIPlaylists(self):
        """Yield all playlists."""
        for entry in self.TDATA.tree_dict.keys():
            if isinstance(entry, PlaylistID) and entry != LIBRARY_UID:
                yield entry


    def beginExport(self, opts: dict):
        self.setStatus("Exporting songs.")

        time_info = datetime.now()
        save_data = {
            "file_signature": f'{self.SpotipyAPI.display_name}_{str(time_info)}',
            "library": None,
            "playlists": None,
        }

        
        save_data["library"] = []
        for i, track in enumerate(self._findPlaylistTracks(LIBRARY_UID)):
            save_data["library"].append(
                {
                    "pos": i + 1,
                    "name": track.name,
                    "album": track.album,
                    "artist": track.artist,
                    "id": track.id,
                }
            )

        for playlist in self.getGUIPlaylists():
            if save_data["playlists"] == None:
                save_data["playlists"] = {}
            save_data["playlists"][playlist.name] = {
                "id": playlist.id,
                "tracks": [],
            }
            
            for i, track in enumerate(self._findPlaylistTracks(playlist)):
                save_data["playlists"][playlist.name]["tracks"].append(
                    {
                        "pos": i + 1,
                        "name": track.name,
                        "album": track.album,
                        "artist": track.artist,
                        "id": track.id,
                    }
                )

        save_data = json.dumps(save_data, indent=(4)).encode()

        savef = open(opts["file"], "wb")
        savef.write(save_data)
        savef.flush()
        savef.close()
        self.setStatus("Saved successfully")

    def handle(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break

            if event == "new_account":
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=True)
                self.setStatus("Making a new_account account")
                self.newAddAccount()
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=False)
                self.setStatus("")

            if event == "account_selection":
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=True)
                try:
                    client_id = values["accounts"].split(" ", 1)[
                        0
                    ]  # Filter out name if present
                    self.setStatus(f"Connecting to account {client_id}")
                    self.SpotipyAPI = self.backend(client_id)
                except Exception as ex:
                    sg.popup_error_with_traceback("Error with backend:", ex)
                    break

                self.updateElement(
                    "accounts",
                    value=f"{values['accounts'][:6]}... - {self.SpotipyAPI.display_name}",
                )
                self.setStatus("Staring to pull the tracks.")
                self.loadTracklist()
                for element in self.UNFOCUS_TARGET:
                    self.updateElement(element, disabled=False)


            if event == "save_to":
                for element in self.UNFOCUS_TARGET:
                    self.window[element].update(disabled=True)

                self.setStatus("Starting save process")
                wizard = ExportPopUp()
                opts = wizard.start()

                # Do the save_to here...
                self.beginExport(opts)

                for element in self.UNFOCUS_TARGET:
                    self.window[element].update(disabled=False)

        self.window.close()


if __name__ == "__main__":
    MainGUI()
