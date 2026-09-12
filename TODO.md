# TODO

Geçici çalışma listesi. Araştırma tamamlandıkça maddeler güncellenecek.

## Battery / HID keşfi

- [ ] `HIDIOCGFEATURE` sonuçlarının neden tüm report ID'lerde `ff 01...` döndürdüğünü doğrula.
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

## Firmware / Windows araştırması

- [ ] ASUS `S54WL_Update_V3763` firmware paketini statik olarak incele.
- [ ] Firmware/update executable içinde `0b05`, `18d6`, HID report ID ve battery ile ilgili stringleri ara.
- [ ] Armoury Crate / Armoury II'nin cihazla kullandığı protokolü araştır.
- [ ] Mümkünse Windows + USBPcap + Wireshark ile gerçek HID trafiğini yakala.
- [ ] Battery query request/response çiftini tespit et.

## Uygulama

- [ ] Battery yüzdesini güvenilir şekilde okuyacak Linux HID kodunu yaz.
- [ ] `/dev/hidrawN` yerine VID/PID veya stabil udev yolu ile cihaz keşfi yap.
- [ ] Düşük pil eşiği için freedesktop notification desteği ekle.
- [ ] DE/WM bağımsız arka plan çalışmasını tasarla.
- [ ] Kullanıcı servisi / udev izinleri konusunu düzenle.

## Sonraki oturum için ilk adım

1. HID report'larını ve sysfs bağlantılarını daha ayrıntılı incele.
2. Ardından firmware statik analizine geç.
3. Sonuçları `research/rog-strix-go-2-4-linux-research.md` dosyasına ekle.
