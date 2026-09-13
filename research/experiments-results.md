# ROG Strix Go 2.4 - Deney ve Araştırma Sonuçları

Bu dosya, şimdiye kadar yapılan deneyleri iki temel sınıfa ayırır: **sonuç alınan / doğrulanan bulgular** ve **denenen fakat sonuç vermeyen veya henüz anlamlandırılamayan yöntemler**.

Amaç, araştırmanın hangi noktalarının kesinleştiğini ve hangi yolların tekrar edilmemesi gerektiğini açıkça belgelemektir.

---

## 1. Cihaz kimliği ve Linux bağlantısı

### ✅ Sonuç alındı

Linux cihazı doğru şekilde tespit edildi.

- Ürün: `ASUS ROG STRIX Go 2.4`
- USB VID: `0x0B05`
- USB PID: `0x18D6`
- USB revision: `3765`
- USB speed: Full Speed
- HID interface: `1-1:1.3`
- HID sürücüsü: `usbhid`
- Test sırasında cihaz: `/dev/hidraw5`

`hidraw` numarasının sabit olmadığı doğrulandı. Bu nedenle uygulama `/dev/hidraw5` gibi sabit bir yolu kullanmamalı; VID/PID ve cihaz adına göre keşif yapmalı.

`udevadm info -q property -n /dev/hidraw5` ile ASUS cihazına ait USB/HID özellikleri başarıyla görüldü.

---

## 2. Linux input event'leri

### ✅ Sonuç alındı

Kulaklığın Consumer Control arayüzü `/dev/input/event18` üzerinden Linux'a standart medya tuşları sağlıyor.

Desteklenen kontroller:

- `KEY_VOLUMEUP`
- `KEY_VOLUMEDOWN`
- `KEY_MUTE`
- `KEY_PLAYPAUSE`
- `KEY_NEXTSONG`
- `KEY_PREVIOUSSONG`

Play/Pause düğmesinin çoklu tıklama davranışı da doğrulandı:

- 1 tıklama → Play/Pause
- 2 tıklama → Next Track
- 3 tıklama → Previous Track

Bu davranışlar Linux input katmanında gözlemlendi.

### ⚠️ Kısmi sonuç / belirsiz

`event19` ve `event20` isim olarak yine `ASUS ROG STRIX Go 2.4` olarak görünüyor.

`event19`:

- `BTN_0`
- `ABS_MISC`, `0..13`

`event20`:

- `ABS_MISC`, `0..65535`

Normal düğme ve kontrol testlerinde bu event'lerde anlamlı değişiklik tespit edilmedi.

Bunların ne amaçla kullanıldığı henüz bilinmiyor.

---

## 3. Fiziksel mute düğmesi

### ✅ Sonuç alındı, fakat beklenen davranış doğrulanmadı

Fiziksel mute düğmesi Linux'a `KEY_MUTE` olarak geliyor.

Ancak test sırasında düğmeye basıldığında PipeWire tarafındaki mikrofon kaynağının gerçekten `MUTED` durumuna geçmediği görüldü. `wpctl get-volume` çıktısında mute durumu oluşmadı ve mikrofon ses yakalamaya devam etti.

Sonuç:

- Düğmenin Linux input eventi kesin olarak biliniyor.
- Donanımsal mikrofon kesme davranışı gösterilemedi.
- Bu nedenle ileride yazılım tarafında `KEY_MUTE` olayını PipeWire mute komutuna bağlamak mümkün olabilir, ancak bu ayrı bir özellik olarak ele alınmalı.

---

## 4. PipeWire / ALSA ses aygıtları

### ✅ Sonuç alındı

Kulaklığın gerçek ses aygıtları PipeWire tarafından doğru şekilde tanınıyor.

- Çıkış: `ROG STRIX Go 2.4 Analog Stereo`
- Mikrofon: `ROG STRIX Go 2.4 Mono`

Bu sonuç, `event19` ve `event20` cihazlarının gerçek PCM mikrofon/ses akışı olmadığını doğruladı.

---

## 5. Standart Linux battery arayüzleri

