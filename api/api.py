# stolen from https://spotipy.readthedocs.io/, merci!

# system + builtin
from time import sleep
from spotipy.oauth2 import SpotifyOAuth, SpotifyPKCE
import spotipy


class SpotipyAPI:
    SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"
    DEF_SCOPES = (
        "user-modify-playback-state",
        "user-library-read",
        "user-library-modify",
        "playlist-modify-private",
        "playlist-read-private",
        "playlist-modify-public",
    )

    def __init__(self, client_id: str, redirect_uri=SPOTIPY_REDIRECT_URI) -> None:
        self.client_id = client_id
        self.auth_manager = SpotifyPKCE(
            client_id=self.client_id,
            redirect_uri=redirect_uri,
            scope=" ".join(self.DEF_SCOPES),
        )
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

        # Trigger auth
        self.usercache = self.spotify.me()

    def __repr__(self):
        return f'<SpotipyAPI user="{self.display_name}">'

    @property
    def display_name(self) -> str:
        return self.usercache["display_name"]

    @property
    def id(self) -> str:
        return self.usercache["id"]

    @property
    def user_url(self) -> str:
        return self.usercache["external_urls"]["spotify"]

    @property
    def user_followers(self) -> int:
        return self.usercache["followers"]["total"]

    @property
    def user_picture(self) -> str:
        return self.usercache["images"][0]["url"]

    def getPagedItem(self, func, **kwargs):
        offset = 0
        data = func(**kwargs)

        while len(data["items"]) != 0:
            yield from data["items"]

            offset += len(data["items"])
            data = func(**kwargs, offset=offset)

    def getArtists(self, track: list, sep=", ") -> str:
        return sep.join(artist["name"] for artist in track["artists"])

    def track_yield(self, src: dict) -> dict:
        for track in src:
            id_ = track["track"]["id"]
            name = track["track"]["name"]
            album = track["track"]["album"]["name"]
            artist = self.getArtists(track["track"])

            yield {"id": id_, "name": name, "album": album, "artist": artist}

    def iterPlaylists(self, *, limit: int = 1):
        for playlist in self.getPagedItem(
            self.spotify.current_user_playlists, limit=limit
        ):
            name = playlist["name"]
            id_ = playlist["id"]
            tracks = self.iterPlaylistTracks(id_)

            yield {"name": name, "id": id_, "tracks": tracks}

    def iterPlaylistNames(self):
        yield from (
            playlist["name"]
            for playlist in self.getPagedItem(
                self.spotify.current_user_playlists, limit=1
            )
        )

    def iterPlaylistTracks(self, playlist_id: str, *, limit: int = 1):
        getter = self.getPagedItem(
            self.spotify.user_playlist_tracks, playlist_id=playlist_id, limit=limit
        )
        yield from self.track_yield(getter)

    def getPlaylistTracks(self, playlist_id: str) -> tuple:
        results = list()
        for result in self.iterPlaylistTracks(playlist_id, limit=100):
            results.append(result)
        return tuple(results)

    def getPlaylists(self, delay: int = 1) -> tuple:
        playlists = list()
        for playlist in self.iterPlaylists(limit=50):
            playlist["tracks"] = self.getPlaylistTracks(playlist["id"])
            playlists.append(playlist)
            sleep(delay)
        return tuple(playlists)

    def getPlaylistNames(self):
        return tuple(self.iterPlaylistNames())

    def getPlaylistID(self, playlist_name):
        for playlist in self.iterPlaylists(limit=50):
            if playlist["name"] == playlist_name:
                return playlist["id"]
        raise Exception("Could not find playlist")

    def iterSavedTracks(self, *, limit: int = 1):
        getter = self.getPagedItem(self.spotify.current_user_saved_tracks, limit=limit)
        yield from self.track_yield(getter)

    def getSavedTracks(self) -> tuple:
        tracks = list()
        for track in self.iterSavedTracks(limit=20):
            tracks.append(track)
        return tuple(tracks)
