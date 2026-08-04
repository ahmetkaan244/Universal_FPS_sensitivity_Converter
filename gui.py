"""
sens-cli GUI
~~~~~~~~~~~~
Modern grafik arayuz. customtkinter ile olusturulmustur.
sens_cli.core ve sens_cli.scopes motorunu kullanir.

Kullanim:
    python -m gui
    sens-gui  (pip install sonrasi)
"""

from __future__ import annotations

import sys
import os

# Proje kokunu sys.path'e ekle (pip install yoksa direkt calistirma icin)
_proj_root = os.path.dirname(os.path.abspath(__file__))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

import customtkinter as ctk
from tkinter import messagebox

from sens_cli.constants import GAMES, get_game, list_games
from sens_cli.core import convert_sensitivity, sens_to_cm360
from sens_cli.scopes import calculate_scopes

# ── GORSEL TEMA ──────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ── SABITLER ─────────────────────────────────────────────────
PAD = 10
INNER_PAD = 6
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 13
TITLE = "Evrensel FPS Sens Cevirici v3.0.0"
WIN_W = 680
WIN_H = 680


class SensGui(ctk.CTk):
    """Ana uygulama penceresi."""

    def __init__(self) -> None:
        super().__init__()

        self.title(TITLE)
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.minsize(520, 580)
        self.resizable(True, True)

        self._game_keys = list_games()
        self._game_names = [GAMES[k].name for k in self._game_keys]

        self._build_ui()
        self._bind_events()

    # ── ARAYUZ KURULUMU ──────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # sonuclar alani esnek

        # --- Baslik ---
        header = ctk.CTkLabel(
            self, text=TITLE,
            font=(FONT_FAMILY, 20, "bold"),
            anchor="center",
        )
        header.grid(row=0, column=0, pady=(PAD, 0), padx=PAD, sticky="ew")

        ayrac = ctk.CTkFrame(self, height=2, fg_color="#2fa572")
        ayrac.grid(row=1, column=0, pady=(PAD, 0), padx=PAD * 2, sticky="ew")

        # --- Girdi Alani ---
        self._build_inputs()

        # --- Hesapla Butonu ---
        self._btn_hesapla = ctk.CTkButton(
            self, text="HESAPLA",
            font=(FONT_FAMILY, 14, "bold"),
            height=42,
            corner_radius=8,
            command=self._on_calculate,
        )
        self._btn_hesapla.grid(row=3, column=0, pady=(PAD, 0), padx=PAD * 4, sticky="ew")

        # --- Sonuc Alani ---
        self._build_results()

    def _build_inputs(self) -> None:
        """Girdi panelini olusturur."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=2, column=0, pady=(PAD, 0), padx=PAD, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        satir = 0
        row_conf = {"sticky": "ew", "padx": (PAD, INNER_PAD), "pady": INNER_PAD}

        # Kaynak Oyun
        ctk.CTkLabel(frame, text="Kaynak Oyun:", font=(FONT_FAMILY, FONT_SIZE)).grid(
            row=satir, column=0, **row_conf
        )
        self._src_combo = ctk.CTkComboBox(
            frame, values=self._game_names, state="readonly",
            font=(FONT_FAMILY, FONT_SIZE), width=200,
        )
        self._src_combo.set(self._game_names[0])
        self._src_combo.grid(row=satir, column=1, **row_conf)
        satir += 1

        # Hedef Oyun
        ctk.CTkLabel(frame, text="Hedef Oyun:", font=(FONT_FAMILY, FONT_SIZE)).grid(
            row=satir, column=0, **row_conf
        )
        self._tgt_combo = ctk.CTkComboBox(
            frame, values=self._game_names, state="readonly",
            font=(FONT_FAMILY, FONT_SIZE), width=200,
        )
        if len(self._game_names) > 1:
            self._tgt_combo.set(self._game_names[1])
        else:
            self._tgt_combo.set(self._game_names[0])
        self._tgt_combo.grid(row=satir, column=1, **row_conf)
        satir += 1

        # Hassasiyet
        ctk.CTkLabel(frame, text="Hassasiyet (Sens):", font=(FONT_FAMILY, FONT_SIZE)).grid(
            row=satir, column=0, **row_conf
        )
        self._sens_entry = ctk.CTkEntry(
            frame, placeholder_text="Orn: 1.2", font=(FONT_FAMILY, FONT_SIZE),
        )
        self._sens_entry.grid(row=satir, column=1, **row_conf)
        satir += 1

        # DPI
        ctk.CTkLabel(frame, text="DPI:", font=(FONT_FAMILY, FONT_SIZE)).grid(
            row=satir, column=0, **row_conf
        )
        self._dpi_entry = ctk.CTkEntry(
            frame, placeholder_text="Orn: 800", font=(FONT_FAMILY, FONT_SIZE),
        )
        self._dpi_entry.grid(row=satir, column=1, **row_conf)
        satir += 1

        # Hedef DPI
        ctk.CTkLabel(frame, text="Hedef DPI (opsiyonel):", font=(FONT_FAMILY, FONT_SIZE)).grid(
            row=satir, column=0, **row_conf
        )
        self._tdpi_entry = ctk.CTkEntry(
            frame, placeholder_text="Bos = kaynak DPI", font=(FONT_FAMILY, FONT_SIZE),
        )
        self._tdpi_entry.grid(row=satir, column=1, **row_conf)
        satir += 1

        # MDM
        ctk.CTkLabel(frame, text="MDM Eslama %:", font=(FONT_FAMILY, FONT_SIZE)).grid(
            row=satir, column=0, **row_conf
        )
        mdm_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mdm_frame.grid(row=satir, column=1, **row_conf)
        mdm_frame.grid_columnconfigure(0, weight=1)

        self._mdm_slider = ctk.CTkSlider(
            mdm_frame, from_=0, to=100, number_of_steps=100,
            command=self._on_mdm_change,
        )
        self._mdm_slider.set(0)
        self._mdm_slider.grid(row=0, column=0, sticky="ew", padx=(0, INNER_PAD))

        self._mdm_label = ctk.CTkLabel(
            mdm_frame, text="%0", font=(FONT_FAMILY, FONT_SIZE),
            width=45, anchor="center",
        )
        self._mdm_label.grid(row=0, column=1)

    def _build_results(self) -> None:
        """Sonuc goruntuleme alanini olusturur."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=4, column=0, pady=PAD, padx=PAD, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self._result_box = ctk.CTkTextbox(
            frame,
            font=(FONT_FAMILY, 13),
            corner_radius=8,
            wrap="word",
            state="disabled",
        )
        self._result_box.grid(row=0, column=0, pady=PAD, padx=PAD, sticky="nsew")

    # ── OLAYLAR ──────────────────────────────────────────────

    def _bind_events(self) -> None:
        self._sens_entry.bind("<Return>", lambda _: self._on_calculate())
        self._dpi_entry.bind("<Return>", lambda _: self._on_calculate())

    def _on_mdm_change(self, value: float) -> None:
        self._mdm_label.configure(text=f"%{int(value)}")

    # ── HESAPLAMA ────────────────────────────────────────────

    def _get_game_key(self, combo: ctk.CTkComboBox) -> str:
        """ComboBox'taki oyun adindan anahtar dondurur."""
        name = combo.get()
        for key, game in GAMES.items():
            if game.name == name:
                return key
        return self._game_keys[0]

    def _validate_inputs(self) -> tuple[float, int, int | None, float] | None:
        """Girdileri dogrular. Hataliysa None, dogruysa (sens, dpi, tdpi, mdm) dondurur."""
        try:
            sens = float(self._sens_entry.get().strip().replace(",", "."))
        except (ValueError, AttributeError):
            messagebox.showerror("Hata", "Gecersiz hassasiyet degeri. Orn: 1.2")
            return None

        if sens <= 0:
            messagebox.showerror("Hata", "Hassasiyet 0'dan buyuk olmalidir.")
            return None

        try:
            dpi = int(self._dpi_entry.get().strip())
        except (ValueError, AttributeError):
            messagebox.showerror("Hata", "Gecersiz DPI degeri. Orn: 800")
            return None

        if dpi <= 0:
            messagebox.showerror("Hata", "DPI 0'dan buyuk olmalidir.")
            return None

        tdpi_raw = self._tdpi_entry.get().strip()
        tdpi: int | None = None
        if tdpi_raw:
            try:
                tdpi = int(tdpi_raw)
                if tdpi <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Hata", "Gecersiz hedef DPI degeri.")
                return None

        mdm = self._mdm_slider.get()

        return sens, dpi, tdpi, mdm

    def _on_calculate(self) -> None:
        """Hesaplama butonu tiklandiginda calisir."""
        sonuc = self._validate_inputs()
        if sonuc is None:
            return

        sens, dpi, tdpi, mdm = sonuc
        src_key = self._get_game_key(self._src_combo)
        tgt_key = self._get_game_key(self._tgt_combo)

        src_game = get_game(src_key)
        tgt_game = get_game(tgt_key)

        self._result_box.configure(state="normal")
        self._result_box.delete("1.0", "end")

        def w(text: str) -> None:
            self._result_box.insert("end", text + "\n")

        try:
            cm360, target_sens = convert_sensitivity(
                source_sens=sens,
                source_dpi=dpi,
                source_game=src_key,
                target_game=tgt_key,
                target_dpi=tdpi,
            )

            # Baslik
            w("=" * 50)
            w(f"  Sonuc: {src_game.name} -> {tgt_game.name}")
            w("=" * 50)

            # cm/360
            w(f"\n [+] Fiziksel Eslisme (cm/360): {cm360} cm")
            w(f"     Yaw: {src_game.name}: {src_game.yaw}, {tgt_game.name}: {tgt_game.yaw}")
            hedef_cm360 = sens_to_cm360(sens, dpi, tgt_key)
            w(f"     Not: {sens} degeri {src_game.name}'de {cm360} cm/360 ama {tgt_game.name}'de {hedef_cm360} cm/360 eder.")
            w(f"     Bu yuzden oyunlar arasi deger farklidir - motor yaw sabitleri farklidir.")

            dpi_str = f"{dpi}"
            if tdpi:
                dpi_str = f"{dpi} -> {tdpi}"
            w(f"     DPI: {dpi_str}  |  Sens: {sens}")

            # Hedef sens
            w(f"\n [+] {tgt_game.name} Genel Hassasiyet: {target_sens}")

            # Durbunler
            scopes = calculate_scopes(
                base_sens=target_sens,
                source_game=src_key,
                target_game=tgt_key,
                match_pct=mdm,
            )

            if scopes:
                w(f"\n [+] {tgt_game.name} Durbun Ayarlari (MDM %{int(mdm)}):")
                max_name = max(len(s["name"]) for s in scopes.values())
                for data in scopes.values():
                    name_p = data["name"].ljust(max_name)
                    w(f"     - {name_p} : {data['sens']:>8}  (FOV: {data['fov']}d)")

            w(f"\n {'*'} Ipucu: Sonrasi nisan hissinizi antrenmanda test edin.")

        except KeyError as e:
            w(f"\n [!] HATA: {e}")
        except Exception as e:
            w(f"\n [!] Beklenmeyen hata: {e}")

        self._result_box.configure(state="disabled")
        self._result_box.see("1.0")

    # ── KLAVYE KISAYOLLARI ───────────────────────────────────

    def run(self) -> None:
        """Pencereyi baslat."""
        self.mainloop()


def main() -> None:
    """GUI giris noktasi. `sens-gui` script entry point'i buraya yonlenir."""
    app = SensGui()
    app.run()


if __name__ == "__main__":
    main()
