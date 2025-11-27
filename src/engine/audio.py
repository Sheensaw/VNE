from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PySide6.QtCore import QUrl
from src.common.paths import get_assets_path
import os


class AudioManager:
    """
    Gère la musique de fond (streaming) et les effets sonores (chargés en mémoire).
    """

    def __init__(self):
        # Musique (BGM)
        self.music_player = QMediaPlayer()
        self.music_output = QAudioOutput()
        self.music_player.setAudioOutput(self.music_output)
        self.music_output.setVolume(0.5)  # 50% par défaut

        self.current_music_file = None

        # Sound Effects (SFX)
        self.sfx_cache = {}  # Cache pour éviter de recharger

    def play_music(self, filename: str):
        """Joue une musique en boucle. Ne redémarre pas si c'est la même."""
        if not filename:
            self.music_player.stop()
            return

        if filename == self.current_music_file and self.music_player.playbackState() == QMediaPlayer.PlayingState:
            return

        full_path = get_assets_path() / filename
        if not os.path.exists(full_path):
            print(f"[Audio] Fichier manquant: {full_path}")
            return

        self.current_music_file = filename
        self.music_player.setSource(QUrl.fromLocalFile(str(full_path)))
        self.music_player.setLoops(QMediaPlayer.Infinite)
        self.music_player.play()

    def play_sfx(self, filename: str):
        """Joue un effet sonore (one-shot)."""
        if not filename:
            return

        if filename not in self.sfx_cache:
            full_path = get_assets_path() / filename
            if not os.path.exists(full_path):
                return
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(str(full_path)))
            self.sfx_cache[filename] = effect

        self.sfx_cache[filename].play()