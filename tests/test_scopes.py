"""
test_scopes.py
~~~~~~~~~~~~~~
scopes.py MDM dürbün hesaplama motoru için testler.
"""

from __future__ import annotations

import pytest

from sens_cli.scopes import (
    calculate_scopes,
    calculate_single_scope,
    _mdm_multiplier,
)


class TestMdmMultiplier:
    """_mdm_multiplier: FOV oranindan MDM carpani."""

    def test_same_fov_returns_one(self):
        # Ayni FOV -> carpan 1.0
        assert _mdm_multiplier(90.0, 90.0) == pytest.approx(1.0, abs=1e-6)

    def test_smaller_scope_fov_reduces_sens(self):
        # Durbun FOV'u kuculurse sens yavaslamali (< 1.0)
        multiplier = _mdm_multiplier(106.26, 51.0)
        assert multiplier < 1.0

    def test_zero_percent_matches_focal_length(self):
        # %0 MDM = focal length scaling
        m0 = _mdm_multiplier(106.26, 51.0, match_pct=0.0)
        hip_rad = 106.26 * 3.141592653589793 / 180.0
        scope_rad = 51.0 * 3.141592653589793 / 180.0
        expected = __import__("math").tan(scope_rad / 2) / __import__("math").tan(hip_rad / 2)
        assert m0 == pytest.approx(expected, abs=1e-6)

    def test_higher_match_pct_changes_multiplier(self):
        # Farkli esleme yuzdesi farkli carpan uretir
        m0 = _mdm_multiplier(106.26, 51.0, match_pct=0.0)
        m100 = _mdm_multiplier(106.26, 51.0, match_pct=100.0)
        assert m0 != pytest.approx(m100, abs=1e-6)

    def test_known_verified_values(self):
        # mouse-sensitivity.com kanonik formulu ile dogrulanmis degerler
        # hipfire=106.26 hdeg, scope=51 hdeg
        m0 = _mdm_multiplier(106.26, 51.0, match_pct=0.0)
        m50 = _mdm_multiplier(106.26, 51.0, match_pct=50.0)
        m100 = _mdm_multiplier(106.26, 51.0, match_pct=100.0)
        assert m0 == pytest.approx(0.3577, abs=1e-4)
        assert m50 == pytest.approx(0.3982, abs=1e-4)
        assert m100 == pytest.approx(0.4800, abs=1e-4)

    def test_100_pct_equals_radian_ratio(self):
        # 100% MDM = scope_fov_rad / hipfire_fov_rad (basitlestirilmis hali)
        m100 = _mdm_multiplier(106.26, 51.0, match_pct=100.0)
        ratio = (51.0 * 3.141592653589793 / 180.0) / (106.26 * 3.141592653589793 / 180.0)
        assert m100 == pytest.approx(ratio, abs=1e-6)

    def test_monotonic_increasing_with_pct(self):
        # Carpan, yuzde ile monotonik artmali (0% -> 100%)
        values = [
            _mdm_multiplier(106.26, 51.0, match_pct=p)
            for p in (0.0, 25.0, 50.0, 75.0, 100.0)
        ]
        assert values == sorted(values)

    def test_pubg_8x_small_fov_edge_case(self):
        # PUBG 8x: hipfire 90d, scope 11d - kucuk FOV kenar durumu
        m0 = _mdm_multiplier(90.0, 11.0, match_pct=0.0)
        m100 = _mdm_multiplier(90.0, 11.0, match_pct=100.0)
        assert m0 == pytest.approx(0.0963, abs=1e-4)
        assert m100 == pytest.approx(0.1222, abs=1e-4)
        assert m0 < m100  # 100% durbunlu hiz daha yuksek olmali

    def test_extreme_percent_values(self):
        # %1 gibi cok kucuk yuzde: carpan hala gecerli aralikta
        m1 = _mdm_multiplier(90.0, 11.0, match_pct=1.0)
        m0 = _mdm_multiplier(90.0, 11.0, match_pct=0.0)
        assert 0 < m1 < 1.0
        # %1, %0'dan buyuk olmali (monotoniklik)
        assert m1 > m0


class TestCalculateScopes:
    """calculate_scopes: hedef oyunun tum durbunlerini hesaplar."""

    def test_pubg_has_all_six_scopes(self):
        scopes = calculate_scopes(42.5, "cs2", "pubg", 0.0)
        assert set(scopes.keys()) == {"ads", "2x", "3x", "4x", "6x", "8x"}

    def test_scope_sens_monotonic_decreasing(self):
        # Zoom arttikca (FOV azaldikca) sens azalmali
        scopes = calculate_scopes(42.5, "cs2", "pubg", 0.0)
        fovs = [s["fov"] for s in scopes.values()]
        sens = [s["sens"] for s in scopes.values()]
        # FOV artan sirada, sens azalan sirada olmali
        assert fovs == sorted(fovs, reverse=True)
        assert sens == sorted(sens, reverse=True)

    def test_ads_sens_less_than_base(self):
        # Durbunlu hiz, ana hizdan yavas olmali
        scopes = calculate_scopes(42.5, "cs2", "pubg", 0.0)
        for data in scopes.values():
            assert data["sens"] < 42.5

    def test_scope_names_present(self):
        scopes = calculate_scopes(42.5, "cs2", "pubg", 0.0)
        assert scopes["2x"]["name"] == "2x Dürbün"
        assert scopes["ads"]["name"] == "ADS (Lazer/Holo)"

    def test_mdm_percentage_changes_results(self):
        s0 = calculate_scopes(42.5, "cs2", "pubg", 0.0)
        s100 = calculate_scopes(42.5, "cs2", "pubg", 100.0)
        assert s0["2x"]["sens"] != s100["2x"]["sens"]

    def test_valorant_two_scopes(self):
        scopes = calculate_scopes(0.314, "cs2", "valorant", 0.0)
        assert set(scopes.keys()) == {"ads", "sniper"}

    def test_invalid_target_game_raises(self):
        with pytest.raises(KeyError):
            calculate_scopes(42.5, "cs2", "minecraft", 0.0)


class TestCalculateSingleScope:
    """calculate_single_scope: secili durbun -> hedef oyun durbunu."""

    def test_pubg_ads_to_cs2_zoom(self):
        # PUBG'de ADS durbunu -> CS2 zoom'a donustur
        sens = calculate_single_scope(40.0, "pubg", "cs2", "ads", 0.0)
        assert sens > 0
        assert isinstance(sens, float)

    def test_unknown_scope_raises(self):
        with pytest.raises(KeyError):
            calculate_single_scope(40.0, "pubg", "cs2", "9x", 0.0)
