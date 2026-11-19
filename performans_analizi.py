
# 8. HAFTA - PERFORMANS ANALİZİ
# SUMO simülasyonlarından elde edilen sonuçlar

# 5. hafta - Aynı seed ile öncelik karşılaştırması
onceliksiz_sure = 48
oncelikli_sure = 18

# 7. hafta - Güncel sistem senaryoları
normal_sure = 13
kuyruk_sure = 20

# 5. hafta performans hesabı
zaman_kazanci = onceliksiz_sure - oncelikli_sure

iyilesme_orani = (
    zaman_kazanci / onceliksiz_sure
) * 100

# 7. hafta senaryo karşılaştırması
kuyruk_gecikmesi = kuyruk_sure - normal_sure

print("===== 8. HAFTA PERFORMANS ANALİZİ =====")

print(f"Önceliksiz geçiş: {onceliksiz_sure} saniye")
print(f"Öncelikli geçiş: {oncelikli_sure} saniye")
print(f"Zaman kazancı: {zaman_kazanci} saniye")
print(f"Geçiş süresindeki azalma: %{iyilesme_orani:.2f}")

print("\n===== 7. HAFTA SENARYO KARŞILAŞTIRMASI =====")

print(f"NORMAL senaryosu: {normal_sure} saniye")
print(f"KUYRUK senaryosu: {kuyruk_sure} saniye")
print(f"Kuyruk nedeniyle süre farkı: {kuyruk_gecikmesi} saniye")



# 8. HAFTA - PERFORMANS GRAFİKLERİ

import matplotlib.pyplot as plt

# Grafik 1: Öncelikli ve önceliksiz sistem
plt.figure(figsize=(7, 5))

sistemler = ["Önceliksiz", "Öncelikli"]
sureler = [onceliksiz_sure, oncelikli_sure]

plt.bar(sistemler, sureler, color=["gray", "green"])

plt.title("Ambulans Öncelik Sistemi Karşılaştırması")
plt.ylabel("Geçiş Süresi (saniye)")

for i, sure in enumerate(sureler):
    plt.text(i, sure + 0.5, f"{sure} sn", ha="center")

plt.ylim(0, 55)
plt.tight_layout()
plt.savefig("oncelik_karsilastirma.png")
plt.close()

# Grafik 2: NORMAL ve KUYRUK senaryoları
plt.figure(figsize=(7, 5))

senaryolar = ["NORMAL", "KUYRUK"]
senaryo_sureleri = [normal_sure, kuyruk_sure]

plt.bar(senaryolar, senaryo_sureleri, color=["blue", "orange"])

plt.title("7. Hafta Senaryo Karşılaştırması")
plt.ylabel("Geçiş Süresi (saniye)")

for i, sure in enumerate(senaryo_sureleri):
    plt.text(i, sure + 0.3, f"{sure} sn", ha="center")

plt.ylim(0, 25)
plt.tight_layout()
plt.savefig("senaryo_karsilastirma.png")
plt.close()

print("\nPerformans grafikleri oluşturuldu.")
