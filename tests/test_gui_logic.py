"""
test_gui_logic.py
~~~~~~~~~~~~~~~~~~
gui.py içinden soyutlanan saf (pure) fonksiyonların testleri.

Bu testler GUI widget'larına dokunmaz — yalnızca gui modülündeki
tkinter bağımsız yardımcı fonksiyonları doğrular.
"""

from __future__ import annotations

import pytest

from sens_cli.constants import get_game

from gui import (
    build_game_info,
    build_game_table,
    build_result_text,
    get_scope_id_from_name,
    validate_and_parse,
)


class TestValidateAndParse:
    """validate_and_parse: ham metin girdilerini doğrular."""

    def test_valid_inputs(self):
        sens, dpi, tdpi = validate_and_parse("1.2", "800", "", get_game("cs2"))
        assert sens == pytest.approx(1.2)
        assert dpi == 800
        assert tdpi is None

    def test_comma_decimal_supported(self):
        sens, _, _ = validate_and_parse("1,5", "800", "", get_game("cs2"))
        assert sens == pytest.approx(1.5)

    def test_optional_target_dpi(self):
        _, _, tdpi = validate_and_parse("1.0", "800", "1600", get_game("cs2"))
        assert tdpi == 1600

    def test_invalid_sens_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("abc", "800", "", get_game("cs2"))

    def test_zero_sens_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("0", "800", "", get_game("cs2"))

    def test_negative_sens_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("-2", "800", "", get_game("cs2"))

    def test_invalid_dpi_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("1.0", "seksen", "", get_game("cs2"))

    def test_zero_dpi_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("1.0", "0", "", get_game("cs2"))

    def test_invalid_target_dpi_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("1.0", "800", "abc", get_game("cs2"))

    def test_zero_target_dpi_raises(self):
        with pytest.raises(ValueError):
            validate_and_parse("1.0", "800", "0", get_game("cs2"))


class TestBuildResultText:
    """build_result_text: biçimlendirilmiş sonuç metni üretir."""

    def test_contains_key_sections(self):
        scopes = {"ads": {"name": "ADS", "sens": 5.0, "fov": 67.0}}
        text = build_result_text(
            cm360=43.29,
            src_name="Counter-Strike 2",
            tgt_name="PUBG: Battlegrounds",
            src_yaw=0.022,
            tgt_yaw=0.0055,
            dpi_label="800",
            target_sens=42.5,
            scopes=scopes,
            mdm=0,
        )
        assert "43.29" in text
        assert "42.5" in text
        assert "Counter-Strike 2" in text
        assert "PUBG: Battlegrounds" in text
        assert "ADS" in text

    def test_no_scopes_still_formats(self):
        text = build_result_text(
            cm360=51.95,
            src_name="Counter-Strike 2",
            tgt_name="Counter-Strike 2",
            src_yaw=0.022,
            tgt_yaw=0.022,
            dpi_label="800",
            target_sens=1.5,
            scopes={},
            mdm=0,
        )
        assert "51.95" in text
        assert "1.5" in text

    def test_scope_note_included_when_present(self):
        text = build_result_text(
            cm360=43.29,
            src_name="A",
            tgt_name="B",
            src_yaw=0.022,
            tgt_yaw=0.011,
            dpi_label="800",
            target_sens=2.0,
            scopes={},
            mdm=0,
            scope_note="Kaynak durbun: 4x",
        )
        assert "Kaynak durbun: 4x" in text


class TestBuildGameTable:
    """build_game_table: CLI `list` ile aynı tabloyu üretir."""

    def test_contains_all_four_games(self):
        table = build_game_table()
        assert "cs2" in table
        assert "valorant" in table
        assert "pubg" in table
        assert "arena_breakout" in table

    def test_contains_names(self):
        table = build_game_table()
        assert "Counter-Strike 2" in table
        assert "PUBG: Battlegrounds" in table


class TestBuildGameInfo:
    """build_game_info: CLI `info` ile aynı detayları üretir."""

    def test_cs2_info(self):
        info = build_game_info("cs2")
        assert "0.022" in info          # yaw
        assert "106.26" in info         # hipfire FOV
        assert "Zoom" in info           # dürbün adı

    def test_pubg_scope_listing(self):
        info = build_game_info("pubg")
        assert "8x Dürbün" in info or "8x Durbun" in info
        assert "pubg_100" in info

    def test_invalid_game_raises(self):
        with pytest.raises(KeyError):
            build_game_info("minecraft")


class TestGetScopeIdFromName:
    """get_scope_id_from_name: görünen dürbün adından id bulur."""

    def test_exact_match(self):
        assert get_scope_id_from_name("pubg", "4x Dürbün") == "4x"
        assert get_scope_id_from_name("pubg", "4x Durbun") == "4x"

    def test_none_when_missing(self):
        assert get_scope_id_from_name("pubg", "12x Dürbün") is None

    def test_none_for_invalid_game(self):
        assert get_scope_id_from_name("minecraft", "ads") is None
