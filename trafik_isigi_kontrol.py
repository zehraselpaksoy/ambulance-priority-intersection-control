import traci

KAVSAK_ID = "J0"
ALGILAMA_MESAFESI = 80  # En kısa yaklaşım yolu (-E2: 85.3m) ile uyumlu

DOGU_BATI_YESIL = 0
DOGU_BATI_SARI = 1
KUZEY_GUNEY_YESIL = 2
KUZEY_GUNEY_SARI = 3

SARI_SURESI = 3
KIRMIZI_SURESI = 2

gecis_asamasi = "NORMAL"
asamaya_giris_zamani = 0
aktif_ambulans_id = None
hedef_yesil_fazi = DOGU_BATI_YESIL
hedef_sari_fazi = DOGU_BATI_SARI
tamamlanan_ambulanslar = set()


def yone_gore_faz_belirle(yon):
    if yon in ["Batı", "Doğu"]:
        return DOGU_BATI_YESIL, DOGU_BATI_SARI
    return KUZEY_GUNEY_YESIL, KUZEY_GUNEY_SARI


def oncelik_kontrol(bilgi):
    if bilgi is None:
        return "Ambulans bulunamadı"
    if bilgi["mesafe"] is None:
        return "Ambulans yaklaşım yolunda değil"
    if bilgi["mesafe"] > ALGILAMA_MESAFESI:
        return f"Ambulans henüz {ALGILAMA_MESAFESI}m sınırında değil"

    istenen_yesil, _ = yone_gore_faz_belirle(bilgi["yon"])
    faz = traci.trafficlight.getPhase(KAVSAK_ID)

    if faz == istenen_yesil:
        return f"{bilgi['yon']} yönünde yeşil ışık aktif"
    return f"{bilgi['yon']} yönü için yeşil ışık önceliği gerekli"


def sari_isik_gecisi(faz):
    traci.trafficlight.setProgram(KAVSAK_ID, "0")
    traci.trafficlight.setPhase(KAVSAK_ID, faz)
    sari_durum = traci.trafficlight.getRedYellowGreenState(KAVSAK_ID)
    traci.trafficlight.setRedYellowGreenState(KAVSAK_ID, sari_durum)
    print(f"3 saniyelik sarı ışık geçişi başladı (Faz {faz}).")


def tum_yonler_kirmizi():
    traci.trafficlight.setRedYellowGreenState(KAVSAK_ID, "r" * 12)
    print("Tüm yönler kırmızı: 2 saniye güvenlik aşaması.")


def ambulansa_yesil_ver(yesil_faz):
    traci.trafficlight.setProgram(KAVSAK_ID, "0")
    traci.trafficlight.setPhase(KAVSAK_ID, yesil_faz)
    traci.trafficlight.setPhaseDuration(KAVSAK_ID, 5)
    print(f"Ambulans yönüne yeşil ışık verildi (Faz {yesil_faz}).")


def ambulans_gecti_mi(ambulans_id):
    if ambulans_id not in traci.vehicle.getIDList():
        return True
    yol = traci.vehicle.getRoadID(ambulans_id)
    return yol in ["E0", "E1", "E2", "E3"]


def faz_toparla_ve_normale_don(son_yesil_faz):
    traci.trafficlight.setProgram(KAVSAK_ID, "0")
    bekleyen_faz = KUZEY_GUNEY_YESIL if son_yesil_faz == DOGU_BATI_YESIL else DOGU_BATI_YESIL
    traci.trafficlight.setPhase(KAVSAK_ID, bekleyen_faz)
    TOPARLAMA_YESIL_SURESI = 25
    traci.trafficlight.setPhaseDuration(KAVSAK_ID, TOPARLAMA_YESIL_SURESI)
    print(f"Faz toparlama aktif: Bekleyen yöne (Faz {bekleyen_faz}) {TOPARLAMA_YESIL_SURESI} sn telafi yeşili verildi.")


