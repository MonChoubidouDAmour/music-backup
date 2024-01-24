# Music Backup
This is a project that will create a `.json` with every single music in your playlists. This is basically going to immortalize your playlist in a `.json`

## Setting Up Spotify API Credentials

Before running the project, you need to set up your Spotify API credentials. Follow the steps below to export the necessary environment variables:

1. **Get Spotify API Credentials:**
   - Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Log in or create a new Spotify account if necessary.
   - Create a new application to obtain the client ID and client secret.

2. **Export Environment Variables:**
   Open your terminal and run the following commands to export the required environment variables. Replace 'client_id' and 'client_secret' with your actual Spotify API credentials.

    ```bash
    export SPOTIPY_CLIENT_ID='your_client_id'
    export SPOTIPY_CLIENT_SECRET='your_client_secret'
    export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
    ```

    Make sure to click on the blue edit button on the Spotify Developer Dashboard to set the redirect URI.

## Running the Project

Now that you have set up your Spotify API credentials, you can proceed to run the project as described in the previous section. If you encounter any issues related to authentication, ensure that your environment variables are correctly set and match the credentials provided by the Spotify Developer Dashboard.


1. **Clone the Repository:**
    ```bash
    git clone https://github.com/MonChoubidouDAmour/music-backup.git
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Test your environment**
    ```bash
    python run_first_test.py
    ```

If this doesn't work, please go over the setup again.

## Important Notes

- Make sure to update any configuration files or settings if required for the latest versions of dependencies. There shouldn't be any issues, but Spotify's api could change.
