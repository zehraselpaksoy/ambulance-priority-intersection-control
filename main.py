import traci
from ambulans_algilama import ambulans_bilgisi
from trafik_isigi_kontrol import oncelik_kontrol, oncelik_sistemini_guncelle

# SENARYO SEÇİMİ:
# "COKLU_YON": 4 yönden (Batı, Kuzey, Doğu, Güney) gelen ambulanslar art arda test edilir
# "KUYRUK": Batı yönünde yoğun kuyruk arkasındaki ambulans test edilir
# "AMBULANSSIZ": Sadece normal trafik
SENARYO = "COKLU_YON"

ambulanslar = ["ambulance_w_e", "ambulance_n_s", "ambulance_e_w", "ambulance_s_n"]
giris_zamanlari = {}
cikis_zamanlari = {}
toplam_carpisma_uyarisi = 0

traci.start([
    "sumo-gui",
    "-c", "simulation.sumocfg",
    "--start",
    "--delay", "150",
    "--seed", "42",
    "--collision.action", "warn",
    "--collision.check-junctions", "true"
])

try:
    for adim in range(450):
        traci.simulationStep()
        araclar = traci.vehicle.getIDList()

        if SENARYO == "AMBULANSSIZ":
            for amb_id in ambulanslar:
                if amb_id in araclar:
                    traci.vehicle.remove(amb_id)
            araclar = traci.vehicle.getIDList()

        # Kuyruk (Gridlock) uç senaryosu
        if adim == 10 and SENARYO == "KUYRUK":
            print("\n[UÇ SENARYO] Ambulansın önüne araç kuyruğu ekleniyor...")
            try:
                traci.route.add("kuyruk_rotasi", ["-E3", "E0"])
            except Exception:
                pass
            for i in range(5):
                try:
                    traci.vehicle.add(
                        vehID=f"kuyruk_araci_{i}",
                        routeID="kuyruk_rotasi",
                        typeID="car",
                        departPos=str(i * 8)
                    )
                except Exception:
                    pass

        # Çarpışma kontrolü
        carpisma_sayisi = traci.simulation.getCollidingVehiclesNumber()
        if carpisma_sayisi > 0:
            toplam_carpisma_uyarisi += 1
            print(f"UYARI! Çarpışma tespit edildi: {carpisma_sayisi}")

        # Aktif ambulansların verilerini topla
        aktif_bilgiler = {}
        for amb_id in ambulanslar:
            if amb_id in araclar:
                if amb_id not in giris_zamanlari:
                    giris_zamanlari[amb_id] = traci.simulation.getTime()
                    print(f"[{amb_id}] simülasyona girdi: {giris_zamanlari[amb_id]:.0f}. sn")

                aktif_bilgiler[amb_id] = ambulans_bilgisi(amb_id)

                yol = traci.vehicle.getRoadID(amb_id)
                if yol in ["E0", "E1", "E2", "E3"] and amb_id not in cikis_zamanlari:
                    cikis_zamanlari[amb_id] = traci.simulation.getTime()
                    sure = cikis_zamanlari[amb_id] - giris_zamanlari[amb_id]
                    print(f"[{amb_id}] kavşaktan çıkış yaptı ({yol}). Geçiş süresi: {sure:.2f} sn")

        if SENARYO == "AMBULANSSIZ":
            asama = "NORMAL"
        else:
            asama = oncelik_sistemini_guncelle(aktif_bilgiler)

        # Tüm ambulanslar çıkış yaptıysa ve faz toparlama bittiyse simülasyonu temizce sonlandır
        if (
            SENARYO != "AMBULANSSIZ"
            and len(cikis_zamanlari) == len(ambulanslar)
            and asama == "NORMAL"
            and traci.simulation.getTime() > max(cikis_zamanlari.values()) + 10
        ):
            print("\nTüm ambulans geçişleri ve faz toparlama tamamlandı.")
            break

finally:
    traci.close()

print("\n===== SİMÜLASYON DEMO ÖZETİ =====")
print(f"Senaryo: {SENARYO}")
for amb_id in ambulanslar:
    if amb_id in giris_zamanlari and amb_id in cikis_zamanlari:
        gecis = cikis_zamanlari[amb_id] - giris_zamanlari[amb_id]
        print(f"- {amb_id}: {gecis:.2f} saniye")
print(f"Toplam çarpışma uyarısı: {toplam_carpisma_uyarisi}")