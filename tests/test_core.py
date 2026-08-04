"""
test_core.py
~~~~~~~~~~~~
core.py dönüşüm motoru için karakterizasyon testleri.

Beklenen değerler bağımsız kaynaklardan doğrulanmıştır:
- senslab.pro / cpsmeter.com: CS2 yaw=0.022, Valorant yaw=0.07
- sensai.games: Valorant 0.4 @ 800 DPI → CS2 1.2727, cm/360=40.82
- senslab.pro: CS2 2.0 @ 800 DPI → Valorant 0.6286
"""

from __future__ import annotations

import pytest

from sens_cli.core import (
    sens_to_cm360,
    cm360_to_sens,
    convert_sensitivity,
)


class TestSensToCm360:
    """sens_to_cm360: oyun içi hassasiyet → fiziksel mesafe."""

    @pytest.mark.parametrize(
        "sens,dpi,game,expected",
        [
            (1.0, 800, "cs2", 51.95),          # cpsmeter: ~52.0 cm
            (0.4, 800, "valorant", 40.82),     # sensai.games: 40.82 cm
            (1.2, 800, "cs2", 43.29),          # plan dokumani: 43.2
        ],
    )
    def test_known_values(self, sens, dpi, game, expected):
        assert sens_to_cm360(sens, dpi, game) == pytest.approx(expected, abs=0.05)

    def test_pubg_uses_slider_scale(self):
        # PUBG 42.5 slider, CS2 1.2@800 ile ayni cm/360 vermeli (43.2)
        cm_cs2 = sens_to_cm360(1.2, 800, "cs2")
        cm_pubg = sens_to_cm360(42.5, 800, "pubg")
        assert cm_cs2 == pytest.approx(cm_pubg, abs=0.5)

    def test_invalid_game_raises(self):
        with pytest.raises(KeyError):
            sens_to_cm360(1.0, 800, "minecraft")

    def test_zero_dpi_raises(self):
        with pytest.raises(ZeroDivisionError):
            sens_to_cm360(1.0, 0, "cs2")


class TestCm360ToSens:
    """cm360_to_sens: fiziksel mesafe → oyun içi hassasiyet."""

    @pytest.mark.parametrize(
        "cm360,dpi,game,expected",
        [
            (51.95, 800, "valorant", 0.314),   # CS2 1.0@800 esdegeri
            (40.82, 800, "cs2", 1.273),        # sensai: 1.2727
            (43.29, 800, "pubg", 42.5),        # plan dokumani: 42.5
        ],
    )
    def test_known_values(self, cm360, dpi, game, expected):
        assert cm360_to_sens(cm360, dpi, game) == pytest.approx(expected, abs=0.05)


class TestConvertSensitivity:
    """convert_sensitivity: uçtan uca dönüşüm."""

    def test_cs2_to_valorant_known_ratio(self):
        # Bilinen donusum orani: val = cs2 * 0.022/0.07 = cs2 * 0.3143
        cm360, val_sens = convert_sensitivity(2.0, 800, "cs2", "valorant")
        assert cm360 == pytest.approx(25.98, abs=0.05)
        assert val_sens == pytest.approx(0.6286, abs=0.01)  # senslab: 0.6286

    def test_valorant_to_cs2_known_ratio(self):
        # Bilinen donusum orani: cs2 = val * 0.07/0.022 = val * 3.1818
        cm360, cs2_sens = convert_sensitivity(0.4, 800, "valorant", "cs2")
        assert cm360 == pytest.approx(40.82, abs=0.05)
        assert cs2_sens == pytest.approx(1.273, abs=0.01)  # sensai: 1.2727

    def test_round_trip_preserves_sens(self):
        # CS2 1.2 -> PUBG 42.48 -> geri CS2 = 1.2
        _, pubg_sens = convert_sensitivity(1.2, 800, "cs2", "pubg")
        _, back_cs2 = convert_sensitivity(pubg_sens, 800, "pubg", "cs2")
        assert back_cs2 == pytest.approx(1.2, abs=0.05)

    def test_round_trip_cs2_valorant(self):
        _, val_sens = convert_sensitivity(1.0, 800, "cs2", "valorant")
        _, back_cs2 = convert_sensitivity(val_sens, 800, "valorant", "cs2")
        assert back_cs2 == pytest.approx(1.0, abs=0.05)

    def test_target_dpi_different_from_source(self):
        # CS2 1.0@800 -> Valorant@1600: cm/360 ayni, sens yariya iner
        cm360, val_sens = convert_sensitivity(1.0, 800, "cs2", "valorant", target_dpi=1600)
        assert cm360 == pytest.approx(51.95, abs=0.05)
        assert val_sens == pytest.approx(0.157, abs=0.01)

    def test_same_game_passthrough(self):
        cm360, cs2_sens = convert_sensitivity(1.5, 800, "cs2", "cs2")
        assert cm360 == pytest.approx(34.64, abs=0.05)
        assert cs2_sens == pytest.approx(1.5, abs=0.01)
