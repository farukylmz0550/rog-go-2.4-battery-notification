# ROG Go 2.4 Battery Notification

Linux için ASUS ROG Strix Go 2.4'ün pil seviyesini takip etmeye yönelik bir çalışma.

> ⚠️ **Erken geliştirme aşaması**
>
> Projenin şu anki ana amacı araştırma ve protokol keşfi. Henüz çalışan bir pil yüzdesi okuyucusu bulunmuyor.

## Amaç

Birincil hedef:

**ROG Strix Go 2.4'ün pil yüzdesini Linux'tan okuyabilmek ve pil azaldığında masaüstü bildirim göstermek.**

Bildirimler mümkün olduğunca masaüstü ortamından ve pencere yöneticisinden bağımsız, freedesktop bildirim standardı üzerinden çalışacak.

Diğer özellikler daha sonra değerlendirilebilir.

## Mevcut durum

- USB cihazı Linux tarafından tanınıyor.
- VID/PID: `0B05:18D6`
- ROG Strix Go 2.4 için HID arayüzü mevcut.
- `hidraw` üzerinden ASUS vendor HID raporları incelenebiliyor.
- Standart medya kontrolleri Linux input sistemi tarafından tanınıyor.
- UPower şu anda kulaklığı bir batarya aygıtı olarak göstermiyor.
- `/sys/class/power_supply/` altında kulaklık için batarya aygıtı bulunmuyor.
- HID Feature Report `0xFF` okunabiliyor ancak mevcut cevap pil seviyesini göstermiyor.
- Pil yüzdesinin hangi HID raporunda bulunduğu henüz bilinmiyor.

## Araştırma

Detaylı tersine mühendislik notları:

[`research/rog-strix-go-2-4-linux-research.md`](research/rog-strix-go-2-4-linux-research.md)

Araştırma notlarında HID descriptor, report ID'ler, Linux input arayüzleri, PipeWire durumu ve yapılan deneylerin sonuçları tutuluyor.

## Kapsam

### Ana özellik

- Pil yüzdesini okumak
- Düşük pil seviyesinde bildirim göstermek

### Opsiyonel

- Şarj oluyor bildirimi
- Kritik pil bildirimi
- Mikrofon mute davranışı
- Diğer cihaz bilgileri
- ASUS'a özgü ek özellikler

### Kapsam dışı

EQ ve genel ses işleme bu projenin ana hedefi değil. Bunlar Linux'un PipeWire/EasyEffects ekosistemiyle ayrıca çözülebilir.

## Durum

**Research / Reverse Engineering**

Şimdilik proje araştırma aşamasında. Kod yapısı, pil protokolü çözüldükten sonra şekillendirilecek.
