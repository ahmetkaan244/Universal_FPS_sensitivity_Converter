"""
sens_cli.core
~~~~~~~~~~~~~
Evrensel cm/360 dönüşüm motoru.

Tüm oyunların hassasiyet değerleri önce evrensel fiziksel birime
(cm/360) çekilir, ardından hedef oyunun motor parametreleriyle
tekrar oyun içi değere dönüştürülür.
"""

from __future__ import annotations

import math

from .constants import GameDef, get_game


def sens_to_cm360(sens: float, dpi: int, game_key: str) -> float:
    """Oyun içi hassasiyet değerini cm/360'a çevirir.

    Formül:
        cm/360 = 360 / (sens * dpi * yaw) * 2.54

    Args:
        sens: Kaynak oyundaki hassasiyet değeri.
        dpi:  Farenin DPI değeri.
        game_key: Oyun anahtarı (ör: "cs2", "valorant").

    Returns:
        Fiziksel mesafe (santimetre cinsinden).
    """
    game = get_game(game_key)
    internal_sens = game.sens_to_internal(sens)
    yaw = game.yaw
    cm360 = 360.0 / (internal_sens * dpi * yaw) * 2.54
    return round(cm360, 2)


def cm360_to_sens(cm360: float, dpi: int, game_key: str) -> float:
    """cm/360 değerini hedef oyunun hassasiyet değerine çevirir.

    Formül:
        sens = 360 / ((cm360 / 2.54) * dpi * yaw)

    Args:
        cm360: Fiziksel mesafe (santimetre).
        dpi:   Farenin DPI değeri.
        game_key: Oyun anahtarı.

    Returns:
        Hedef oyundaki hassasiyet değeri.
    """
    game = get_game(game_key)
    yaw = game.yaw
    internal_sens = 360.0 / ((cm360 / 2.54) * dpi * yaw)
    return game.internal_to_sens(internal_sens)


def convert_sensitivity(
    source_sens: float,
    source_dpi: int,
    source_game: str,
    target_game: str,
    target_dpi: int | None = None,
) -> tuple[float, float]:
    """Kaynak oyundaki hassasiyeti hedef oyuna dönüştürür.

    İki adımlı dönüşüm:
        1. Kaynak değer → cm/360 (evrensel fiziksel birim)
        2. cm/360 → Hedef oyun değeri

    Args:
        source_sens: Kaynak oyundaki hassasiyet.
        source_dpi:  Kaynak oyundaki DPI.
        source_game: Kaynak oyun anahtarı.
        target_game: Hedef oyun anahtarı.
        target_dpi:  Hedef oyundaki DPI (None = source_dpi ile aynı).

    Returns:
        (cm360, target_sens) ikilisi.
    """
    tdpi = target_dpi if target_dpi is not None else source_dpi
    cm360 = sens_to_cm360(source_sens, source_dpi, source_game)
    target_sens = cm360_to_sens(cm360, tdpi, target_game)
    return cm360, target_sens
