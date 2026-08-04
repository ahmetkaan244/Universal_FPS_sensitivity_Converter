"""
sens_cli - Evrensel FPS Sens Çevirici
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Açık kaynak CLI aracı. Oyunlar arası fare hassasiyeti dönüşümü
yapar. Merkezinde cm/360 evrensel fiziksel ölçü birimi bulunur.

Kullanım:
    sens-cli convert --source cs2 --sens 1.2 --dpi 800 --target pubg
"""

__version__ = "3.0.0"
__author__ = "GameSens Generator Contributors"

from . import cli, constants, core, scopes
