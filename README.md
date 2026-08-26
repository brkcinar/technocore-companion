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
6. [Bu araç neden güvenli](#6-bu-araç-neden-güvenli)
7. [Sık sorulan sorular](#7-sık-sorulan-sorular)
8. [Katkıda bulunma](#8-katkıda-bulunma)
9. [Lisans](#9-lisans)

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
 3) Katkimi kaydet + paylasim metni olustur (offline, hicbir sey gonderilmez)
 4) Kaydedilen katkiyi Technocore'a gonder (AGA VERI GONDERIR - onay ister)
 5) Cikis
```

Önerilen sıra:

1. **`1` — Yeni kimlik oluştur:** Sizden 12+ karakterlik bir parola
   isteyecek. Bu parolayı **unutmayın ve kimseyle paylaşmayın** — kimliğinizi
   şifreleyip `~/.technocore/identity.pem` dosyasına kaydeder.
2. **`2` — Kimliğimi göster:** Az önce oluşturduğunuz DID'i (dijital
   kimlik) ekrana yazdırır, örn: `did:key:z6Mk...`
3. **`3` — Katkımı kaydet:** Neyi katkı olarak sunmak istediğinizi
   sorar (örneğin bu repoyu yazdıysanız onu anlatabilirsiniz), isteğe
   bağlı bir link ister, sonra **tamamen offline** bir imzalı mesaj ve
   hazır bir paylaşım (tweet) metni hazırlar. Bu adımda **hiçbir yere
   hiçbir şey gönderilmez.**
4. **`4` — Technocore'a gönder:** Bu adım ağa gerçekten veri gönderir.
   Göndermeden önce size *tam olarak* neyin, hangi adrese gideceğini
   gösterir ve `evet`/`hayir` diye açıkça sorar. İstemiyorsanız `hayir`
   yazıp iptal edebilirsiniz.

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

## 6) Bu araç neden güvenli

- **Özel anahtar hiçbir zaman şifresiz diske yazılmaz.** Parola ile
  şifrelenmiş PEM formatında saklanır (`0600` dosya izniyle, yani sadece
  siz okuyabilirsiniz).
- **Hiçbir tarayıcı ya da yerel web sunucusu açılmaz.** Bazı benzer
  araçlar özel anahtarı bir yerel API üzerinden tarayıcıya gönderip
  şifresiz bir dosya olarak indirtir — bu araç bunu yapmaz.
- **Ağa veri gönderen tek adım (`4`) her zaman açık onay ister** ve
  göndermeden önce tam içeriği gösterir.
- Kod tek bir Python dosyası (`technocore_companion.py`) — kısa, okunabilir,
  gizli bir davranışı yok; isterseniz kurulum yapmadan önce dosyayı açıp
  okuyabilirsiniz.

## 7) Sık sorulan sorular

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

## 8) Katkıda bulunma

Hata bulursanız veya bir iyileştirme öneriniz varsa GitHub üzerinden bir
"Issue" açabilir ya da doğrudan bir "Pull Request" gönderebilirsiniz.

## 9) Lisans

[MIT](LICENSE) — özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz.
