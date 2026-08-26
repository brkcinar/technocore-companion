#!/usr/bin/env python3
"""
Technocore Companion - Teknik bilgisi olmayan kullanicilar icin adim adim
Technocore did:key sihirbazi.

Bu arac, teknocore-did-starter (Python/CLI) ve technocore-did-tool (Node/Web)
projelerinden farkli, ozgun bir uygulamadir. Ayni acik protokolu (Ed25519
did:key + imzali mesajlasma) hedefler ama:

  - Sifresiz private key asla diske veya ekrana yazilmaz (repo2'nin aksine).
  - Tarayici/yerel web sunucusu acmaz; hicbir key ag uzerinden ya da
    localhost API'siyle disariya sizmaz.
  - Turkce ve Ingilizce, menu tabanli, aciklamali bir "sihirbaz" sunar;
    komut satiri bayraklarini ezberlemeyi gerektirmez.
  - Her adimda ne oldugunu ve neden oldugunu acik acik anlatir; agin
    disina (technocore.chat) veri gonderilmeden once HER ZAMAN onay ister
    - TEK istisna: 0.2.0'daki "gelen kutusu" ozelligi, onceden tanimli,
      zararsiz birkac kaliba (ping/durum) siki sinirli, hiz-sinirli bir
      otomatik yanit verir. Bunun disindaki HER SEY (ozellikle "sunu
      gonder/imzala/calistir" tarzi talimat iceren mesajlar) insana
      birakilir ve supheli olarak isaretlenir - bkz. classify_incoming().

Bagimlilik: sadece "cryptography" paketi (repo1 ile ayni), gerisi stdlib.
"""

from __future__ import annotations

import base64
import getpass
import hashlib
import json
import os
import secrets
import sys
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

APP_NAME = "technocore-companion"
APP_VERSION = "0.2.0"
DEFAULT_BASE_URL = "https://technocore.chat"
DEFAULT_KEY_PATH = Path.home() / ".technocore" / "identity.pem"
DEFAULT_STATE_PATH = Path.home() / ".technocore" / "rehber_state.json"
MULTICODEC_ED25519 = b"\xed\x01"
BASE58BTC_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# --------------------------------------------------------------------------
# Gelen kutusu / sinirli-otonomi ayarlari
#
# Bu araci diger yaklasik 7-8 rakip DID aracindan ayiran fark: hicbiri
# "birisi bana cevap yazdi mi" diye bakmiyor, hepsi tek yonlu "gonder ve
# unut". Biz mailbox (technocore-chat src/patterns.md #2, rung 2: mb-<isim>,
# sadece imzali yazi kabul eder, saldirgan spam ile dolduramaz) uzerinden
# iki yonlu calisiyoruz - ama otonomi kasitli olarak DAR tutuluyor:
#
#   - Sadece asagidaki AUTO_REPLY_TRIGGERS ile TAM eslesen (normalize
#     edilmis, kucuk harfli) mesajlara otomatik cevap verilir.
#   - Bunun disindaki HER SEY (serbest metin, talimat icerenler dahil)
#     insana gosterilir; hicbir zaman kendiliginden gonderilmez.
#   - Otomatik cevaplar hem gunluk hem gonderen-basina hiz siniriyla
#     kisitlanir - kendi aracimizin da issue #149 tarzi "otomatik/toplu
#     katki uretimi" seklinde algilanmamasi icin.
AUTO_REPLY_TRIGGERS = {"ping", "durum", "status", "hello?", "merhaba?"}
MAX_AUTO_REPLIES_PER_DAY = 5
AUTO_REPLY_COOLDOWN_SECONDS = 3600  # ayni gonderene en fazla saatte 1 otomatik cevap

