"""
sens_cli.cli
~~~~~~~~~~~~
Argparse CLI arabirimi.

Kullanici dostu terminal deneyimi sunar:
  - Oyunlar arasi tek adimda donusum
  - Tum durkun degerlerinin MDM ile hesaplanmasi
  - Duzenli cikti
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .constants import GAMES, get_game, list_games
from .core import convert_sensitivity
from .scopes import calculate_scopes


def _fmt(val: bool) -> str:
    return "[+]" if val else "[-]"


def _run_convert(args: argparse.Namespace) -> None:
    """convert alt komutunu calistirir."""
    try:
        get_game(args.source)
        get_game(args.target)

        target_dpi = args.target_dpi or args.dpi

        cm360, target_sens = convert_sensitivity(
            source_sens=args.sens,
            source_dpi=args.dpi,
            source_game=args.source,
            target_game=args.target,
            target_dpi=target_dpi,
        )

        src_game = get_game(args.source)
        tgt_game = get_game(args.target)

        # Baslik
        print("=" * 55)
        print(f"  Evrensel FPS Sens Cevirici v{__version__}")
        print(f"  {src_game.name} -> {tgt_game.name}")
        print("=" * 55)

        # cm/360 bilgisi
        print(f"\n {_fmt(True)} Fiziksel Eslisme (cm/360): {cm360} cm")
        dpi_label = f"{args.dpi}"
        if args.target_dpi:
            dpi_label = f"{args.dpi} -> {target_dpi}"
        print(f"    DPI: {dpi_label}  |  Sens: {args.sens}")

        # Hedef oyun ana hassasiyeti
        print(f"\n {_fmt(True)} {tgt_game.name} Genel Hassasiyet: {target_sens}")

        # Durkun hesaplari
        scopes = calculate_scopes(
            base_sens=target_sens,
            source_game=args.source,
            target_game=args.target,
            match_pct=args.mdm,
        )

        if scopes:
            print(f"\n {_fmt(True)} {tgt_game.name} Durkun Ayarlari (MDM %{args.mdm} Eslame):")
            max_name_len = max(len(s["name"]) for s in scopes.values())
            for scope_id, data in scopes.items():
                name_padded = data["name"].ljust(max_name_len)
                sens_str = f"{data['sens']}"
                fov_str = f"{data['fov']}d"
                print(f"    - {name_padded} : {sens_str:>6}  (FOV: {fov_str})")

        # Not
        if args.source != args.target:
            print(f"\n {'[*]'} Ipucu: Donusum sonrasi nisan hissinizi "
                  f"antrenman modunda test edin.")
        print()

    except KeyError as e:
        print(f"\n {'[!]'} HATA: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n {'[!]'} Beklenmeyen hata: {e}", file=sys.stderr)
        sys.exit(2)


def _run_list(args: argparse.Namespace) -> None:
    """list komutu: desteklenen oyunlari gosterir."""
    print(f"\n{'='*50}")
    print(f"  Desteklenen Oyunlar (v{__version__})")
    print(f"{'='*50}")
    print(f"  {'Kod':<16} {'Oyun':<28} {'Yaw':<8} {'Durbun':<8}")
    print(f"  {'-'*16} {'-'*28} {'-'*8} {'-'*8}")
    for key in list_games():
        game = get_game(key)
        scope_count = len(game.scopes)
        print(f"  {key:<16} {game.name:<28} {game.yaw:<8} {scope_count:<8}")
    print()


def _run_info(args: argparse.Namespace) -> None:
    """info komutu: belirli bir oyunun detaylarini gosterir."""
    try:
        game = get_game(args.game)
    except KeyError as e:
        print(f"\n[!] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  {game.name}")
    print(f"{'='*50}")
    print(f"  Anahtar       : {args.game}")
    print(f"  Yaw           : {game.yaw}")
    print(f"  Hipfire FOV   : {game.hipfire_fov} (16:9 yatay)")
    print(f"  Sens Araligi  : {game.sens_min} - {game.sens_max}")
    print(f"  Sens Skalasi  : {game.sens_scale}")
    print(f"  Durbunler     : {len(game.scopes)} adet")
    for scope in game.scopes:
        print(f"    - {scope.id:<8} -> {scope.name} (FOV: {scope.fov})")
    print()


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sens-cli",
        description="Evrensel FPS Sens Cevirici - Oyunlar arasi fare "
                    "hassasiyeti donusum araci",
        epilog="Detayli bilgi: github.com/GameSens/sens-cli",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # -- convert --
    conv = sub.add_parser(
        "convert",
        help="Hassasiyet donusumu yap",
        description=(
            "Iki oyun arasinda hassasiyet donusumu yapar. "
            "Kaynak oyundaki degeriniz once evrensel cm/360'a "
            "cevrilir, ardindan hedef oyunun motor parametreleriyle "
            "tekrar oyun ici degere donusturulur."
        ),
    )
    conv.add_argument(
        "--source", "-s",
        required=True,
        metavar="OYUN",
        help=f"Kaynak oyun ({', '.join(list_games())})",
    )
    conv.add_argument(
        "--sens", "-S",
        required=True,
        type=float,
        metavar="DEGER",
        help="Kaynak oyundaki hassasiyet degeri",
    )
    conv.add_argument(
        "--dpi", "-d",
        required=True,
        type=int,
        metavar="DPI",
        help="Farenizin DPI degeri (orn: 400, 800, 1600)",
    )
    conv.add_argument(
        "--target", "-t",
        required=True,
        metavar="OYUN",
        help=f"Hedef oyun ({', '.join(list_games())})",
    )
    conv.add_argument(
        "--target-dpi",
        type=int,
        default=None,
        metavar="DPI",
        help="Hedef oyundaki DPI (belirtilmezse kaynak DPI kullanilir)",
    )
    conv.add_argument(
        "--mdm",
        type=float,
        default=0.0,
        metavar="YUZDE",
        help="MDM esleme yuzdesi (0-100, varsayilan: 0)",
    )
    conv.set_defaults(func=_run_convert)

    # -- list --
    sub.add_parser(
        "list",
        help="Desteklenen oyunlari listele",
        description="Tum desteklenen oyunlari ve temel parametrelerini gosterir.",
    ).set_defaults(func=_run_list)

    # -- info --
    info = sub.add_parser(
        "info",
        help="Oyun detaylarini goster",
        description="Belirli bir oyunun yaw, FOV ve durkun bilgilerini gosterir.",
    )
    info.add_argument(
        "game",
        metavar="OYUN",
        help=f"Oyun anahtari ({', '.join(list_games())})",
    )
    info.set_defaults(func=_run_info)

    return parser


def main() -> None:
    """CLI giris noktasi."""
    parser = _create_parser()
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
