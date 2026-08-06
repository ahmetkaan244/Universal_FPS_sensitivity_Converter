"""
test_constants.py
~~~~~~~~~~~~~~~~~
constants.py oyun veritabani tutarliligi testleri.
"""

from __future__ import annotations

import pytest

from sens_cli.constants import GAMES, get_game, list_games


class TestGameDatabase:
    """GAMES veritabani yapisal tutarlilik."""

    def test_eighteen_games_supported(self):
        assert set(GAMES.keys()) == {
            "cs2", "valorant", "pubg", "arena_breakout",
            "apex_legends", "overwatch_2", "call_of_duty_serisi", "the_finals",
            "marvel_rivals", "deadlock", "rainbow_six_siege", "fortnite",
            "battlefield_2042", "halo_infinite", "destiny_2",
            "escape_from_tarkov", "rust", "team_fortress_2",
        }

    def test_all_games_listable(self):
        games = list_games()
        assert len(games) == 18
        assert games == sorted(games)

    def test_cs2_yaw_matches_source_engine(self):
        assert get_game("cs2").yaw == 0.022

    def test_valorant_yaw_matches_ue4(self):
        assert get_game("valorant").yaw == 0.07

    @pytest.mark.parametrize(
        "key,expected_yaw",
        [
            ("apex_legends", 0.022),
            ("overwatch_2", 0.0066),
            ("call_of_duty_serisi", 0.0066),
            ("the_finals", 0.0066),
            ("marvel_rivals", 0.0066),
            ("deadlock", 0.044),
            ("rainbow_six_siege", 0.00573),
            ("fortnite", 0.005555),
            ("battlefield_2042", 0.0066),
            ("halo_infinite", 0.022),
            ("destiny_2", 0.0066),
            ("escape_from_tarkov", 0.125),
            ("rust", 0.222),
            ("team_fortress_2", 0.022),
        ],
    )
    def test_new_game_yaw_values(self, key, expected_yaw):
        assert get_game(key).yaw == pytest.approx(expected_yaw)

    def test_every_game_has_scopes(self):
        for key, game in GAMES.items():
            assert len(game.scopes) >= 1, f"{key} durbunsuz"

    def test_every_scope_has_unique_id(self):
        for key, game in GAMES.items():
            ids = [s.id for s in game.scopes]
            assert len(ids) == len(set(ids)), f"{key} tekrarlanan durbun id"

    def test_every_scope_fov_positive(self):
        for game in GAMES.values():
            for scope in game.scopes:
                assert scope.fov > 0

    def test_scope_fov_less_than_hipfire(self):
        # Durbun FOV'u her zaman ana FOV'dan kucuk olmali
        for game in GAMES.values():
            for scope in game.scopes:
                assert scope.fov < game.hipfire_fov

    def test_sens_min_max_valid(self):
        for game in GAMES.values():
            assert 0 < game.sens_min < game.sens_max

    def test_pubg_uses_slider_scale(self):
        assert get_game("pubg").sens_scale == "pubg_100"

    def test_linear_games_pass_through(self):
        for key in ("cs2", "valorant", "arena_breakout"):
            game = get_game(key)
            assert game.sens_to_internal(1.5) == 1.5
            assert game.internal_to_sens(1.5) == 1.5

    def test_pubg_slider_mapping_roundtrip(self):
        game = get_game("pubg")
        internal = game.sens_to_internal(50.0)
        assert game.internal_to_sens(internal) == pytest.approx(50.0, abs=0.1)

    def test_get_game_case_insensitive(self):
        assert get_game("CS2") == get_game("cs2")

    def test_get_game_unknown_raises(self):
        with pytest.raises(KeyError):
            get_game("tetris")