### ❌ Sonuç alınamadı

Standart Linux güç yönetimi arayüzlerinde kulaklık pili görünmedi.

Testler:

```text
/sys/class/power_supply/ → cihaz yok
```

```text
upower -e → yalnızca DisplayDevice
```

UPower üzerinde ASUS / ROG / `18d6` aranmasına rağmen kulaklık pili bulunamadı.

Sonuç: pil yüzdesi standart UPower/power_supply üzerinden alınamıyor veya kernel/driver bu cihaz için battery entegrasyonu sağlamıyor.

---

## 6. Pasif hidraw dinleme

### ❌ Vendor report açısından sonuç alınamadı

Şu yöntem kullanıldı:

```bash
sudo timeout 30s cat /dev/hidraw5 | xxd -g1
```

Cihaz doğru olmasına rağmen 30 saniyelik pasif dinleme sırasında `0x64`, `0x65`, `0x90`, `0xC4` veya `0xE2` vendor input report'larından spontan veri gelmedi.

Bu, cihazın bu durum bilgilerini sürekli yayınlamadığını veya başka bir tetikleyici/request beklediğini düşündürüyor.

Standard Consumer Control olayları ise fiziksel tuşlara basıldığında görülebiliyor.

---

## 7. HID report descriptor analizi

### ✅ Sonuç alındı

HID report descriptor başarıyla elde edildi. Descriptor uzunluğu 426 byte.

Önemli report ID'leri ve yapıları belirlendi:

| Report ID | Yön | Tür / yapı |
|---|---|---|
| `0x01` | IN | Consumer Control |
| `0x64` | IN | Vendor-defined, `0xFFC0` |
| `0x65` | IN | Vendor-defined, `0xFFC0` |
| `0x90` | IN/OUT | Vendor-defined |
| `0xC4` | IN/OUT | Vendor-defined |
| `0xE2` | IN | Vendor-defined |
| `0xFF` | IN/FEATURE | Vendor-defined |

Özellikle `0x90` ve `0xC4` hem Input hem Output olarak tanımlı. Bunlar ileride protokol araştırmasında önem taşıyor.

---

## 8. Consumer Control raw HID report

### ✅ Sonuç alındı

`0x01` report ID'si üzerinden fiziksel bir ses kontrolü sırasında şu raw report gözlemlendi:

```text
01 00 02 00 00
01 00 00 00 00
```

Descriptor ile karşılaştırıldığında bunun Volume Down basma/bırakma olayı olduğu doğrulandı.

Bu, descriptor ile gerçek cihaz davranışının eşleştiğini doğrulayan önemli bir kontrol noktasıdır.

---

## 9. HIDIOCGFEATURE deneyi

### ⚠️ Beklenmeyen sonuç / henüz anlamlandırılamadı

Vendor report ID'leri için `HIDIOCGFEATURE` çağrıları yapıldı.

Sorgulanan ID'ler:

- `0x64`
- `0x65`
- `0x90`
- `0xC4`
- `0xE2`
- `0xFF`

Hepsinde başlangıçta aynı tür cevap görüldü:

```text
ff 01 ...
```

Örnek olarak `0xFF` için daha önce 27 byte uzunluğunda şu cevap alınmıştı:

