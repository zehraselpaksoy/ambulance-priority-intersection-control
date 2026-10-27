
import traci

# Ambulans algılama fonksiyonu
from ambulans_algilama import ambulans_bilgisi

# Trafik ışığı kontrol fonksiyonları
from trafik_isigi_kontrol import (
    oncelik_kontrol,
    oncelik_sistemini_guncelle
)

# TEST MODU: ÖNCELİKLİ SİSTEM
# Ambulans algılandığında trafik ışıkları kontrol edilir.

# Ambulans bilgileri
ambulanslar = ["ambulance_w_e"]
algilanan_ambulanslar = set()

# Geçiş süresi ölçümü
ambulans_giris_zamani = None
ambulans_cikis_zamani = None

# Çarpışma kontrolü
toplam_carpisma_uyarisi = 0

# Sabit rastgelelik ayarıyla SUMO'yu başlat
traci.start([
    "sumo-gui",
    "-c", "simulation.sumocfg",
    "--start",
    "--delay", "200",
    "--seed", "42",
    "--collision.action", "warn",
    "--collision.check-junctions", "true"
])

try:
    # Simülasyonu en fazla 250 adım çalıştır
    for adim in range(250):

        # Simülasyonu bir adım ilerlet
        traci.simulationStep()

        # Çarpışma güvenlik kontrolü
        carpisma_sayisi = (
            traci.simulation.getCollidingVehiclesNumber()
        )

        if carpisma_sayisi > 0:
            toplam_carpisma_uyarisi += 1

            print(
                f"UYARI! Çarpışmaya karışan araç sayısı: "
                f"{carpisma_sayisi}"
            )

        # Simülasyondaki aktif araçlar
        araclar = traci.vehicle.getIDList()

        ambulans_id = ambulanslar[0]
        bilgi = None

        # Ambulansı algıla
        if ambulans_id in araclar:

            algilanan_ambulanslar.add(ambulans_id)

            # İlk görülme zamanını kaydet
            if ambulans_giris_zamani is None:

                ambulans_giris_zamani = (
                    traci.simulation.getTime()
                )

                print(
                    f"Ambulans giriş zamanı: "
                    f"{ambulans_giris_zamani:.0f} saniye"
                )

            # Ambulansın konum ve hız bilgileri
            bilgi = ambulans_bilgisi(ambulans_id)

        # ÖNCELİKLİ TRAFİK IŞIĞI KONTROLÜ
        # Her simülasyon adımında çalışır
        asama = oncelik_sistemini_guncelle(
            bilgi,
            ambulans_id
        )

        # Ambulansın çıkış zamanını kaydet
        if (
            ambulans_id in araclar
            and ambulans_cikis_zamani is None
        ):

            yol = traci.vehicle.getRoadID(ambulans_id)

            if yol == "E0":

                ambulans_cikis_zamani = (
                    traci.simulation.getTime()
                )

                print(
                    f"Ambulans çıkış zamanı: "
                    f"{ambulans_cikis_zamani:.0f} saniye"
                )

                if ambulans_giris_zamani is not None:

                    gecis_suresi = (
                        ambulans_cikis_zamani
                        - ambulans_giris_zamani
                    )

                    print(
                        f"Ambulans geçiş süresi: "
                        f"{gecis_suresi:.2f} saniye"
                    )

        # Trafik ışıklarının durumunu göster
        if (
            adim % 10 == 0
            or asama in ["KIRMIZI", "DONUS_KIRMIZI"]
        ):

            faz = traci.trafficlight.getPhase("J0")

            isik_durumu = (
                traci.trafficlight.getRedYellowGreenState("J0")
            )

            print(f"\nSimülasyon adımı: {adim + 1}")
            print(f"Trafik ışığı fazı: {faz}")
            print(f"Trafik ışığı renkleri: {isik_durumu}")
            print(f"Kontrol aşaması: {asama}")

        # Her 5 adımda ambulans bilgilerini göster
        if adim % 5 == 0 and bilgi is not None:

            karar = oncelik_kontrol(bilgi)

            print("\n===== AMBULANS BİLGİLERİ =====")
            print(f"Ambulans ID: {bilgi['id']}")
            print(f"Yaklaşım yönü: {bilgi['yon']}")

            if bilgi["mesafe"] is not None:

                print(
                    f"Kavşağa kalan mesafe: "
                    f"{bilgi['mesafe']:.2f} metre"
                )

            else:
                print("Kavşağa kalan mesafe: -")

            print(f"Hız: {bilgi['hiz']:.2f} m/s")
            print(f"Durum: {bilgi['durum']}")
            print(f"Öncelik kararı: {karar}")
            print(f"Kontrol aşaması: {asama}")
            print("==============================")

        # Simülasyonda araç kalmadıysa bitir
        if traci.simulation.getMinExpectedNumber() == 0:

            print("Simülasyonda araç kalmadı.")
            break

finally:
    # SUMO bağlantısını kapat
    traci.close()


# TEST SONUÇLARI
print("\n===== ÖNCELİKLİ SİMÜLASYON ÖZETİ =====")

if "ambulance_w_e" in algilanan_ambulanslar:
    print("Ambulans: ALGILANDI")
else:
    print("Ambulans: ALGILANMADI")

if (
    ambulans_giris_zamani is not None
    and ambulans_cikis_zamani is not None
):

    gecis_suresi = (
        ambulans_cikis_zamani - ambulans_giris_zamani
    )

    print(
        f"Öncelikli geçiş süresi: "
        f"{gecis_suresi:.2f} saniye"
    )

    # Aynı seed=42 ile ölçülen önceliksiz sonuç
    onceliksiz_sure = 48.00

    zaman_kazanci = onceliksiz_sure - gecis_suresi

    iyilesme = (
        zaman_kazanci / onceliksiz_sure
    ) * 100

    print(
        f"Önceliksiz geçiş süresi: "
        f"{onceliksiz_sure:.2f} saniye"
    )

    print(
        f"Zaman kazancı: "
        f"{zaman_kazanci:.2f} saniye"
    )

    print(
        f"Geçiş süresindeki azalma: "
        f"%{iyilesme:.2f}"
    )

else:
    print("Ambulans geçiş süresi ölçülemedi.")

print(
    f"Çarpışma algılanan simülasyon adımı sayısı: "
    f"{toplam_carpisma_uyarisi}"
)

print("\nProgram tamamlandı.")