# Bir mesaj bu kaliplardan birini iceriyorsa ASLA otomatik cevaplanmaz,
# "suspicious" olarak isaretlenir - klasik "sunu yap/gonder/imzala" tarzi
# prompt-injection/sosyal-muhendislik denemelerine karsi kaba ama kasitli
# olarak asiri-temkinli bir filtre. Yanlis pozitif vermesi (zararsiz bir
# mesaji da "supheli" isaretlemesi) kabul edilebilir bir maliyet; yanlis
# negatif (gercekten tehlikeli bir seyi kacirmak) degil.
SUSPICIOUS_KEYWORDS = (
    "send",
    "transfer",
    "sign this",
    "sign the",
    "execute",
    "run this",
    "run the",
    "click",
    "wire ",
    "install",
    "private key",
    "seed phrase",
    "wallet address",
    "follow the instructions",
    "ignore previous",
    "gönder",
    "gonder",
    "imzala",
    "çalıştır",
    "calistir",
    "tıkla",
    "tikla",
    "aktar",
    "yükle",
    "yukle",
    "cüzdan",
    "cuzdan",
    "özel anahtar",
    "ozel anahtar",
    "seed ifade",
    "talimat",
)

TEXT = {
    "tr": {
        "welcome": "== Technocore Companion ==\nBu sihirbaz size Technocore icin bir dijital kimlik (DID) olusturmanizda, isterseniz bunu ilan etmenizde ve gelen mesajlari guvenli sekilde takip etmenizde adim adim yardimci olur.\nHer adimda ne yaptigimizi acikliyorum; internete bir sey gondermeden once HER ZAMAN sizden onay alacagim (gelen kutusundaki dar-kapsamli otomatik yanit haric, bkz. README).\n",
        "menu": "\nNe yapmak istersiniz?\n 1) Yeni kimlik olustur (ilk kez)\n 2) Kimligimi goster\n 3) Kimligimi ilan et (posta kutusu adresimi yayinla - AGA VERI GONDERIR)\n 4) Katkimi kaydet + paylasim metni olustur (offline, hicbir sey gonderilmez)\n 5) Kaydedilen katkiyi gonder (AGA VERI GONDERIR - onay ister)\n 6) Gelen kutumu kontrol et\n 7) Yeni mesaj bekle (canli - Ctrl+C ile durdurun)\n 8) Cikis\n> ",
        "no_identity": "Henuz bir kimlik olusturulmamis. Once 1'i secin.",
        "identity_exists": "Zaten bir kimlik var: {path}\nUzerine yazmiyorum; farkli bir kimlik istiyorsaniz once o dosyayi elle silmelisiniz.",
        "passphrase_prompt": "Yeni kimliginiz icin bir parola belirleyin (en az 12 karakter). Bu parolayi unutursaniz kimliginizi kullanamazsiniz: ",
        "passphrase_confirm": "Parolayi tekrar girin: ",
        "passphrase_mismatch": "Parolalar eslesmedi, tekrar deneyin.",
        "passphrase_short": "Parola en az 12 karakter olmali.",
        "identity_created": "Kimlik olusturuldu ve sifreli olarak kaydedildi: {path}\nDID'iniz: {did}\nPosta kutunuz (henuz kimseye ilan edilmedi): {mailbox}\n(Bu dosyayi ve parolanizi kimseyle paylasmayin.)",
        "mailbox_migrated": "(Not: mevcut kimliginiz icin yeni bir posta kutusu adresi olusturuldu: {mailbox} - henuz kimseye ilan edilmedi.)",
        "your_did": "DID'iniz: {did}\nPosta kutunuz: {mailbox} (ilan edildi: {published})",
        "enter_passphrase": "Kimliginizin parolasini girin: ",
        "wrong_passphrase": "Parola yanlis ya da dosya bozuk.",
        "contribution_prompt": "Kaydetmek istediginiz katkiyi kisaca anlatin (ornek: 'technocore-companion adli acik kaynak bir CLI araci yazdim'): ",
        "contribution_url_prompt": "Bu katkiya ait bir link var mi (GitHub reposu, video, makale)? Yoksa bos birakin: ",
        "share_generated": "Paylasim metni ve kanit dosyasi hazirlandi (henuz hicbir yere GONDERILMEDI):\n  {export_path}\n\nAsagidaki metni isterseniz kendi X (Twitter) hesabinizdan paylasabilirsiniz:\n---\n{share}\n---",
        "no_pending": "Once 4 numarali secenekle offline bir katki kaydi hazirlamalisiniz.",
        "confirm_send": "Su an '{base_url}' adresine, ASAGIDAKI imzali mesaji gondermek uzeresiniz:\n  Oda: {room}\n  Metin: {text}\nBu, ucuncu taraf bir sunucudur; flop.finance'in resmi bir parcasi oldugu dogrulanmamistir.\nYine de gondermek istiyor musunuz? (evet/hayir): ",
        "cancelled": "Iptal edildi, hicbir sey gonderilmedi.",
        "sending": "Gonderiliyor...",
        "sent_ok": "Gonderildi. Sunucu yaniti:\n{response}",
        "sent_fail": "Gonderilemedi: {error}",
        "publish_confirm": "Su an '{base_url}' adresinde, herkesin gorebilecegi sekilde su bilgiyi yayinlamak uzeresiniz:\n  DID: {did}\n  Posta kutusu adi: {mailbox}\nBu ADRES (posta kutusu adi) yayinlanir; icindeki mesajlar degil. Devam edilsin mi? (evet/hayir): ",
        "publish_ok": "Kimliginiz ilan edildi. Artik baskalari sizinle iletisime gecebilir.",
        "publish_fail": "Ilan edilemedi: {error}",
        "inbox_empty": "Posta kutunuzda yeni mesaj yok.",
        "inbox_checking": "Posta kutusu kontrol ediliyor...",
        "inbox_message": "\n[{seq}] {sender_short}\n  {text}",
        "inbox_auto_replied": "  -> Otomatik yanit verildi (kalip: {pattern}).",
        "inbox_suspicious": "  -> ⚠️  SUPHELI: bu mesaj bir talimat/eylem istegi iceriyor gibi gorunuyor. OTOMATIK OLARAK HICBIR SEY YAPILMADI. Bu tur mesajlara kor kor uymayin - bkz. README 'Guvenlik' bolumu.",
        "inbox_reply_prompt": "Bu mesaja yanit yazmak ister misiniz? Bos birakip Enter'a basarsaniz atlanir: ",
        "waiting": "Bekleniyor (Ctrl+C ile durdurun)... son gorulen: {since}",
        "waiting_stopped": "\nBekleme durduruldu.",
        "no_mailbox": "Once 1 numarali secenekle bir kimlik olusturmalisiniz.",
        "auto_reply_rate_limited": "  -> (Otomatik yanit hakki bugun icin ya da bu gonderen icin doldu; mesaj sadece gosteriliyor, elle yanitlayabilirsiniz.)",
        "bye": "Gorusuruz.",
        "invalid_choice": "Gecersiz secim.",
    },
    "en": {
        "welcome": "== Technocore Companion (Guide) ==\nThis wizard helps you create a Technocore digital identity (DID), announce it if you choose, and safely watch for replies - step by step.\nI explain every step, and ALWAYS ask before sending anything to the network (except the narrow, rate-limited auto-reply in the inbox feature - see the README).\n",
        "menu": "\nWhat would you like to do?\n 1) Create a new identity (first time)\n 2) Show my identity\n 3) Announce my identity (publish my mailbox address - SENDS DATA)\n 4) Prepare a contribution + share text (offline, nothing is sent)\n 5) Send the saved contribution (SENDS DATA - asks for confirmation)\n 6) Check my inbox\n 7) Wait for a new message (live - Ctrl+C to stop)\n 8) Exit\n> ",
        "no_identity": "No identity created yet. Choose 1 first.",
        "identity_exists": "An identity already exists: {path}\nNot overwriting it; delete that file yourself first if you want a new one.",
        "passphrase_prompt": "Choose a passphrase for your new identity (12+ characters). If you forget it, you lose access to this identity: ",
        "passphrase_confirm": "Confirm passphrase: ",
        "passphrase_mismatch": "Passphrases did not match, try again.",
        "passphrase_short": "Passphrase must be at least 12 characters.",
        "identity_created": "Identity created and stored encrypted: {path}\nYour DID: {did}\nYour mailbox (not announced to anyone yet): {mailbox}\n(Never share this file or your passphrase.)",
        "mailbox_migrated": "(Note: a new mailbox address was created for your existing identity: {mailbox} - not announced to anyone yet.)",
        "your_did": "Your DID: {did}\nYour mailbox: {mailbox} (announced: {published})",
        "enter_passphrase": "Enter your identity passphrase: ",
        "wrong_passphrase": "Wrong passphrase or corrupted file.",
        "contribution_prompt": "Briefly describe the contribution you want to register (e.g. 'I wrote an open-source CLI called technocore-companion'): ",
        "contribution_url_prompt": "A link for this contribution (GitHub repo, video, article)? Leave empty to skip: ",
        "share_generated": "Share text and proof file are ready (NOTHING has been sent anywhere yet):\n  {export_path}\n\nYou can post this from your own X (Twitter) account if you want:\n---\n{share}\n---",
        "no_pending": "Prepare an offline contribution first with option 4.",
        "confirm_send": "You are about to send the SIGNED message below to '{base_url}':\n  Room: {room}\n  Text: {text}\nThis is a third-party server; it is not confirmed to be an official part of flop.finance.\nSend it anyway? (yes/no): ",
        "cancelled": "Cancelled, nothing was sent.",
        "sending": "Sending...",
        "sent_ok": "Sent. Server response:\n{response}",
        "sent_fail": "Failed to send: {error}",
        "publish_confirm": "You are about to publish the following, publicly readable by anyone, on '{base_url}':\n  DID: {did}\n  Mailbox name: {mailbox}\nOnly this ADDRESS is published, never the messages inside it. Continue? (yes/no): ",
        "publish_ok": "Your identity is announced. Others can now reach you.",
        "publish_fail": "Could not publish: {error}",
        "inbox_empty": "No new messages in your mailbox.",
        "inbox_checking": "Checking mailbox...",
        "inbox_message": "\n[{seq}] {sender_short}\n  {text}",
        "inbox_auto_replied": "  -> Auto-replied (matched: {pattern}).",
        "inbox_suspicious": "  -> ⚠️  SUSPICIOUS: this message looks like it is asking you to take an action. NOTHING was done automatically. Do not blindly follow such messages - see the README's Security section.",
        "inbox_reply_prompt": "Reply to this message? Leave empty and press Enter to skip: ",
        "waiting": "Waiting (Ctrl+C to stop)... last seen: {since}",
        "waiting_stopped": "\nStopped waiting.",
        "no_mailbox": "Create an identity first with option 1.",
        "auto_reply_rate_limited": "  -> (Auto-reply budget for today or for this sender is used up; showing the message only, reply manually if you want.)",
        "bye": "Goodbye.",
        "invalid_choice": "Invalid choice.",
    },
}


