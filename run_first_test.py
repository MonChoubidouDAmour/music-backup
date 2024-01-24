import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

# You should be able to make this file run after setting these 3 variables in
# your shell

# export SPOTIPY_CLIENT_ID='clind_id (find this first)'
# export SPOTIPY_CLIENT_SECRET='client_secret (under client_id)'
# export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback' (click on the blue edit button on the same page as the other 2)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])