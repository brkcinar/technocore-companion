# technocore-companion

🇹🇷 Türkçe | [🇬🇧 English](README.en.md)

Hiç teknik bilgisi olmayan bir kullanıcının bile adım adım takip edip
uygulayabileceği, Türkçe menülü, açıklamalı bir **Technocore `did:key`
sihirbazı**. Terminalde çalışır, hiçbir tarayıcı ya da yerel web sunucusu
açmaz; kimliğinizin özel anahtarı (private key) her zaman şifreli olarak
diskte tutulur ve hiçbir zaman ekrana ya da ağa çıplak biçimde yazılmaz.

> ⚠️ **Önemli:** `technocore.chat`, Flop Labs'ın resmi GitHub
> organizasyonunda (`github.com/flop-labs/technocore-chat`) yayınladığı,
> çekirdek protokolün parçası olmayan ("satellite service") ama resmen
> kendi işlettiği bir yardımcı servistir. Buna rağmen bu araç size hiçbir
> ödül ya da airdrop uygunluğu **garanti etmez** — bunlar Flop Labs'ın
> kendi takdirinde. Ağa bir şey göndermeden önce araç size her seferinde
> tam olarak ne gönderileceğini gösterir ve onayınızı ister.

---

## İçindekiler

1. [Gereksinimler](#1-gereksinimler)
2. [Sistemi güncelleme](#2-sistemi-güncelleme)
3. [Kurulum](#3-kurulum)
4. [Kullanım](#4-kullanım)
5. [Örnek çalıştırma](#5-örnek-çalıştırma)
6. [Gelen kutusu ve sınırlı otomatik yanıt](#6-gelen-kutusu-ve-sınırlı-otomatik-yanıt)
7. [Bu araç neden güvenli](#7-bu-araç-neden-güvenli)
8. [Sık sorulan sorular](#8-sık-sorulan-sorular)
9. [Katkıda bulunma](#9-katkıda-bulunma)
10. [Lisans](#10-lisans)

---

## 1) Gereksinimler

Bu rehber **Ubuntu / Debian tabanlı Linux** dağıtımları için yazılmıştır
(Ubuntu 20.04 ve üzeri önerilir). İhtiyacınız olanlar:

- Bir terminal (Ubuntu'da `Ctrl+Alt+T` ile açılır)
- İnternet bağlantısı (sadece kurulum ve isteğe bağlı 4. adım için)
- Yaklaşık 5 dakika

Aşağıdaki paketler kurulum adımında otomatik olarak kurulacak, şimdiden
bilmeniz yeterli:

| Paket | Ne işe yarar |
|---|---|
| `python3` | Aracı çalıştıran programlama dili |
| `python3-venv` | Bağımlılıkları izole bir ortamda tutmak için |
| `python3-pip` | Python paketlerini kurmak için |
| `git` | Bu repoyu bilgisayarınıza indirmek (klonlamak) için |

## 2) Sistemi güncelleme

Yeni bir şey kurmadan önce sisteminizi güncel tutmanız her zaman iyi bir
alışkanlıktır. Terminali açın ve şu iki komutu sırayla çalıştırın:

```bash
sudo apt update
sudo apt upgrade -y
```

- `sudo` komutu yönetici (admin) yetkisi ister; sisteminizin parolasını
  soracaktır, yazarken ekranda görünmez, bu normaldir, yazıp Enter'a basın.
- `apt update`, paket listelerini günceller (henüz hiçbir şey kurmaz).
- `apt upgrade -y` ise sisteminizdeki mevcut paketleri günceller. `-y`
  sorulan onay sorularına otomatik "evet" der.

## 3) Kurulum

Şimdi gerekli paketleri kurup bu repoyu indirelim:

```bash
# Gerekli sistem paketlerini kur
sudo apt install -y python3 python3-venv python3-pip git

# Bu repoyu bilgisayarınıza indirin (klonlayın)
git clone https://github.com/<kullanici-adiniz>/technocore-companion.git
cd technocore-companion

# Python için izole bir çalışma ortamı (venv) oluşturun ve aktive edin
python3 -m venv .venv
source .venv/bin/activate

# Aracın ihtiyaç duyduğu tek Python paketini kurun
pip install -r requirements.txt
```

> 💡 `source .venv/bin/activate` komutunu her yeni terminal açtığınızda
> bu klasörde tekrar çalıştırmanız gerekir. Terminal isteminizin başında
> `(.venv)` yazısını görürseniz ortam aktif demektir.

## 4) Kullanım

Aracı Türkçe menüyle başlatmak için:

```bash
python3 technocore_companion.py tr
```

İngilizce menü için:

```bash
python3 technocore_companion.py en
```

Karşınıza şöyle bir menü çıkacak:

```
Ne yapmak istersiniz?
 1) Yeni kimlik olustur (ilk kez)
 2) Kimligimi goster
 3) Kimligimi ilan et (posta kutusu adresimi yayinla - AGA VERI GONDERIR)
 4) Katkimi kaydet + paylasim metni olustur (offline, hicbir sey gonderilmez)
 5) Kaydedilen katkiyi gonder (AGA VERI GONDERIR - onay ister)
 6) Gelen kutumu kontrol et
 7) Yeni mesaj bekle (canli - Ctrl+C ile durdurun)
 8) Cikis
```

Önerilen sıra:

1. **`1` — Yeni kimlik oluştur:** Sizden 12+ karakterlik bir parola
   isteyecek. Bu parolayı **unutmayın ve kimseyle paylaşmayın** — kimliğinizi
   şifreleyip `~/.technocore/identity.pem` dosyasına kaydeder. Aynı anda,
   sizin için rastgele, tahmin edilemez bir **posta kutusu adı**
   (`mb-p-...`) üretir — ama bunu henüz kimseye söylemez.
2. **`2` — Kimliğimi göster:** DID'inizi ve posta kutunuzu ekrana yazdırır.
3. **`3` — Kimliğimi ilan et:** Posta kutunuzun adresini herkesin
   okuyabileceği bir yere yazar, böylece başkaları size mesaj
   gönderebilir. **Sadece adres yayınlanır**, kutunuzun içeriği değil.
4. **`4` — Katkımı kaydet:** Neyi katkı olarak sunmak istediğinizi
   sorar (örneğin bu repoyu yazdıysanız onu anlatabilirsiniz), isteğe
   bağlı bir link ister, sonra **tamamen offline** bir imzalı mesaj ve
   hazır bir paylaşım (tweet) metni hazırlar. Bu adımda **hiçbir yere
   hiçbir şey gönderilmez.**
5. **`5` — Gönder:** Bu adım ağa gerçekten veri gönderir. Göndermeden
   önce size *tam olarak* neyin, hangi adrese gideceğini gösterir ve
   `evet`/`hayir` diye açıkça sorar. İstemiyorsanız `hayir` yazıp
   iptal edebilirsiniz.
6. **`6` / `7` — Gelen kutusu:** bkz. aşağıdaki bölüm.

## 5) Örnek çalıştırma

```
$ python3 technocore_companion.py tr

== Technocore Companion ==
Bu sihirbaz size Technocore icin bir dijital kimlik (DID) olusturmanizda...

Ne yapmak istersiniz?
> 1
Yeni kimliginiz icin bir parola belirleyin (en az 12 karakter): ********
Parolayi tekrar girin: ********
Kimlik olusturuldu ve sifreli olarak kaydedildi: /home/kullanici/.technocore/identity.pem
DID'iniz: did:key:z6MkvxJLotfEqBPjCnsinArfX1vEmRPKvwnPgGcKReYySaog
```

## 6) Gelen kutusu ve sınırlı otomatik yanıt

Bu, `technocore-companion`'ı bildiğimiz diğer Technocore araçlarından
ayıran özellik: onların hepsi **tek yönlü** ("kimlik oluştur, mesaj at,
bitti"). Bu araç isterseniz **iki yönlü** çalışır — birisi size mesaj
yazdığında haberdar olabilirsiniz.

Bu, Technocore'un kendi "posta kutusu" (`mb-`) mekanizmasını kullanır:
sadece **imzalı** (yani kanıtlanabilir bir kimlikten gelen) mesajlar kabul
eder ve adı tahmin edilemez olduğu için (`mb-p-<rastgele>`) spam ile
doldurulamaz. Adresi sadece siz, `3` numaralı adımla ilan ederseniz
başkaları bulabilir.

- **`6` — Gelen kutumu kontrol et:** Kutunuzu bir kez okur, yeni
  mesajları gösterir.
- **`7` — Yeni mesaj bekle:** Sürekli açık kalıp, biri yazınca **anında**
  ekrana basar. Durdurmak için `Ctrl+C`.

### Otomatiklik SINIRLIDIR, bilerek

Araç, gelen bir mesaja üç şekilde davranabilir:

1. **Otomatik yanıt** — SADECE mesaj tam olarak `ping`, `durum` gibi
   önceden tanımlı, zararsız birkaç kalıptan birine eşleşirse, "buradayım"
   anlamında sabit bir cevap gönderir. Bunun da **günlük** ve
   **gönderen başına** bir üst sınırı vardır.
2. **⚠️ Şüpheli işaretleme** — mesaj "gönder", "imzala", "çalıştır",
   "tıkla", "cüzdan", "özel anahtar" gibi bir **eylem talebi** içeriyor
   gibi görünüyorsa, araç **hiçbir şey yapmaz**, sadece sizi açıkça uyarır.
   Bu tür mesajlara **kör kör uymayın** — bu, sizi kandırıp bir şey
   yaptırmaya çalışan bir mesaj olabilir (bkz. aşağıdaki güvenlik notu).
3. **İnsana bırak** — yukarıdakilerin hiçbiri değilse, mesajı gösterir ve
   isterseniz elle bir cevap yazmanızı ister; siz onaylamadan **hiçbir
   şey gönderilmez.**

Yani araç kendi başına asla "şunu gönder/imzala/indir" diyen bir mesaja
uymaz veya sizin adınıza karmaşık bir işlem yapmaz — en fazla "buradayım"
der. Gerisi her zaman size kalır.

## 7) Bu araç neden güvenli

- **Özel anahtar hiçbir zaman şifresiz diske yazılmaz.** Parola ile
  şifrelenmiş PEM formatında saklanır (`0600` dosya izniyle, yani sadece
  siz okuyabilirsiniz).
- **Hiçbir tarayıcı ya da yerel web sunucusu açılmaz.** Bazı benzer
  araçlar özel anahtarı bir yerel API üzerinden tarayıcıya gönderip
  şifresiz bir dosya olarak indirtir — bu araç bunu yapmaz.
- **Ağa veri gönderen adımlar (`3`, `5`) her zaman açık onay ister** ve
  göndermeden önce tam içeriği gösterir.
- **Otomatik yanıt kasıtlı olarak dar tutulmuştur** — bkz. yukarıdaki
  bölüm 6. Bir şey "gönder/imzala/çalıştır" gibi bir talep içeriyorsa
  araç hiçbir zaman kendi başına buna uymaz, sadece sizi uyarır.
- Kod tek bir Python dosyası (`technocore_companion.py`) — kısa, okunabilir,
  gizli bir davranışı yok; isterseniz kurulum yapmadan önce dosyayı açıp
  okuyabilirsiniz.

## 8) Sık sorulan sorular

**Parolamı unuttum, ne yapmalıyım?**
Maalesef şifrelenmiş kimlik dosyasını parolasız açmanın bir yolu yok.
`~/.technocore/identity.pem` dosyasını silip `1` numaralı adımla yeni bir
kimlik oluşturmanız gerekir.

**Bu araç bana airdrop garantisi veriyor mu?**
Hayır. Bu sadece Technocore protokolüne katılmanızı kolaylaştıran bir
araç. Herhangi bir ödül vaadinin flop.finance'in resmi kanallarından
doğrulanması size kalmıştır.

**`command not found: python3` hatası alıyorum.**
`sudo apt install -y python3` komutunu çalıştırıp tekrar deneyin.

**`(.venv)` yazısı terminalimde yok, ne yapmalıyım?**
Repo klasöründeyken `source .venv/bin/activate` komutunu tekrar çalıştırın.

**Gelen kutusu otomatik yanıt vermeyi reddetti, neden?**
Ya günlük otomatik-yanıt hakkınız doldu, ya da aynı kişiye çok yakın
zamanda zaten otomatik yanıt verilmiş (spam/kötüye kullanımı önlemek için
kasıtlı bir sınır). Mesajı elle yanıtlayabilirsiniz.

## 9) Katkıda bulunma

Hata bulursanız veya bir iyileştirme öneriniz varsa GitHub üzerinden bir
"Issue" açabilir ya da doğrudan bir "Pull Request" gönderebilirsiniz.

## 10) Lisans

[MIT](LICENSE) — özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz.
