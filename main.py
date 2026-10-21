
import traci

# Ambulans algılama fonksiyonunu içe aktar
from ambulans_algilama import ambulans_bilgisi

# Sadece batıdan doğuya gelen ambulans
ambulanslar = [
    "ambulance_w_e"
]

# Algılanan ambulansları kaydet
algilanan_ambulanslar = set()

# SUMO simülasyonunu yavaş başlat
traci.start([
    "sumo-gui",
    "-c", "simulation.sumocfg",
    "--start",
    "--delay", "200"
])

try:
    # Simülasyonu en fazla 250 adım çalıştır
    for adim in range(250):

        if traci.simulation.getMinExpectedNumber() == 0:
            print("Simülasyonda araç kalmadı.")
            break

        # Simülasyonu bir adım ilerlet
        traci.simulationStep()

        # Simülasyondaki aktif araçları al
        araclar = traci.vehicle.getIDList()

        # TEK AMBULANSI KONTROL ET
        for ambulans_id in ambulanslar:

            if ambulans_id in araclar:

                algilanan_ambulanslar.add(ambulans_id)

                # Her 5 adımda bir ambulans bilgilerini göster
                if adim % 5 == 0:

                    bilgi = ambulans_bilgisi(ambulans_id)

                    if bilgi is not None:

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
                        print("==============================")

finally:
    # SUMO bağlantısını kapat
    traci.close()

# TEST SONUÇLARI
print("\n===== ALGILAMA ÖZETİ =====")

if "ambulance_w_e" in algilanan_ambulanslar:
    print("ambulance_w_e: ALGILANDI")
else:
    print("ambulance_w_e: ALGILANMADI")

print("\nProgram tamamlandı.")
