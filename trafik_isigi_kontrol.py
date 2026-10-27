
import traci

# KAVŞAK AYARLARI
KAVSAK_ID = "J0"
ALGILAMA_MESAFESI = 50

AMBULANS_YESIL_FAZI = 0
AMBULANS_SARI_FAZI = 1
DIGER_YESIL_FAZI = 2
DIGER_SARI_FAZI = 3

SARI_SURESI = 3
KIRMIZI_SURESI = 2

# Kontrol değişkenleri
gecis_asamasi = "NORMAL"
asamaya_giris_zamani = 0
oncelik_tamamlandi = False


# ZEHRA - Ambulans öncelik kararı
def oncelik_kontrol(bilgi):

    if bilgi is None:
        return "Ambulans bulunamadı"

    if bilgi["mesafe"] is None:
        return "Ambulans yaklaşım yolunda değil"

    if bilgi["mesafe"] > ALGILAMA_MESAFESI:
        return "Ambulans henüz 50 metre sınırında değil"

    faz = traci.trafficlight.getPhase(KAVSAK_ID)

    if faz == AMBULANS_YESIL_FAZI:
        return "Ambulans yönünde yeşil ışık var"

    return "Ambulans için yeşil ışık önceliği gerekli"


# ROJIN - Sarı ışık geçişi
def sari_isik_gecisi(faz):

    traci.trafficlight.setProgram(KAVSAK_ID, "0")
    traci.trafficlight.setPhase(KAVSAK_ID, faz)

    # Sarı durumunu sabitle
    sari_durum = traci.trafficlight.getRedYellowGreenState(
        KAVSAK_ID
    )

    traci.trafficlight.setRedYellowGreenState(
        KAVSAK_ID, sari_durum
    )

    print("3 saniyelik sarı ışık geçişi başladı.")


# SU NUR - Tüm yönler kırmızı
def tum_yonler_kirmizi():

    traci.trafficlight.setRedYellowGreenState(
        KAVSAK_ID, "r" * 12
    )

    print("Tüm yönler kırmızı: 2 saniye.")


# ZEHRA - Ambulansa yeşil verme
def ambulansa_yesil_ver():

    traci.trafficlight.setProgram(KAVSAK_ID, "0")

    traci.trafficlight.setPhase(
        KAVSAK_ID, AMBULANS_YESIL_FAZI
    )

    traci.trafficlight.setPhaseDuration(
        KAVSAK_ID, 5
    )

    print("Ambulans yönüne yeşil ışık verildi.")


# Ambulans kavşağı geçti mi?
def ambulans_gecti_mi(ambulans_id):

    araclar = traci.vehicle.getIDList()

    if ambulans_id not in araclar:
        return False

    yol = traci.vehicle.getRoadID(ambulans_id)

    return yol == "E0"


# Yeşil ışığı koru
def ambulans_yesilini_koru():

    if traci.trafficlight.getPhase(KAVSAK_ID) == 0:
        traci.trafficlight.setPhaseDuration(
            KAVSAK_ID, 5
        )


# ANA TRAFİK IŞIĞI KONTROLÜ
def oncelik_sistemini_guncelle(bilgi, ambulans_id):

    global gecis_asamasi
    global asamaya_giris_zamani
    global oncelik_tamamlandi

    zaman = traci.simulation.getTime()

    # 1. NORMAL DURUM
    if gecis_asamasi == "NORMAL":

        if oncelik_tamamlandi:
            return gecis_asamasi

        if bilgi is None or bilgi["mesafe"] is None:
            return gecis_asamasi

        if bilgi["mesafe"] > ALGILAMA_MESAFESI:
            return gecis_asamasi

        faz = traci.trafficlight.getPhase(KAVSAK_ID)

        print("Ambulans öncelik bölgesine girdi.")

        if faz == AMBULANS_YESIL_FAZI:

            gecis_asamasi = "YESIL"
            ambulans_yesilini_koru()

        else:

            if faz == AMBULANS_SARI_FAZI:
                sari_isik_gecisi(AMBULANS_SARI_FAZI)
            else:
                sari_isik_gecisi(DIGER_SARI_FAZI)

            gecis_asamasi = "SARI"
            asamaya_giris_zamani = zaman

    # 2. SARI ISIK
    elif gecis_asamasi == "SARI":

        if zaman - asamaya_giris_zamani >= SARI_SURESI:

            tum_yonler_kirmizi()

            gecis_asamasi = "KIRMIZI"
            asamaya_giris_zamani = zaman

    # 3. TUM YONLER KIRMIZI
    elif gecis_asamasi == "KIRMIZI":

        if zaman - asamaya_giris_zamani >= KIRMIZI_SURESI:

            ambulansa_yesil_ver()

            gecis_asamasi = "YESIL"
            asamaya_giris_zamani = zaman

    # 4. AMBULANS YESILI
    elif gecis_asamasi == "YESIL":

        if ambulans_gecti_mi(ambulans_id):

            sari_isik_gecisi(AMBULANS_SARI_FAZI)

            gecis_asamasi = "DONUS_SARI"
            asamaya_giris_zamani = zaman

            print("Ambulans kavşağı geçti.")

        else:
            ambulans_yesilini_koru()

    # 5. NORMAL DONGUYE DONUS SARISI
    elif gecis_asamasi == "DONUS_SARI":

        if zaman - asamaya_giris_zamani >= SARI_SURESI:

            tum_yonler_kirmizi()

            gecis_asamasi = "DONUS_KIRMIZI"
            asamaya_giris_zamani = zaman

    # 6. NORMAL DONGUYE GUVENLI DONUS
    elif gecis_asamasi == "DONUS_KIRMIZI":

        if zaman - asamaya_giris_zamani >= KIRMIZI_SURESI:

            traci.trafficlight.setProgram(KAVSAK_ID, "0")

            traci.trafficlight.setPhase(
                KAVSAK_ID, DIGER_YESIL_FAZI
            )

            traci.trafficlight.setPhaseDuration(
                KAVSAK_ID, 35
            )

            gecis_asamasi = "NORMAL"
            oncelik_tamamlandi = True

            print("Normal trafik döngüsüne dönüldü.")

    return gecis_asamasi
