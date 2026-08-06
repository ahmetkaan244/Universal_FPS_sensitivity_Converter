# Universal_FPS_sensitivity_Converter

**Evrensel FPS Sens Çevirici** — Oyunlar arası fare hassasiyeti (sensitivite) dönüşüm aracı.

CS2, Valorant, PUBG ve Arena Breakout arasında hassasiyetinizi fiziksel bir referansa
(cm/360) sabitleyerek tutarlı şekilde aktarın. Dürbün (scope/zoom) ayarları için
MDM (Monitor Distance Match) hesabı dahildir.

---
![Ana Menü](https://githubusercontent.com)


---

## ✨ Özellikler

- **cm/360 evrensel fiziksel birimi** üzerinden iki yönlü dönüşüm
- **18 oyun** desteği: Counter-Strike 2, Valorant, PUBG: Battlegrounds, Arena Breakout, Apex Legends, Overwatch 2, Call of Duty Serisi, The Finals, Marvel Rivals, Deadlock, Rainbow Six Siege, Fortnite, Battlefield 2042, Halo Infinite, Destiny 2, Escape From Tarkov, Rust, Team Fortress 2
- **MDM (0–100%) dürbün eşlemesi** — farklı zoom seviyelerinde tutarlı nişan
- **Hedef DPI** desteği (farklı DPI kullanıyorsanız)
- **Asimetrik dürbün çözümü** — çok dürbünlü → az dürbünlü senaryolarda kaynak dürbün seçimi
- **Grafiksel arayüz (GUI)** — customtkinter tabanlı, temiz ve modern
- **Komut satırı (CLI)** — hızlı ve betiklenebilir dönüşüm

---

## 📦 Kurulum

Gereksinim: **Python 3.10+**

```bash
# Depoyu klonlayın
git clone https://github.com/GameSens/sens-cli.git
cd Universal_FPS_sensitivity_Converter

# GUI (önerilen) dahil tam kurulum
pip install -e ".[gui]"

# Sadece komut satırı
pip install -e .
```

Bağımlılıklar:

| Bağımlılık     | Gerekçe                      |
| -------------- | ----------------------------- |
| `customtkinter`| Grafiksel arayüz (opsiyonel)  |
| `pytest`       | Testler (opsiyonel)           |

---

## 🖥️ CLI Kullanımı

### Dönüşüm (`convert`)

```bash
# CS2'deki 1.2 sens @ 800 DPI → PUBG
sens-cli convert --source cs2 --sens 1.2 --dpi 800 --target pubg
```

Parametreler:

| Parametre     | Kısa | Açıklama                              |
| ------------- | ---- | ------------------------------------- |
| `--source`    | `-s` | Kaynak oyun                            |
| `--sens`      | `-S` | Kaynak oyundaki hassasiyet             |
| `--dpi`       | `-d` | Farenizin DPI değeri                   |
| `--target`    | `-t` | Hedef oyun                             |
| `--target-dpi`|      | Hedef DPI (boş = kaynak DPI)           |
| `--mdm`       |      | MDM eşleme yüzdesi (0–100, varsayılan 0)|

### Oyunları listele (`list`)

```bash
sens-cli list
```

### Oyun detayı (`info`)

```bash
sens-cli info cs2
sens-cli info pubg
```

### Doğrudan çalıştırma

```bash
python -m sens_cli list
python gui.py            # veya sens-gui
```

---

## 🎨 GUI Kullanımı

`sens-gui` komutu ile başlatın:

```bash
sens-gui
# ya da geliştirme sırasında:
python gui.py
```

Arayüzde:

1. **Kaynak Oyun** ve **Hedef Oyun** seçin
2. **Hassasiyet** ve **DPI** değerlerinizi girin (hedef DPI isteğe bağlı)
3. **MDM eşleme yüzdesi**ni slaytla ayarlayın (0% merkez, 100% ekran kenarı)
4. **HESAPLA** düğmesine tıklayın

Ek:

- **⇄ Takas** düğmesi kaynak ile hedef oyunu (ve DPI alanlarını) değiştirir
- **Kaynak Dürbün** seçimi, çok dürbünlü → tek dürbünlü senaryolarda hangi
  dürbünün hedef oyunun dürbününe eşleneceğini belirler (örn: PUBG 4x → CS2 Zoom)
- **Oyunlar** sekmesi tüm oyunların ve seçili oyunların detaylarını gösterir
- **Kopyala** düğmesi sonucu panoya kopyalar

---

## 🎮 Desteklenen Oyunlar

| Anahtar               | Oyun                | Yaw      | Dürbün |
| --------------------- | ------------------- | -------- | ------ |
| `apex_legends`        | Apex Legends        | 0.022    | 1      |
| `arena_breakout`      | Arena Breakout      | 0.011    | 4      |
| `battlefield_2042`    | Battlefield 2042    | 0.0066   | 2      |
| `call_of_duty_serisi` | Call of Duty Serisi | 0.0066   | 1      |
| `cs2`                 | Counter-Strike 2    | 0.022    | 1      |
| `deadlock`            | Deadlock            | 0.044    | 1      |
| `destiny_2`           | Destiny 2           | 0.0066   | 2      |
| `escape_from_tarkov`  | Escape From Tarkov  | 0.125    | 2      |
| `fortnite`            | Fortnite            | 0.005555 | 2      |
| `halo_infinite`       | Halo Infinite       | 0.022    | 1      |
| `marvel_rivals`       | Marvel Rivals       | 0.0066   | 1      |
| `overwatch_2`         | Overwatch 2         | 0.0066   | 1      |
| `pubg`                | PUBG: Battlegrounds | 0.0055   | 6      |
| `rainbow_six_siege`   | Rainbow Six Siege   | 0.00573  | 2      |
| `rust`                | Rust                | 0.222    | 1      |
| `team_fortress_2`     | Team Fortress 2     | 0.022    | 1      |
| `the_finals`          | The Finals          | 0.0066   | 1      |
| `valorant`            | Valorant            | 0.07     | 2      |

> Yeni bir oyun eklemek için `sens_cli/constants.py` dosyasındaki `GAMES`
> sözlüğüne bir girdi eklemeniz yeterlidir.

---

## 🔬 Matematiksel Model

### cm/360 (fiziksel mesafe)

```
cm/360 = 360 / (sens_internal × dpi × yaw) × 2.54
```

### MDM (Monitor Distance Match)

0% eşleme (focal length):

```
scope_multiplier = tan(scope_fov/2) / tan(hipfire_fov/2)
```

P% eşleme (mouse-sensitivity.com kanonik formülü):

```
scope_multiplier = atan(P × tan(scope_fov/2)) / atan(P × tan(hipfire_fov/2))
```

Dönüşüm iki adımda gerçekleşir: kaynak değer → cm/360 → hedef oyun değeri.

---

## 🧪 Testler

```bash
python -m pytest tests/ -q
```

Testler dönüşüm formüllerini bağımsız kaynaklardan (senslab.pro, sensai.games)
doğrulanmış değerlerle karakterize eder.

---

## 📄 Lisans

[MIT](LICENSE) — GameSens Generator Contributors
