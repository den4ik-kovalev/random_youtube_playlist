from __future__ import annotations

from pathlib import Path

from utils import YAMLFile


class Storage:

    root_dir_path = Path("data")

    def __init__(self, chat_id: int):
        self.root_dir_path.mkdir(exist_ok=True)
        self._chat_dir_path = self.root_dir_path / str(chat_id)
        self._chat_dir_path.mkdir(exist_ok=True)
        self._config_file = YAMLFile(self._chat_dir_path / "config.yml")
        self._cache_file = YAMLFile(self._chat_dir_path / "cache.yml")

    @property
    def config_file(self) -> YAMLFile:
        return self._config_file

    @property
    def cache_file(self) -> YAMLFile:
        return self._cache_file

    @property
    def playlist_2_url(self) -> dict[str, str]:
        """ {ПЛЕЙЛИСТ: ССЫЛКА} """
        return (self._config_file.read() or {}).get("urls", {})

    @property
    def mode_2_playlists(self) -> dict[str, list[str]]:
        """ {РЕЖИМ: [ПЛЕЙЛИСТ_1, ПЛЕЙЛИСТ_2]} """
        return (self._config_file.read() or {}).get("modes", {})

    @property
    def mode_2_urls(self) -> dict[str, list[str]]:
        """ {РЕЖИМ: [ССЫЛКА_1, ССЫЛКА_2]} """
        playlist_2_url = self.playlist_2_url
        mode_2_playlists = self.mode_2_playlists
        return {
            mode: [playlist_2_url[playlist] for playlist in playlists]
            for mode, playlists in mode_2_playlists.items()
        }

    @property
    def playlist_url_2_videos_ids(self) -> dict[str, list[str]]:
        """ {ССЫЛКА: [ВИДЕО_ID_1, ВИДЕО_ID_2]} """
        return self.cache_file.read() or {}
