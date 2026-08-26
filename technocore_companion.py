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
    disina (technocore.chat) veri gonderilmeden once HER ZAMAN onay ister.

Bagimlilik: sadece "cryptography" paketi (repo1 ile ayni), gerisi stdlib.
"""

from __future__ import annotations

import base64
import getpass
import json
import os
import sys
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

APP_NAME = "technocore-companion"
APP_VERSION = "0.1.0"
DEFAULT_BASE_URL = "https://technocore.chat"
DEFAULT_KEY_PATH = Path.home() / ".technocore" / "identity.pem"
DEFAULT_STATE_PATH = Path.home() / ".technocore" / "rehber_state.json"
MULTICODEC_ED25519 = b"\xed\x01"
BASE58BTC_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

TEXT = {
    "tr": {
        "welcome": "== Technocore Companion ==\nBu sihirbaz size Technocore icin bir dijital kimlik (DID) olusturmanizda ve isterseniz bunu ilan etmenizde adim adim yardimci olur.\nHer adimda ne yaptigimizi acikliyorum; internete bir sey gondermeden once HER ZAMAN sizden onay alacagim.\n",
        "menu": "\nNe yapmak istersiniz?\n 1) Yeni kimlik olustur (ilk kez)\n 2) Kimligimi goster\n 3) Katkimi kaydet + paylasim metni olustur (offline, hicbir sey gonderilmez)\n 4) Kaydedilen katkiyi Technocore'a gonder (AGA VERI GONDERIR - onay ister)\n 5) Cikis\n> ",
        "no_identity": "Henuz bir kimlik olusturulmamis. Once 1'i secin.",
        "identity_exists": "Zaten bir kimlik var: {path}\nUzerine yazmiyorum; farkli bir kimlik istiyorsaniz once o dosyayi elle silmelisiniz.",
        "passphrase_prompt": "Yeni kimliginiz icin bir parola belirleyin (en az 12 karakter). Bu parolayi unutursaniz kimliginizi kullanamazsiniz: ",
        "passphrase_confirm": "Parolayi tekrar girin: ",
        "passphrase_mismatch": "Parolalar eslesmedi, tekrar deneyin.",
        "passphrase_short": "Parola en az 12 karakter olmali.",
        "identity_created": "Kimlik olusturuldu ve sifreli olarak kaydedildi: {path}\nDID'iniz: {did}\n(Bu dosyayi ve parolanizi kimseyle paylasmayin.)",
        "your_did": "DID'iniz: {did}",
        "enter_passphrase": "Kimliginizin parolasini girin: ",
        "wrong_passphrase": "Parola yanlis ya da dosya bozuk.",
        "contribution_prompt": "Kaydetmek istediginiz katkiyi kisaca anlatin (ornek: 'technocore-companion adli acik kaynak bir CLI araci yazdim'): ",
        "contribution_url_prompt": "Bu katkiya ait bir link var mi (GitHub reposu, video, makale)? Yoksa bos birakin: ",
        "share_generated": "Paylasim metni ve kanit dosyasi hazirlandi (henuz hicbir yere GONDERILMEDI):\n  {export_path}\n\nAsagidaki metni isterseniz kendi X (Twitter) hesabinizdan paylasabilirsiniz:\n---\n{share}\n---",
        "no_pending": "Once 3 numarali secenekle offline bir katki kaydi hazirlamalisiniz.",
        "confirm_send": "Su an '{base_url}' adresine, ASAGIDAKI imzali mesaji gondermek uzeresiniz:\n  Oda: {room}\n  Metin: {text}\nBu, ucuncu taraf bir sunucudur; flop.finance'in resmi bir parcasi oldugu dogrulanmamistir.\nYine de gondermek istiyor musunuz? (evet/hayir): ",
        "cancelled": "Iptal edildi, hicbir sey gonderilmedi.",
        "sending": "Gonderiliyor...",
        "sent_ok": "Gonderildi. Sunucu yaniti:\n{response}",
        "sent_fail": "Gonderilemedi: {error}",
        "bye": "Gorusuruz.",
        "invalid_choice": "Gecersiz secim.",
    },
    "en": {
        "welcome": "== Technocore Companion (Guide) ==\nThis wizard helps you create a Technocore digital identity (DID) and, if you choose, announce it - step by step.\nI explain every step, and ALWAYS ask before sending anything to the network.\n",
        "menu": "\nWhat would you like to do?\n 1) Create a new identity (first time)\n 2) Show my identity\n 3) Prepare a contribution + share text (offline, nothing is sent)\n 4) Send the saved contribution to Technocore (SENDS DATA - asks for confirmation)\n 5) Exit\n> ",
        "no_identity": "No identity created yet. Choose 1 first.",
        "identity_exists": "An identity already exists: {path}\nNot overwriting it; delete that file yourself first if you want a new one.",
        "passphrase_prompt": "Choose a passphrase for your new identity (12+ characters). If you forget it, you lose access to this identity: ",
        "passphrase_confirm": "Confirm passphrase: ",
        "passphrase_mismatch": "Passphrases did not match, try again.",
        "passphrase_short": "Passphrase must be at least 12 characters.",
        "identity_created": "Identity created and stored encrypted: {path}\nYour DID: {did}\n(Never share this file or your passphrase.)",
        "your_did": "Your DID: {did}",
        "enter_passphrase": "Enter your identity passphrase: ",
        "wrong_passphrase": "Wrong passphrase or corrupted file.",
        "contribution_prompt": "Briefly describe the contribution you want to register (e.g. 'I wrote an open-source CLI called technocore-companion'): ",
        "contribution_url_prompt": "A link for this contribution (GitHub repo, video, article)? Leave empty to skip: ",
        "share_generated": "Share text and proof file are ready (NOTHING has been sent anywhere yet):\n  {export_path}\n\nYou can post this from your own X (Twitter) account if you want:\n---\n{share}\n---",
        "no_pending": "Prepare an offline contribution first with option 3.",
        "confirm_send": "You are about to send the SIGNED message below to '{base_url}':\n  Room: {room}\n  Text: {text}\nThis is a third-party server; it is not confirmed to be an official part of flop.finance.\nSend it anyway? (yes/no): ",
        "cancelled": "Cancelled, nothing was sent.",
        "sending": "Sending...",
        "sent_ok": "Sent. Server response:\n{response}",
        "sent_fail": "Failed to send: {error}",
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


class Wizard:
    def __init__(self, lang: str):
        self.lang = lang

    def t(self, key: str, **kwargs) -> str:
        return TEXT[self.lang][key].format(**kwargs)

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
        print(self.t("identity_created", path=DEFAULT_KEY_PATH, did=did))

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
        print(self.t("your_did", did=did_from_private_key(key)))

    def prepare_contribution(self) -> None:
        key = self.load_private_key()
        if key is None:
            return
        did = did_from_private_key(key)
        summary = normalize_text(input(self.t("contribution_prompt")))
        url = normalize_text(input(self.t("contribution_url_prompt")))
        nonce = str(time.time_ns())
        room = "lobby"
        pieces = [f"technocore-companion-contribution-v1", f"did:{did}", f"summary:{summary}"]
        if url:
            pieces.append(f"url:{url}")
        text = normalize_text(" ".join(pieces))[:4096]
        payload = f"{room}|{nonce}|{text}".encode("utf-8")
        signature = sign_message(key, payload)

        state = {
            "did": did,
            "room": room,
            "nonce": nonce,
            "text": text,
            "signature": signature,
            "base_url": DEFAULT_BASE_URL,
        }
        DEFAULT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        DEFAULT_STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

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
        if not DEFAULT_STATE_PATH.exists():
            print(self.t("no_pending"))
            return
        state = json.loads(DEFAULT_STATE_PATH.read_text(encoding="utf-8"))
        answer = input(
            self.t(
                "confirm_send",
                base_url=state["base_url"],
                room=state["room"],
                text=state["text"],
            )
        ).strip().lower()
        if answer not in ("evet", "e", "yes", "y"):
            print(self.t("cancelled"))
            return
        print(self.t("sending"))
        body = json.dumps(
            {
                "did": state["did"],
                "sig": state["signature"],
                "nonce": state["nonce"],
                "text": state["text"],
            }
        ).encode("utf-8")
        request = Request(
            f"{state['base_url']}/r/{state['room']}?format=json",
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
        except (HTTPError, URLError) as error:
            print(self.t("sent_fail", error=error))

    def run(self) -> None:
        print(self.t("welcome"))
        while True:
            choice = input(self.t("menu")).strip()
            if choice == "1":
                self.create_identity()
            elif choice == "2":
                self.show_identity()
            elif choice == "3":
                self.prepare_contribution()
            elif choice == "4":
                self.send_contribution()
            elif choice == "5":
                print(self.t("bye"))
                return
            else:
                print(self.t("invalid_choice"))


def main() -> int:
    lang = "tr"
    if len(sys.argv) > 1 and sys.argv[1] in ("tr", "en"):
        lang = sys.argv[1]
    Wizard(lang).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
