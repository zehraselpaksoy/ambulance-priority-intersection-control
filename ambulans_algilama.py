
import traci

# Ambulansların kavşağa giriş yolları
YAKLASIM_YOLLARI = {
    "-E3": "Batı",
    "-E0": "Doğu",
    "-E1": "Kuzey",
    "-E2": "Güney"
}


def ambulans_bilgisi(ambulans_id):
    """
    Ambulansın yaklaşım yönünü ve
    kavşağa kalan mesafesini hesaplar.
    """

    # Ambulans simülasyonda mı?
    if ambulans_id not in traci.vehicle.getIDList():
        return None

    # Ambulansın bulunduğu yol
    yol_id = traci.vehicle.getRoadID(ambulans_id)

    # Ambulansın hızı
    hiz = traci.vehicle.getSpeed(ambulans_id)

    # Ambulansın koordinatları
    konum = traci.vehicle.getPosition(ambulans_id)

    # Kavşağa yaklaşım yolunda mı?
    if yol_id in YAKLASIM_YOLLARI:

        # Bulunduğu şerit
        serit_id = traci.vehicle.getLaneID(ambulans_id)

        # Şeridin toplam uzunluğu
        yol_uzunlugu = traci.lane.getLength(serit_id)

        # Ambulansın şerit üzerindeki konumu
        yol_konumu = traci.vehicle.getLanePosition(ambulans_id)

        # Kavşağa girişe kalan mesafe
        mesafe = max(0, yol_uzunlugu - yol_konumu)

        return {
            "id": ambulans_id,
            "yon": YAKLASIM_YOLLARI[yol_id],
            "mesafe": mesafe,
            "hiz": hiz,
            "konum": konum,
            "durum": "Kavşağa yaklaşıyor"
        }

    return {
        "id": ambulans_id,
        "yon": "Yaklaşım yolu dışında",
        "mesafe": None,
        "hiz": hiz,
        "konum": konum,
        "durum": "Kavşağa yaklaşım yolunda değil"
    }
