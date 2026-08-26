# technocore-companion

[🇹🇷 Türkçe](README.md) | 🇬🇧 English

A beginner-friendly, menu-driven **Technocore `did:key` wizard** that even
a complete non-technical user can follow step by step. It runs in a plain
terminal, never opens a browser or local web server, and your identity's
private key is always kept encrypted on disk — it is never printed to the
screen or sent over the network in plaintext.

> ⚠️ **Important:** `technocore.chat` is a "satellite service" published by
> Flop Labs on its official GitHub organization
> (`github.com/flop-labs/technocore-chat`) — not part of the core protocol,
> but officially run by Flop Labs itself. That said, this tool does **not**
> guarantee any reward or airdrop eligibility — that is entirely at Flop
> Labs' discretion. Before sending anything over the network, the tool
> always shows you exactly what will be sent and asks for confirmation.

---

## Table of contents

1. [Requirements](#1-requirements)
2. [Updating your system](#2-updating-your-system)
3. [Installation](#3-installation)
4. [Usage](#4-usage)
5. [Example run](#5-example-run)
6. [Inbox and limited auto-reply](#6-inbox-and-limited-auto-reply)
7. [Why this tool is safe](#7-why-this-tool-is-safe)
8. [FAQ](#8-faq)
9. [Contributing](#9-contributing)
10. [License](#10-license)

---

## 1) Requirements

This guide targets **Ubuntu / Debian-based** Linux distributions (Ubuntu
20.04+ recommended). You need:

- A terminal (open it on Ubuntu with `Ctrl+Alt+T`)
- An internet connection (only for setup and the optional step 4)
- About 5 minutes

The following packages will be installed automatically in the setup step
— just so you know what they're for:

| Package | What it's for |
|---|---|
| `python3` | The language the tool is written in |
| `python3-venv` | Keeps dependencies in an isolated environment |
| `python3-pip` | Installs Python packages |
| `git` | Downloads (clones) this repository to your computer |

## 2) Updating your system

It's always good practice to update your system before installing
anything new. Open a terminal and run these two commands in order:

```bash
sudo apt update
sudo apt upgrade -y
```

- `sudo` asks for administrator privileges; it will prompt for your
  system password. The characters won't show as you type — that's
  normal, just type it and press Enter.
- `apt update` refreshes the package lists (installs nothing yet).
- `apt upgrade -y` upgrades your existing packages. The `-y` flag
  automatically answers "yes" to confirmation prompts.

## 3) Installation

Now let's install the required packages and download this repository:

```bash
# Install the required system packages
sudo apt install -y python3 python3-venv python3-pip git

# Clone this repository to your computer
git clone https://github.com/<your-username>/technocore-companion.git
cd technocore-companion

# Create and activate an isolated Python environment (venv)
python3 -m venv .venv
source .venv/bin/activate

# Install the single Python package the tool needs
pip install -r requirements.txt
```

> 💡 You need to run `source .venv/bin/activate` again every time you
> open a new terminal in this folder. If your prompt shows `(.venv)` at
> the start, the environment is active.

## 4) Usage

To start the tool with the English menu:

```bash
python3 technocore_companion.py en
```

For the Turkish menu:

```bash
python3 technocore_companion.py tr
```

You'll see a menu like this:

```
What would you like to do?
 1) Create a new identity (first time)
 2) Show my identity
 3) Announce my identity (publish my mailbox address - SENDS DATA)
 4) Prepare a contribution + share text (offline, nothing is sent)
 5) Send the saved contribution (SENDS DATA - asks for confirmation)
 6) Check my inbox
 7) Wait for a new message (live - Ctrl+C to stop)
 8) Exit
```

Recommended order:

1. **`1` — Create a new identity:** You'll be asked for a passphrase
   (12+ characters). **Don't forget it and never share it** — it
   encrypts your identity and stores it at `~/.technocore/identity.pem`.
   It also generates a random, unguessable **mailbox address**
   (`mb-p-...`) for you at the same time — but does not tell anyone
   about it yet.
2. **`2` — Show my identity:** Prints your DID and your mailbox address.
3. **`3` — Announce my identity:** Publishes your mailbox address
   somewhere anyone can read, so others can reach you. **Only the
   address is published**, never what's inside the mailbox.
4. **`4` — Prepare a contribution:** Asks what you want to register as
   your contribution (for example, this repository if you wrote it),
   an optional link, then prepares a signed message and ready-to-post
   share text **entirely offline**. **Nothing is sent anywhere** at
   this step.
5. **`5` — Send:** This step actually sends data over the
   network. Before sending, it shows you *exactly* what will be sent
   and to which address, and explicitly asks `yes`/`no`. Type `no` to
   cancel if you don't want to proceed.
6. **`6` / `7` — Inbox:** see the section below.

## 5) Example run

```
$ python3 technocore_companion.py en

== Technocore Companion (Guide) ==
This wizard helps you create a Technocore digital identity (DID)...

What would you like to do?
> 1
Choose a passphrase for your new identity (12+ characters): ********
Confirm passphrase: ********
Identity created and stored encrypted: /home/user/.technocore/identity.pem
Your DID: did:key:z6MkvxJLotfEqBPjCnsinArfX1vEmRPKvwnPgGcKReYySaog
```

## 6) Inbox and limited auto-reply

This is what sets `technocore-companion` apart from every other
Technocore tool we know of: they are all **one-way** ("create identity,
post a message, done"). This tool can be **two-way** — you can find out
when someone writes back to you.

It uses Technocore's own "mailbox" (`mb-`) mechanism: it only accepts
**signed** messages (from a provable identity), and its name is
unguessable (`mb-p-<random>`), so it cannot be flooded with spam. Only
people you've told (via step `3`) can find the address.

- **`6` — Check my inbox:** reads your mailbox once, shows new messages.
- **`7` — Wait for a new message:** stays open and prints a message
  **the instant** someone sends one. `Ctrl+C` to stop.

### Autonomy is LIMITED, on purpose

The tool can react to an incoming message in exactly three ways:

1. **Auto-reply** — ONLY when the message is an exact match for one of a
   short, fixed, harmless list of triggers (like `ping` or `status`), it
   sends back a canned "I'm here" reply. This is also capped, both
   **per day** and **per sender**.
2. **⚠️ Flagged as suspicious** — if the message looks like it's asking
   you to *do* something ("send", "sign", "run", "click", "wallet",
   "private key"...), the tool does **nothing automatically** and warns
   you loudly instead. **Do not blindly follow such messages** — this
   could be an attempt to trick you into an action (see the security
   note below).
3. **Left to you** — anything else is simply shown to you, with an
   optional prompt to write a reply by hand; **nothing is sent** unless
   you type it and confirm.

In other words, the tool never follows a "send/sign/download this"
instruction on its own, and never performs a complex action on your
behalf — the most it ever does automatically is say "I'm here." Everything
else stays your call.

## 7) Why this tool is safe

- **The private key is never written to disk in plaintext.** It's
  stored as a passphrase-encrypted PEM file (with `0600` permissions,
  meaning only you can read it).
- **No browser or local web server is opened.** Some similar tools pass
  the private key through a local API to the browser and let you
  download it as a plaintext file — this tool does not.
- **The steps that send data (`3`, `5`) always ask for explicit
  confirmation** and show the full content before sending.
- **Auto-reply is deliberately narrow** — see section 6 above. If a
  message asks the tool to send/sign/run something, it never complies
  on its own; it only warns you.
- The code is a single Python file (`technocore_companion.py`) — short,
  readable, with no hidden behavior; feel free to read it before
  installing anything.

## 8) FAQ

**I forgot my passphrase, what do I do?**
Unfortunately there's no way to open an encrypted identity file without
its passphrase. Delete `~/.technocore/identity.pem` and create a new
identity with option `1`.

**Does this tool guarantee me an airdrop?**
No. This is only a tool that makes it easier to participate in the
Technocore protocol. Verifying any reward claim through flop.finance's
official channels is up to you.

**I get `command not found: python3`.**
Run `sudo apt install -y python3` and try again.

**My terminal doesn't show `(.venv)`, what now?**
Run `source .venv/bin/activate` again while inside the repo folder.

**My inbox refused to auto-reply, why?**
Either your daily auto-reply budget is used up, or that sender already
got an auto-reply too recently (a deliberate limit against spam/abuse).
You can still reply by hand.

## 9) Contributing

Found a bug or have an improvement idea? Open an Issue on GitHub, or
send a Pull Request directly.

## 10) License

[MIT](LICENSE) — free to use, modify, and distribute.
