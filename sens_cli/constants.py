"""
sens_cli.constants
~~~~~~~~~~~~~~~~~~
Evrensel FPS Sens Çevirici - Oyun Sabitleri

Her oyunun yaw (derece/mouse-count), varsayılan FOV ve dürbün/scope
tanımlarını içerir.

NOT: Yaw değerleri topluluk tarafından doğrulanmış kaynaklardan
derlenmiştir. Yeni oyun eklemek için bu dosyaya bir satır eklemek
yeterlidir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ScopeDef:
    """Bir dürbün/zoom seviyesinin tanımı."""
    id: str                     # Makine okuması için kısa kod (ör: "2x", "ads")
    name: str                   # İnsan okuması için görünen ad (ör: "2x Dürbün")
    fov: float                  # Bu dürbünle yatay görüş açısı (16:9, derece)


@dataclass
class GameDef:
    """Bir oyunun tüm hassasiyet parametreleri."""
    name: str                   # Görünen ad
    yaw: float                  # Yaw sabiti (derece/count)
    hipfire_fov: float          # Varsayılan yatay görüş açısı (16:9, derece)
    scopes: list[ScopeDef]      # Desteklenen dürbün/zoom tipleri
    sens_min: float = 0.1       # Minimum hassasiyet değeri
    sens_max: float = 100.0     # Maksimum hassasiyet değeri
    sens_scale: Literal["linear", "pubg_100"] = "linear"
    # "linear"  → CS2/Valorant tipi: sens değeri doğrudan çarpana dönüşür
    # "pubg_100" → PUBG tipi: 1-100 arası slider, içsel skalaya dönüşüm gerekir

    def sens_to_internal(self, slider_value: float) -> float:
        """Oyunun slider/hassasiyet değerini içsel çarpana dönüştürür.

        "linear" oyunlarda slider değeri aynen kullanılır.
        "pubg_100" oyunlarda 1-100 skalası içsel bir doğrusal skalaya
        haritalanır (topluluk tarafından kalibre edilmelidir).
        """
        if self.sens_scale == "pubg_100":
            # PUBG'de slider 1-100 arasıdır; içsel çarpan yaklaşık
            # slider / PUBG_SENS_DIVISOR kadardır.
            return slider_value / self._pubg_divisor
        return slider_value

    def internal_to_sens(self, internal_value: float) -> float:
        """İçsel çarpanı oyunun slider değerine dönüştürür."""
        if self.sens_scale == "pubg_100":
            return round(internal_value * self._pubg_divisor, 3)
        return round(internal_value, 3)


# ═══════════════════════════════════════════════════════════════
#  GAME DATABASE
#  Yeni oyun eklemek için bu sözlüğe bir girdi ekleyin.
#  Yaw değerleri, mouse-sensitivity.com ve topluluk kaynakları
#  temel alınarak derlenmiştir.
# ═══════════════════════════════════════════════════════════════

GAMES: dict[str, GameDef] = {
    "cs2": GameDef(
        name="Counter-Strike 2",
        yaw=0.022,
        hipfire_fov=106.26,
        sens_min=0.1,
        sens_max=10,
        scopes=[
            ScopeDef(id="zoom", name="Zoom (AWP/Krieg)", fov=51.0),
        ],
    ),

    "valorant": GameDef(
        name="Valorant",
        yaw=0.07,
        hipfire_fov=103.0,
        sens_min=0.01,
        sens_max=20,
        scopes=[
            ScopeDef(id="ads", name="ADS (Vandal/Phantom)", fov=58.0),
            ScopeDef(id="sniper", name="Keskin Nişancı (Operator)", fov=34.0),
        ],
    ),

    "pubg": GameDef(
        name="PUBG: Battlegrounds",
        yaw=0.0055,
        hipfire_fov=90.0,
        sens_min=1,
        sens_max=100,
        sens_scale="pubg_100",
        scopes=[
            ScopeDef(id="ads", name="ADS (Lazer/Holo)", fov=67.0),
            ScopeDef(id="2x", name="2x Dürbün", fov=45.0),
            ScopeDef(id="3x", name="3x Dürbün", fov=34.0),
            ScopeDef(id="4x", name="4x Dürbün", fov=22.0),
            ScopeDef(id="6x", name="6x Dürbün", fov=15.0),
            ScopeDef(id="8x", name="8x Dürbün", fov=11.0),
        ],
    ),

    "arena_breakout": GameDef(
        name="Arena Breakout",
        yaw=0.011,
        hipfire_fov=80.0,
        sens_min=0.1,
        sens_max=4.0,
        sens_scale="linear",
        scopes=[
            ScopeDef(id="1x", name="1x (Kırmızı Nokta/Holo)", fov=65.0),
            ScopeDef(id="2x", name="2x Dürbün", fov=45.0),
            ScopeDef(id="3.5x", name="3.5x Dürbün", fov=30.0),
            ScopeDef(id="4x", name="4x Dürbün", fov=24.0),
        ],
    ),
}

# PUBG için içsel çarpan dönüşüm sabiti
# Kalibrasyon: CS2 sens=1.2, DPI=800 → cm/360=43.3 → PUBG slider=42.5
# Formül: divisor = slider / internal_sens = 42.5 / 4.80 ≈ 8.85
# Geliştiriciler: PR ile güncelleyin.
GameDef._pubg_divisor = 8.85


def get_game(game_key: str) -> GameDef:
    """Oyun tanımını döndürür. Bulunamazsa KeyError fırlatır."""
    game = GAMES.get(game_key.lower())
    if game is None:
        available = ", ".join(sorted(GAMES))
        raise KeyError(
            f"'{game_key}' desteklenmiyor. Mevcut oyunlar: {available}"
        )
    return game


def list_games() -> list[str]:
    """Tüm desteklenen oyun anahtarlarını döndürür."""
    return sorted(GAMES.keys())