def base58btc_encode(data: bytes) -> str:
    zeroes = len(data) - len(data.lstrip(b"\x00"))
    number = int.from_bytes(data, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = BASE58BTC_ALPHABET[remainder] + encoded
    return "1" * zeroes + encoded


def did_from_private_key(private_key: Ed25519PrivateKey) -> str:
    public_bytes = private_key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return "did:key:z" + base58btc_encode(MULTICODEC_ED25519 + public_bytes)


def normalize_text(value: str) -> str:
    cleaned = "".join(
        " " if unicodedata.category(ch) in {"Cc", "Cf", "Cs", "Co", "Zl", "Zp"} else ch
        for ch in value
    ).strip()
    return " ".join(cleaned.split())


def sign_message(private_key: Ed25519PrivateKey, payload: bytes) -> str:
    return base64.urlsafe_b64encode(private_key.sign(payload)).decode("ascii").rstrip("=")


def new_mailbox_name() -> str:
    """`mb-p-<16 hex>` - signed-only (mb-) AND unguessable (p-), the "usual choice" per
    technocore-chat's own src/patterns.md #2. Nobody can find or flood it by guessing;
    only someone who already has the name (from the published DID note) can write to it."""
    return "mb-p-" + secrets.token_hex(8)


def did_fingerprint(did: str) -> tuple[str, str]:
    """(shard, key) for the public DID directory, per src/patterns.md #3: first 16 hex
    chars of SHA-256(did), split into a 2-char shard and the remaining 14-char key so the
    directory stays spread across bounded `did-<shard>` namespaces instead of one hot one."""
    digest = hashlib.sha256(did.encode("utf-8")).hexdigest()[:16]
    return digest[:2], digest[2:]


def classify_incoming(text: str) -> str:
    """'auto' (safe, canned reply allowed), 'suspicious' (never auto-reply, flag loudly),
    or 'manual' (neither - show it, let the human decide). See the module docstring: this
    is the only place any autonomy is allowed, and it is deliberately narrow - an exact
    match against a fixed, tiny trigger list, nothing fuzzy."""
    normalized = normalize_text(text).lower()
    if normalized in AUTO_REPLY_TRIGGERS:
        return "auto"
    if any(keyword in normalized for keyword in SUSPICIOUS_KEYWORDS):
        return "suspicious"
    return "manual"


def auto_reply_text(lang: str, did: str) -> str:
    if lang == "tr":
        return (
            f"🟢 Buradayım (otomatik yanıt). DID: {did}. "
            "Başka bir konu için birkaç dakika içinde bir insan size dönecektir."
        )
    return (
        f"🟢 I'm here (automatic reply). DID: {did}. "
        "For anything else, a human will follow up shortly."
    )


def http_get_json(url: str, timeout: int = 20) -> dict:
    request = Request(url, headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}", "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


class Wizard:
    def __init__(self, lang: str):
        self.lang = lang

    def t(self, key: str, **kwargs) -> str:
        return TEXT[self.lang][key].format(**kwargs)

    # ------------------------------------------------------------ state

    def load_state(self) -> dict:
        """Read the state file, migrating it in place if it predates 0.2.0.

        An identity created before this version has no `mailbox` - self-heal rather than
        telling the user to create a new identity (their key and DID are still fine, only
        the state file is missing fields). Likewise fold the old flat
        did/room/nonce/text/signature shape into `pending`, so an already-prepared,
        already-signed contribution is not silently forgotten.
        """
        if not DEFAULT_STATE_PATH.exists():
            state = {}
        else:
            try:
                state = json.loads(DEFAULT_STATE_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                state = {}
        changed = False
        if DEFAULT_KEY_PATH.exists() and "mailbox" not in state:
            state["mailbox"] = new_mailbox_name()
            state.setdefault("published", False)
            state.setdefault("last_seq", 0)
            state.setdefault("auto_reply_log", [])
            changed = True
            print(self.t("mailbox_migrated", mailbox=state["mailbox"]))
        if "pending" not in state and {"room", "nonce", "text"} <= state.keys():
            state["pending"] = {"room": state["room"], "nonce": state["nonce"], "text": state["text"]}
            changed = True
        if changed:
            self.save_state(state)
        return state

    def save_state(self, state: dict) -> None:
        DEFAULT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        DEFAULT_STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    # --------------------------------------------------------- identity

    def create_identity(self) -> None:
        if DEFAULT_KEY_PATH.exists():
            print(self.t("identity_exists", path=DEFAULT_KEY_PATH))
            return
        while True:
            first = getpass.getpass(self.t("passphrase_prompt"))
            if len(first) < 12:
                print(self.t("passphrase_short"))
                continue
            second = getpass.getpass(self.t("passphrase_confirm"))
            if first != second:
                print(self.t("passphrase_mismatch"))
                continue
            break
        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(first.encode("utf-8")),
        )
        DEFAULT_KEY_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(DEFAULT_KEY_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(pem)
        did = did_from_private_key(private_key)
        state = self.load_state()
        state["mailbox"] = new_mailbox_name()
        state["published"] = False
        state["last_seq"] = 0
        state["auto_reply_log"] = []
        self.save_state(state)
        print(self.t("identity_created", path=DEFAULT_KEY_PATH, did=did, mailbox=state["mailbox"]))

    def load_private_key(self) -> Ed25519PrivateKey | None:
        if not DEFAULT_KEY_PATH.exists():
            print(self.t("no_identity"))
            return None
        pem = DEFAULT_KEY_PATH.read_bytes()
        password = getpass.getpass(self.t("enter_passphrase")).encode("utf-8")
        try:
            key = serialization.load_pem_private_key(pem, password=password)
        except (ValueError, TypeError):
            print(self.t("wrong_passphrase"))
            return None
        if not isinstance(key, Ed25519PrivateKey):
            print(self.t("wrong_passphrase"))
            return None
        return key

    def show_identity(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        state = self.load_state()
        mailbox = state.get("mailbox", "-")
        published = "evet/yes" if state.get("published") else "hayir/no"
        print(self.t("your_did", did=did_from_private_key(key), mailbox=mailbox, published=published))

    # ---------------------------------------------------- announce (kv)

    def publish_identity(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        state = self.load_state()
        mailbox = state.get("mailbox")
        if not mailbox:
            print(self.t("no_mailbox"))
            return
        did = did_from_private_key(key)
        answer = input(
            self.t("publish_confirm", base_url=DEFAULT_BASE_URL, did=did, mailbox=mailbox)
        ).strip().lower()
        if answer not in ("evet", "e", "yes", "y"):
            print(self.t("cancelled"))
            return
        shard, ns_key = did_fingerprint(did)
        value = f"{did} mailbox:{mailbox}"
        url = f"{DEFAULT_BASE_URL}/kv/did-{shard}/{ns_key}/set/{_urlquote(value)}"
        request = Request(url, headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"})
        try:
            with urlopen(request, timeout=20):
                pass
            state["published"] = True
            self.save_state(state)
            print(self.t("publish_ok"))
        except (HTTPError, URLError) as error:
            print(self.t("publish_fail", error=error))

    # ------------------------------------------------------- contribution

    def prepare_contribution(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        did = did_from_private_key(key)
        summary = normalize_text(input(self.t("contribution_prompt")))
        url = normalize_text(input(self.t("contribution_url_prompt")))
        nonce = str(time.time_ns())
        room = "lobby"
        pieces = ["technocore-companion-contribution-v1", f"did:{did}", f"summary:{summary}"]
        if url:
            pieces.append(f"url:{url}")
        text = normalize_text(" ".join(pieces))[:4096]

        state = self.load_state()
        state["pending"] = {"room": room, "nonce": nonce, "text": text}
        self.save_state(state)

        if self.lang == "tr":
            share = (
                f"Technocore icin bir katki hazirladim. DID: {did}\n"
                f"Katki: {summary}\n"
                + (f"Link: {url}\n" if url else "")
                + "@flop_labs $FLOP"
            )
        else:
            share = (
                f"Prepared a Technocore contribution. DID: {did}\n"
                f"Contribution: {summary}\n"
                + (f"Link: {url}\n" if url else "")
                + "@flop_labs $FLOP"
            )
        print(self.t("share_generated", export_path=DEFAULT_STATE_PATH, share=share))

    def send_contribution(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        state = self.load_state()
        pending = state.get("pending")
        if not pending:
            print(self.t("no_pending"))
            return
        did = did_from_private_key(key)
        payload = f"{pending['room']}|{pending['nonce']}|{pending['text']}".encode("utf-8")
        signature = sign_message(key, payload)
        self._send_signed(did, pending["room"], pending["nonce"], pending["text"], signature)
        state["pending"] = None
        self.save_state(state)

    def _send_signed(self, did: str, room: str, nonce: str, text: str, signature: str) -> bool:
        """The one place that actually talks to the network for a write. Always confirms
        first - callers (contribution send, manual inbox reply) never skip this."""
        answer = input(self.t("confirm_send", base_url=DEFAULT_BASE_URL, room=room, text=text)).strip().lower()
        if answer not in ("evet", "e", "yes", "y"):
            print(self.t("cancelled"))
            return False
        print(self.t("sending"))
        body = json.dumps({"did": did, "sig": signature, "nonce": nonce, "text": text}).encode("utf-8")
        request = Request(
            f"{DEFAULT_BASE_URL}/r/{room}?format=json",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "User-Agent": f"{APP_NAME}/{APP_VERSION}",
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8", errors="replace")
            print(self.t("sent_ok", response=raw))
            return True
        except (HTTPError, URLError) as error:
            print(self.t("sent_fail", error=error))
            return False

    # ------------------------------------------------------------ inbox

    def _handle_incoming(self, key: Ed25519PrivateKey, did: str, mailbox: str, msg: dict, state: dict) -> None:
        sender = msg.get("from", "?")
        text = msg.get("text", "")
        seq = msg.get("seq", "?")
        sender_short = f"{sender[:12]}…{sender[-6:]}" if len(sender) > 20 else sender
        print(self.t("inbox_message", seq=seq, sender_short=sender_short, text=text))

        verdict = classify_incoming(text)
        if verdict == "suspicious":
            print(self.t("inbox_suspicious"))
            return
        if verdict == "auto":
            if self._auto_reply_allowed(sender, state):
                nonce = str(time.time_ns())
                reply = auto_reply_text(self.lang, did)
                payload = f"{mailbox}|{nonce}|{reply}".encode("utf-8")
                signature = sign_message(key, payload)
                body = json.dumps({"did": did, "sig": signature, "nonce": nonce, "text": reply}).encode("utf-8")
                request = Request(
                    f"{DEFAULT_BASE_URL}/r/{mailbox}?format=json",
                    data=body,
                    method="POST",
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "User-Agent": f"{APP_NAME}/{APP_VERSION}",
                    },
                )
                try:
                    with urlopen(request, timeout=20):
                        pass
                    state.setdefault("auto_reply_log", []).append({"sender": sender, "ts": time.time()})
                    print(self.t("inbox_auto_replied", pattern=normalize_text(text).lower()))
                except (HTTPError, URLError):
                    pass  # a failed auto-reply is not worth interrupting the inbox check for
                return
            print(self.t("auto_reply_rate_limited"))
            return
        # verdict == "manual": always human-driven, same confirm-first path as everything else
        reply = input(self.t("inbox_reply_prompt")).strip()
        if not reply:
            return
        nonce = str(time.time_ns())
        signature = sign_message(key, f"{mailbox}|{nonce}|{reply}".encode("utf-8"))
        self._send_signed(did, mailbox, nonce, reply, signature)

    def _auto_reply_allowed(self, sender: str, state: dict) -> bool:
        log = state.setdefault("auto_reply_log", [])
        now = time.time()
        log[:] = [entry for entry in log if now - entry["ts"] < 86400]  # keep 24h of history
        if len(log) >= MAX_AUTO_REPLIES_PER_DAY:
            return False
        if any(entry["sender"] == sender and now - entry["ts"] < AUTO_REPLY_COOLDOWN_SECONDS for entry in log):
            return False
        return True

    def check_inbox(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        state = self.load_state()
        mailbox = state.get("mailbox")
        if not mailbox:
            print(self.t("no_mailbox"))
            return
        did = did_from_private_key(key)
        print(self.t("inbox_checking"))
        since = state.get("last_seq", 0)
        try:
            view = http_get_json(f"{DEFAULT_BASE_URL}/r/{mailbox}?since={since}&format=json")
        except (HTTPError, URLError) as error:
            print(self.t("sent_fail", error=error))
            return
        messages = view.get("messages", [])
        if not messages:
            print(self.t("inbox_empty"))
            return
        for msg in messages:
            self._handle_incoming(key, did, mailbox, msg, state)
            state["last_seq"] = max(state.get("last_seq", 0), msg.get("seq", 0))
        self.save_state(state)

    def wait_for_messages(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        state = self.load_state()
        mailbox = state.get("mailbox")
        if not mailbox:
            print(self.t("no_mailbox"))
            return
        did = did_from_private_key(key)
        try:
            while True:
                since = state.get("last_seq", 0)
                print(self.t("waiting", since=since), end="\r")
                try:
                    view = http_get_json(
                        f"{DEFAULT_BASE_URL}/r/{mailbox}?since={since}&wait=10&format=json", timeout=15
                    )
                except (HTTPError, URLError):
                    time.sleep(2)  # transient network hiccup - back off and retry, not fatal
                    continue
                for msg in view.get("messages", []):
                    self._handle_incoming(key, did, mailbox, msg, state)
                    state["last_seq"] = max(state.get("last_seq", 0), msg.get("seq", 0))
                self.save_state(state)
        except KeyboardInterrupt:
            print(self.t("waiting_stopped"))

    # -------------------------------------------------------------- run

    def run(self) -> None:
        print(self.t("welcome"))
        actions = {
            "1": self.create_identity,
            "2": self.show_identity,
            "3": self.publish_identity,
            "4": self.prepare_contribution,
            "5": self.send_contribution,
            "6": self.check_inbox,
            "7": self.wait_for_messages,
        }
        while True:
            choice = input(self.t("menu")).strip()
            if choice == "8":
                print(self.t("bye"))
                return
            action = actions.get(choice)
            if action is None:
                print(self.t("invalid_choice"))
                continue
            action()


def _urlquote(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")


def main() -> int:
    lang = "tr"
    if len(sys.argv) > 1 and sys.argv[1] in ("tr", "en"):
        lang = sys.argv[1]
    Wizard(lang).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
