"""
sens_cli.scopes
~~~~~~~~~~~~~~~
MDM (Monitor Distance Match) Dürbün Hesaplama Motoru.

Farklı oyunların dürbün/zoom seviyeleri arasında tutarlı
hassasiyet dönüşümü yapar. Asimetrik dürbün envanterlerini
(ör: CS2'de tek zoom → PUBG'de 7 dürbün) otomatik çözer.

MDM Formülü (0% eşleme):
    scope_multiplier = tan(scope_fov_rad / 2) / tan(hipfire_fov_rad / 2)
    scope_sens = base_sens × scope_multiplier

P% eşleme (mouse-sensitivity.com kanonik formülü):
    scope_multiplier = atan(P × tan(scope_fov_rad / 2)) / atan(P × tan(hipfire_fov_rad / 2))

100% eşleme basitleşir:
    scope_multiplier = scope_fov_rad / hipfire_fov_rad

Bu yaklaşım "monitor distance" (ekran mesafesi) eşlemesidir;
0% focal length skalası, 100% ekran kenarı eşlemesidir.
"""

from __future__ import annotations

import math

from .constants import ScopeDef, get_game


def _mdm_multiplier(
    hipfire_fov: float,
    scope_fov: float,
    match_pct: float = 0.0,
) -> float:
    """MDM (Monitor Distance Match) çarpanını hesaplar.

    Args:
        hipfire_fov: Ana görüş açısı (yatay, derece).
        scope_fov:   Dürbün görüş açısı (yatay, derece).
        match_pct:   Eşleme yüzdesi (0 = merkez, 100 = kenar).

    Returns:
        scope_sens = hipfire_sens × dönen değer.
    """
    hip_rad = math.radians(hipfire_fov)
    scope_rad = math.radians(scope_fov)

    if match_pct <= 0.0:
        # 0% MDM (focal length scaling)
        num = math.tan(scope_rad / 2.0)
        den = math.tan(hip_rad / 2.0)
    else:
        pct = match_pct / 100.0
        # P% MDM: ekran mesafesini pct oraninda olcekler
        num = math.atan(pct * math.tan(scope_rad / 2.0))
        den = math.atan(pct * math.tan(hip_rad / 2.0))

    if den == 0.0:
        return 1.0
    return num / den


def calculate_scopes(
    base_sens: float,
    source_game: str,
    target_game: str,
    match_pct: float = 0.0,
) -> dict[str, dict]:
    """Hedef oyunun tüm dürbün değerlerini hesaplar.

    Asimetrik dürbün senaryoları:
      - Az → Çok: Kaynağın base_sens'i tüm hedef dürbünlerine
        MDM ile dağıtılır.
      - Çok → Az: Kaynağın belirtilen ana dürbünü baz alınır.

    Args:
        base_sens:   Kaynak oyundaki ana hassasiyet.
        source_game: Kaynak oyun anahtarı.
        target_game: Hedef oyun anahtarı.
        match_pct:   MDM eşleme yüzdesi (varsayılan: 0).

    Returns:
        {scope_id: {"name": str, "sens": float, "fov": float}}
    """
    src = get_game(source_game)
    tgt = get_game(target_game)

    # Kaynağın varsayılan dürbünü yoksa base_sens aynen kullanılır
    # (az dürbünlü → çok dürbünlü senaryosu)
    results: dict[str, dict] = {}

    for scope in tgt.scopes:
        multiplier = _mdm_multiplier(
            hipfire_fov=src.hipfire_fov,
            scope_fov=scope.fov,
            match_pct=match_pct,
        )
        scope_sens = round(base_sens * multiplier, 2)
        results[scope.id] = {
            "name": scope.name,
            "sens": scope_sens,
            "fov": scope.fov,
        }

    return results


def calculate_single_scope(
    base_sens: float,
    source_game: str,
    target_game: str,
    scope_id: str,
    match_pct: float = 0.0,
) -> float:
    """Belirli bir dürbünün hassasiyet değerini hesaplar.

    Bu fonksiyon özellikle "çok dürbünlü → az dürbünlü"
    senaryosunda kullanıcının seçtiği ana dürbünün değerini
    hedef oyunun tek zoom/ADS değerine dönüştürmek için kullanılır.
    """
    src = get_game(source_game)
    tgt = get_game(target_game)

    # Kullanıcının seçtiği kaynak dürbünü bul
    source_scope = None
    for s in src.scopes:
        if s.id == scope_id:
            source_scope = s
            break

    if source_scope is None:
        raise KeyError(
            f"'{scope_id}' dürbünü {source_game} oyununda bulunamadı."
        )

    tgt_scope = tgt.scopes[0]  # Hedefin ilk (genelde tek) dürbünü

    multiplier = _mdm_multiplier(
        hipfire_fov=source_scope.fov,
        scope_fov=tgt_scope.fov,
        match_pct=match_pct,
    )
    return round(base_sens * multiplier, 2)
