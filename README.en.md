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
6. [Why this tool is safe](#6-why-this-tool-is-safe)
7. [FAQ](#7-faq)
8. [Contributing](#8-contributing)
9. [License](#9-license)

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
 3) Prepare a contribution + share text (offline, nothing is sent)
 4) Send the saved contribution to Technocore (SENDS DATA - asks for confirmation)
 5) Exit
```

Recommended order:

1. **`1` — Create a new identity:** You'll be asked for a passphrase
   (12+ characters). **Don't forget it and never share it** — it
   encrypts your identity and stores it at `~/.technocore/identity.pem`.
2. **`2` — Show my identity:** Prints the DID (digital identifier) you
   just created, e.g. `did:key:z6Mk...`
3. **`3` — Prepare a contribution:** Asks what you want to register as
   your contribution (for example, this repository if you wrote it),
   an optional link, then prepares a signed message and ready-to-post
   share text **entirely offline**. **Nothing is sent anywhere** at
   this step.
4. **`4` — Send to Technocore:** This step actually sends data over the
   network. Before sending, it shows you *exactly* what will be sent
   and to which address, and explicitly asks `yes`/`no`. Type `no` to
   cancel if you don't want to proceed.

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

## 6) Why this tool is safe

- **The private key is never written to disk in plaintext.** It's
  stored as a passphrase-encrypted PEM file (with `0600` permissions,
  meaning only you can read it).
- **No browser or local web server is opened.** Some similar tools pass
  the private key through a local API to the browser and let you
  download it as a plaintext file — this tool does not.
- **The only step that sends data (`4`) always asks for explicit
  confirmation** and shows the full content before sending.
- The code is a single Python file (`technocore_companion.py`) — short,
  readable, with no hidden behavior; feel free to read it before
  installing anything.

## 7) FAQ

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

## 8) Contributing

Found a bug or have an improvement idea? Open an Issue on GitHub, or
send a Pull Request directly.

## 9) License

[MIT](LICENSE) — free to use, modify, and distribute.
