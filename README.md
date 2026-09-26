
# GEMA
<img width="1916" height="1007" alt="Screenshot 2026-09-25 123525" src="https://github.com/user-attachments/assets/991ddb80-b1fb-4df3-8eeb-8d9a3081f1bf" />
*by v.obscura*

A top-down psychological horror game made with pygame. In a maze of total darkness, to see is to be heard.

You wake up in a dark maze with an old flashlight and a sonar device. The sonar shows you the way, but the things down here hunt by sound. Find the three fragments on each floor, then find the way out.

The game is in **English** and **Bahasa Indonesia**. On first launch it follows your system language; you can change it any time in **Settings**.

## Download (Windows)

Grab the latest `GEMA-v<version>-windows.zip` from [Releases](https://github.com/reinyako/GEMA/releases), extract it, and run `GEMA.exe`. No Python needed.

> `GEMA.exe` isn't digitally signed, so Windows SmartScreen may show "Windows protected your PC". Click **More info**, then **Run anyway**.

## Install (from source)

Requires **Python 3.10 or newer**.

```bash
pip install -r requirements.txt
```

> If you already have regular `pygame` installed, uninstall it first with `pip uninstall pygame`. GEMA uses `pygame-ce`, and both use the same module name.

## How to play

```bash
python main.py
```

**Wear headphones.** Half of this game is in its sound, and where a sound comes from (left or right) matters.

| Key | Action |
|---|---|
| `W` `A` `S` `D` | Move (walking is quiet) |
| `Shift` (hold) | Run: fast but loud |
| Mouse | Aim the flashlight |
| Left click (hold) | Flashlight |
| Right click / `Space` | Sonar |
| `Q` | Throw a stone: the sound draws them to where it lands |
| `E` (hold) | Break the wall in front of you: opens a way through, but loudly |
| `Esc` | Pause (lives, stones left, and the notes you've found) |
| `F11` | Fullscreen |

### A few things to know

- Standing still is silent. Walking is quiet. Running can be heard from far away.
- The sonar lets you see, but every ping can be heard.
- Your flashlight makes them stop. Not leave.
- Batteries don't refill between floors. Stones and wall breaks do.
- There are three difficulties: **Dim**, **Dark**, and **Pitch Black**. On Dim, losing all your lives restarts the floor with a new maze instead of sending you back to the start.
- There are 14 achievements. See **Achievements** on the title screen.

### Other options

| Option | What it does |
|---|---|
| `python main.py --floor 4` | Start on Floor 4 |
| `python main.py --seed 123` | Same maze every time (include the seed when you report a bug) |
| `python main.py --difficulty pekat` | Preselect a difficulty: `redup` (Dim), `gelap` (Dark), `pekat` (Pitch Black) |
| `python main.py --lang en` | Language for this session (`en` or `id`), without changing your setting |
| `python main.py --mute` | No sound |
| `python main.py --dev` | Dev mode for testing: a menu for invincibility, no sonar cooldown, unlimited flashlight, and unlimited stones & walls. While playing: `F3` debug overlay (map, monster states, stress, battery, FPS), `F5` collect every fragment, `F6` jump to the exit |

Options can be combined, for example `python main.py --dev --floor 5`. Runs that use dev mode or don't start on Floor 1 don't earn achievements.

Your save data (attempts, deaths, endings, achievements, language, and the note you leave at the end) lives in `~/.gema/save.json`. Delete it to start over.

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests run without a window or sound. One of them has a bot play from Floor 1 all the way to the ending.

For headless screenshots (handy when tuning visuals):

```bash
python tools/snap.py --floor 3 --light --ping --near --stress 90 --out shots/example.png
```

## Building GEMA.exe

On Windows:

```bash
pip install -r requirements-build.txt
python tools/build_exe.py
```

The script draws the icon, packages the game with PyInstaller, runs `GEMA.exe --selftest`, and creates `dist/GEMA-v<version>-windows.zip`, ready to upload to Releases. The version comes from `gema/__init__.py`.

The icon is drawn in code ([`gema/render/icon.py`](gema/render/icon.py)), like every other visual in the game.

## Documents

The design documents are written in Indonesian:

- [Game Design Document](docs/GDD.md): concept, mechanics, horror systems, story, visuals, and audio
- [Development plan](docs/PLAN.md): architecture, milestones, testing strategy, and playtest checklist

All the tuning numbers (speeds, battery, stress, and so on) live in one file: [`gema/config.py`](gema/config.py). All the in-game text lives in [`gema/text_en.py`](gema/text_en.py) and [`gema/text_id.py`](gema/text_id.py); adding a language means adding another file like these.