```text
ff 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

10 ardışık okumada aynı cevap görüldü.

Şarj kablosu bağlama/çıkarma testinde de bu değer değişmedi.

Sonuç:

- `0xFF` feature cevabının doğrudan battery yüzdesi olmadığı gösterildi.
- `ff 01` içindeki `01` değerinin anlamı bilinmiyor.
- Testte kullanılan ioctl yaklaşımının cihazın gerçek vendor protokolünü ortaya çıkardığı henüz kanıtlanmış değil.

### Not

İlk probe scriptinde sabit ioctl boyutu nedeniyle `buffer overflow` hatası oluştu. Daha sonra ioctl kodları buffer boyutuna göre dinamik oluşturularak script düzeltildi.

---

## 10. HIDIOCGINPUT deneyi

### ❌ Sonuç alınamadı

Aynı report ID'leri `HIDIOCGINPUT` ile sorgulanmaya çalışıldı.

Tüm sorgular:

```text
ERROR: [Errno 32] Broken pipe
```

sonucunu verdi.

Bu cihazın bu ioctl üzerinden Input report sorgulamasını kabul etmediğini veya bu mekanizmanın bu HID arayüzü için uygun olmadığını düşündürüyor.

Bu yöntem şimdilik araştırmanın ana yolu olmaktan çıkarıldı.

---

## 11. usbmon

### ⚠️ Araç mevcut, fakat erişim engellendi

`usbmon` kernel modülü yüklenebildi.

Ancak debugfs üzerinden usbmon verisi okunurken Fedora kernel lockdown engeli görüldü:

```text
Lockdown: cat: debugfs access is restricted
```

Lockdown durumu:

```text
none [integrity] confidentiality
```

Bu nedenle USB trafiğini mevcut Fedora oturumunda usbmon ile yakalamak mümkün olmadı.

Kernel lockdown'u zayıflatmak mevcut araştırmada tercih edilen bir yöntem değil.

---

## 12. ASUS firmware bilgisi

### ✅ Kısmi sonuç alındı

ASUS tarafında `S54WL_Update_V3763` adlı firmware güncelleme paketi bulundu.

Paket sürümü: `3763`

Cihazın Linux tarafından bildirilen USB revision değeri ise:

```text
3765
```

Bu nedenle cihazdaki firmware/revision ile bulunan eski güncelleme paketi arasında fark olabileceği düşünülebilir.

Firmware henüz statik olarak incelenmedi.

---

## 13. Genel durum

### Kesinleşenler

- Doğru cihaz: `0b05:18d6`
- Doğru HID arayüzü tespit edildi.
- Consumer Control report'ları çözümlendi.
- Fiziksel medya kontrolleri Linux'ta çalışıyor.
- PipeWire ses ve mikrofon aygıtları çalışıyor.
- Standart Linux battery arayüzlerinde kulaklık pili yok.
- Vendor report ID'leri ve descriptor yapısı çıkarıldı.
- Pasif hidraw dinlemesinde vendor status report'u gözlenmedi.
- `HIDIOCGINPUT` kullanılabilir bir yol olarak sonuç vermedi.
- `0xFF` feature cevabı şarj durumuyla değişmedi.

### Henüz çözülemeyenler

- Battery yüzdesinin gerçek kaynağı
- `0x64` / `0x65` report'larının anlamı
- `0x90` report protokolü
- `0xC4` report protokolü
- `0xE2` report protokolü
- `0xFF` report alanlarının anlamı
- `event19` / `event20` işlevi
- Armoury Crate / Armoury II'nin battery sorgu protokolü

---

## 14. Sonraki araştırma yönü

Öncelik sırası:

1. `event19` ve `event20`'yi güç/şarj/dongle durumlarıyla kontrollü test etmek.
2. HID sysfs bağlantılarını daha ayrıntılı incelemek.
3. ASUS firmware/update executable dosyalarını statik olarak analiz etmek.
4. Armoury Crate / Armoury II'nin cihaz protokolünü araştırmak.
5. Mümkünse Windows + USBPcap + Wireshark ile gerçek USB/HID trafiğini yakalamak.
6. Battery query request/response çiftini tespit etmek.
7. Protokol çözüldükten sonra Linux battery daemon ve freedesktop notification katmanını geliştirmek.

---

## Sonuç

Şu ana kadarki araştırma, cihazın Linux tarafından temel HID ve ses işlevleriyle düzgün tanındığını fakat battery bilgisinin standart Linux güç arayüzlerinden gelmediğini gösteriyor.

En önemli negatif sonuçlar `hidraw` pasif dinlemesi, standart battery arayüzleri, `HIDIOCGINPUT` ve mevcut `0xFF` feature sorgusunun battery bilgisini vermemesi.

Bu nedenle bundan sonraki temel hedef, ASUS'un kendi yazılımının veya firmware'inin kullandığı vendor protokolünü ortaya çıkarmaktır.
