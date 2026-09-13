# TODO

Araştırma ve geliştirme çalışma listesi.

## ✅ Sonuç alınanlar

- [x] ROG Strix Go 2.4 USB HID cihazı tespit edildi.
- [x] USB VID/PID tespit edildi: `0x0B05:0x18D6`.
- [x] Pil bilgisinin standart Linux `UPower` / `/sys/class/power_supply/` üzerinden gelmediği doğrulandı.
- [x] İlgili HID arayüzü tespit edildi: `1-1:1.3` / `MI_03`.
- [x] `hidraw` üzerinden cihaza erişim sağlandı.
- [x] HID report descriptor çıkarıldı ve önemli report ID'ler belirlendi: `0x01`, `0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`, `0xFF`.
- [x] Consumer Control report'u çözümlendi ve ses/mute/media kontrolleri doğrulandı.
- [x] `0xFF` Feature Report için `GET_FEATURE` başarılı şekilde gerçekleştirildi.
- [x] `0xFF` Feature Report'un gözlenen cevabının şarj kablosu takılı/takılı değil durumunda değişmediği doğrulandı.
- [x] Pasif HID dinlemede vendor report'larının (`0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`) kendiliğinden anlamlı veri üretmediği görüldü.
- [x] `usbmon` erişiminin kernel lockdown nedeniyle engellendiği tespit edildi.
- [x] G-Helper kaynak kodunda genel ASUS HID battery query protokolü bulundu.
- [x] G-Helper'daki aday sorgu yapısı belirlendi: `[reportId, 0x12, 0x01]`.
- [x] Genel ASUS protokolünde response içindeki `response[6]` alanının pil yüzdesi, `response[9]` alanının şarj durumu olarak kullanıldığı görüldü.
- [x] G-Helper kaynak kodunda doğrudan `0x0B05:0x18D6` / ROG Strix Go 2.4 battery implementasyonu bulunamadı. Bu nedenle protokolün kulaklık için çalıştığı henüz varsayılmıyor.

## ❌ Sonuç alınamayanlar / henüz çözülemeyenler

- [ ] `0xFF` Feature Report'tan doğrudan pil yüzdesi okunamadı.
- [ ] `0x64` report'unun anlamı çözülemedi.
- [ ] `0x65` report'unun anlamı çözülemedi.
- [ ] `0x90` report'unun anlamı çözülemedi.
- [ ] `0xC4` report'unun anlamı çözülemedi.
- [ ] `0xE2` report'unun anlamı çözülemedi.
- [ ] `event19` ve `event20` üzerindeki `ABS_MISC` alanlarının anlamı belirlenemedi.
- [ ] Şu ana kadar hiçbir HID report'undan güvenilir pil yüzdesi elde edilemedi.
- [ ] Şu ana kadar hiçbir HID report'undan güvenilir şarj durumu elde edilemedi.
- [ ] Windows/Armoury Crate tarafındaki gerçek HID battery sorgusu henüz yakalanamadı.

## 🔬 Battery / HID keşfi

- [ ] G-Helper'daki ASUS battery sorgusunu Strix Go 2.4 üzerinde test et.
- [ ] Aday report ID'leri (`0x90`, `0xC4`, `0xFF`) üzerinde `[reportId, 0x12, 0x01]` sorgusunun kabul edilip edilmediğini kontrollü şekilde araştır.
- [ ] Sorgu cevap verirse response yapısını kaydet ve `response[6]` / `response[9]` benzeri alanları doğrula.
- [ ] Pil yüzdesi olduğu düşünülen alanı farklı pil seviyelerinde doğrula.
- [ ] Şarj bağlı ve bağlı değil durumlarında aynı alanı karşılaştır.
- [ ] `HIDIOCGFEATURE` sonuçlarının neden tüm report ID'lerde `ff 01...` döndürdüğünü daha ayrıntılı doğrula.
- [ ] `HIDIOCGINPUT` için alınan `Broken pipe` davranışını not et ve alternatif yöntemleri araştır.
- [ ] `0x64` vendor input report'unu çözümle.
- [ ] `0x65` vendor input report'unu çözümle.
- [ ] `0x90` input/output report'unu çözümle.
- [ ] `0xC4` input/output report'unu çözümle.
- [ ] `0xE2` input report'unu çözümle.
- [ ] `0xFF` feature/input report'unun alanlarını çözümle.
- [ ] Şarj bağlı / bağlı değil durumlarında tüm ilgili HID davranışlarını karşılaştır.
- [ ] Kulaklık açık / kapalı durumlarını karşılaştır.
- [ ] Dongle bağlı / ayrılmış durumlarını karşılaştır.
- [ ] `event19` ve `event20` üzerinde kontrollü durum testleri yap.

## 🔎 Mevcut kaynak kod araştırması

- [x] G-Helper `AsusKeyboard.cs` içindeki genel `ReadBattery()` yaklaşımı incelendi.
- [x] G-Helper'da battery destekleyen ASUS modellerinin `HasBattery()` implementasyonları incelendi.
- [ ] G-Helper issue/PR geçmişinde ROG Strix Go 2.4 (`18D6`) için özel battery protokolünü doğrula.
- [ ] GitHub üzerinde `0B05:18D6`, `18D6`, `0x90`, `0xC4`, `0x12 0x01` kombinasyonlarıyla başka implementasyonlar ara.

## 🧩 Firmware / Windows araştırması

- [ ] ASUS `S54WL_Update_V3763` firmware paketini statik olarak incele.
- [ ] Firmware/update executable içinde `0b05`, `18d6`, HID report ID ve battery ile ilgili stringleri ara.
- [ ] Armoury Crate / Armoury II'nin cihazla kullandığı protokolü araştır.
- [ ] Mümkünse Windows + USBPcap + Wireshark ile gerçek HID trafiğini yakala.
- [ ] Battery query request/response çiftini tespit et.

## 🛠️ Uygulama

- [ ] Battery yüzdesini güvenilir şekilde okuyacak Linux HID kodunu yaz.
- [ ] `/dev/hidrawN` yerine VID/PID veya stabil udev yolu ile cihaz keşfi yap.
- [ ] Düşük pil eşiği için freedesktop notification desteği ekle.
- [ ] Kritik pil eşiği için ayrı bildirim ekle.
- [ ] Şarj durumunu tespit edince şarj başladı/bitti bildirimlerini değerlendir.
- [ ] DE/WM bağımsız arka plan çalışmasını tasarla.
- [ ] Kullanıcı servisi / udev izinleri konusunu düzenle.
- [ ] Dongle yeniden bağlandığında cihazı otomatik yeniden keşfet.

## 🚫 Kapsam dışı

- [x] EQ kontrolü projeye dahil edilmeyecek. PipeWire/EasyEffects tarafından ele alınabilir.
- [x] Armoury Crate klonu yapılmayacak.
- [x] Gereksiz ASUS cihaz kontrolleri, pil okuma çözülene kadar öncelik değil.

## Sonraki oturum için ilk adım

1. G-Helper'daki `[reportId, 0x12, 0x01]` sorgusunu Strix Go 2.4'ün gerçek vendor report ID'leri üzerinde kontrollü şekilde test et.
2. Cevap veren bir report bulunursa response byte'larını kaydet.
3. Aynı değeri farklı pil/şarj durumlarında karşılaştır.
4. Sonuçları `research/rog-strix-go-2-4-linux-research.md` dosyasına ekle.
5. Pil alanı doğrulanırsa gerçek Linux battery reader implementasyonuna geç.