def ambulans_yesilini_koru(yesil_faz):
    if traci.trafficlight.getPhase(KAVSAK_ID) == yesil_faz:
        traci.trafficlight.setPhaseDuration(KAVSAK_ID, 5)


def oncelik_sistemini_guncelle(aktif_bilgiler):
    global gecis_asamasi, asamaya_giris_zamani, aktif_ambulans_id
    global hedef_yesil_fazi, hedef_sari_fazi, tamamlanan_ambulanslar

    zaman = traci.simulation.getTime()

    # 1. NORMAL DURUM - Yaklaşan yeni ambulansı seç
    if gecis_asamasi == "NORMAL":
        aday_bilgi = None
        for amb_id, bilgi in aktif_bilgiler.items():
            if (
                amb_id not in tamamlanan_ambulanslar
                and bilgi is not None
                and bilgi["mesafe"] is not None
                and bilgi["mesafe"] <= ALGILAMA_MESAFESI
            ):
                aday_bilgi = bilgi
                break

        if aday_bilgi is None:
            return gecis_asamasi

        aktif_ambulans_id = aday_bilgi["id"]
        hedef_yesil_fazi, hedef_sari_fazi = yone_gore_faz_belirle(aday_bilgi["yon"])
        faz = traci.trafficlight.getPhase(KAVSAK_ID)

        print(f"\n[{aktif_ambulans_id} - {aday_bilgi['yon']}] öncelik bölgesine girdi.")

        if faz == hedef_yesil_fazi:
            gecis_asamasi = "YESIL"
            ambulans_yesilini_koru(hedef_yesil_fazi)
        else:
            gecis_sari = KUZEY_GUNEY_SARI if faz == KUZEY_GUNEY_YESIL else DOGU_BATI_SARI
            sari_isik_gecisi(gecis_sari)
            gecis_asamasi = "SARI"
            asamaya_giris_zamani = zaman

    # 2. SARI IŞIK
    elif gecis_asamasi == "SARI":
        if zaman - asamaya_giris_zamani >= SARI_SURESI:
            tum_yonler_kirmizi()
            gecis_asamasi = "KIRMIZI"
            asamaya_giris_zamani = zaman

    # 3. TÜM YÖNLER KIRMIZI
    elif gecis_asamasi == "KIRMIZI":
        if zaman - asamaya_giris_zamani >= KIRMIZI_SURESI:
            ambulansa_yesil_ver(hedef_yesil_fazi)
            gecis_asamasi = "YESIL"
            asamaya_giris_zamani = zaman

    # 4. AMBULANS YEŞİLİ
    elif gecis_asamasi == "YESIL":
        if ambulans_gecti_mi(aktif_ambulans_id):
            sari_isik_gecisi(hedef_sari_fazi)
            gecis_asamasi = "DONUS_SARI"
            asamaya_giris_zamani = zaman
            print(f"[{aktif_ambulans_id}] kavşağı güvenle geçti.")
        else:
            ambulans_yesilini_koru(hedef_yesil_fazi)

    # 5. DÖNÜŞ SARISI
    elif gecis_asamasi == "DONUS_SARI":
        if zaman - asamaya_giris_zamani >= SARI_SURESI:
            tum_yonler_kirmizi()
            gecis_asamasi = "DONUS_KIRMIZI"
            asamaya_giris_zamani = zaman

    # 6. FAZ TOPARLAMA VE NORMAL DÖNGÜYE DÖNÜŞ
    elif gecis_asamasi == "DONUS_KIRMIZI":
        if zaman - asamaya_giris_zamani >= KIRMIZI_SURESI:
            faz_toparla_ve_normale_don(hedef_yesil_fazi)
            tamamlanan_ambulanslar.add(aktif_ambulans_id)
            aktif_ambulans_id = None
            gecis_asamasi = "NORMAL"
            print("Normal trafik döngüsüne dönüldü.\n")

    return gecis_asamasi