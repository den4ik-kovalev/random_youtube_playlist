from typing import Optional

from storage import Storage

from pytube import Playlist


class YouTube:

    def __init__(self, storage: Storage, is_available: Optional[bool] = None):
        self._storage = storage
        self._is_available = is_available

    def get_playlist_videos_ids(self, playlist_url: str) -> list[str]:

        if self._is_available is None:
            self._is_available = self._check_youtube_connection(playlist_url)

        if self._is_available:
            playlist = Playlist(playlist_url)
            return [v.video_id for v in playlist.videos]
        else:
            return self._storage.playlist_url_2_videos_ids.get(playlist_url, [])

    def create_cache_file(self) -> None:

        playlist_urls = list(self._storage.playlist_2_url.values())
        if not playlist_urls:
            return

        if self._is_available is None:
            self._is_available = self._check_youtube_connection(playlist_urls[0])

        if not self._is_available:
            return

        data = {}
        for playlist_url in playlist_urls:
            playlist = Playlist(playlist_url)
            data[playlist_url] = [v.video_id for v in playlist.videos]

        self._storage.cache_file.write(data)

    @staticmethod
    def _check_youtube_connection(playlist_url: str) -> bool:
        try:
            playlist = Playlist(playlist_url)
            _ = list(playlist.videos)
        except Exception:
            return False
        else:
            return True
