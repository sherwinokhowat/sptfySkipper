import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_artists_to_avoid(path: str) -> list[str]:
    with open(path, "r") as file:
        return [line.lower().strip() for line in file]
    
def is_artist(playback: dict, artists_to_avoid: list[str]) -> bool:
    artists = playback.get("item", {}).get("artists")

    if not artists:
        return False
    
    for artist in artists:
        name = artist.get("name", "")
        if str.lower(name).strip() in artists_to_avoid:
            return True
        
    return False
    
def get_spotify_client() -> spotipy.Spotify:
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri= os.getenv("REDIRECT_URI")
    scope = "user-read-currently-playing user-read-playback-state streaming"

    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)
    token = sp_oauth.get_access_token(as_dict=False)

    return spotipy.Spotify(auth=token)

def check_and_skip_track(sp: spotipy.Spotify, artists_to_avoid: list[str]):
    try:
        playback = sp.current_playback()
        if playback and is_artist(playback, artists_to_avoid):
            sp.next_track()
    except spotipy.exceptions.SpotifyException as e:
        print(f"An error orccurred: {e}")


if __name__ == "__main__":
    artists_to_avoid = get_artists_to_avoid("artists.txt")

    if not artists_to_avoid:
        print("No artists were loaded.")
        exit(0)

    sp = get_spotify_client()

    while True:
        check_and_skip_track(sp, artists_to_avoid)
        time.sleep(5)
