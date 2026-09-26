"""Every piece of text the player sees, in English. Keys must match text_id.py."""

TEXT = {
    # --- title & menus ---------------------------------------------------
    "start": "Begin",
    "start_died": "You came back.",
    "start_ended": "You came back. Again.",
    "menu_dev": "Dev mode",
    "menu_achievements": "Achievements",
    "menu_settings": "Settings",
    "menu_quit": "Quit",
    "earphones": "Use headphones.",
    "back": "Back",
    "back_hint": "Esc: back",

    # --- difficulty ------------------------------------------------------
    "how_dark": "How dark?",
    "deepest": "   (deepest: Floor {n})",
    "finished_mark": "   (finished)",
    "difficulty": {
        "redup": ("Dim", "3 lives, and the floor restarts when they're gone. Less dark. They're slower."),
        "gelap": ("Dark", "2 lives. As it was meant to be."),
        "pekat": ("Pitch Black", "1 life. Don't expect much."),
    },

    # --- settings --------------------------------------------------------
    "settings_title": "Settings",
    "setting_language": "Language",

    # --- playing ---------------------------------------------------------
    "floor": "Floor {n}",
    "floor_final": "Floor",
    "attempt_over": "Attempt {n} is over.",
    "new_achievement": "New achievement: {name}",
    "pause": "Paused",
    "resume": "Resume",
    "notes": "Notes",
    "to_title": "Back to title",
    "notes_none": "None yet.",
    "tool_stones": "stones",
    "tool_walls": "walls",
    "controls": [
        ("WASD", "move"),
        ("Shift", "run (loud)"),
        ("Mouse", "aim the flashlight"),
        ("Hold left click", "flashlight"),
        ("Right click / Space", "sonar"),
        ("Q", "throw a stone"),
        ("Hold E", "break a wall (loud)"),
        ("Esc", "pause"),
        ("F11", "fullscreen"),
    ],

    # --- story -----------------------------------------------------------
    "notes_list": [
        # Floor 1
        "If you're reading this, the device still works. Good.",
        "The sonar shows you the way. But they hear it too. Use it sparingly.",
        "Light makes them stop. Not leave. Stop.",
        # Floor 2
        "They can't see. They listen. Don't run unless you have to.",
        "Something stands at the edge of the light. While you watch, it doesn't move.",
        None,  # dynamic: note_first_attempt / note_attempt
        # Floor 3
        "Don't trust your memory of the way. The walls move when no one is looking.",
        "The one standing at the edge of the light is harmless.",
        "Don't trust the note that says it's harmless.",
        # Floor 4
        "If you hear a ping you didn't make, it wasn't you.",
        "Not everything on the sonar is real. Not everything real shows up on the sonar.",
        "This looks like my handwriting. But I don't remember writing it.",
        # Floor 5
        "Have you noticed yet? It looks exactly like you.",
        "Everyone here once held this flashlight.",
        "The last door doesn't lead out. I'm opening it anyway. So will you.",
    ],
    "note_first_attempt": "This is the first attempt. At least, that's what it says.",
    "note_attempt": "This is attempt {n}. Don't run this time.",
    "note_again": "How many times have you read this sentence?",
    "ending_lines": [
        "First note.",
        "If you're reading this, the device still works.",
        "Good.",
    ],
    "death_words": ["Not yet.", "Again.", "Wake up."],
    # Dim: shown when a floor restarts. The more often on the same floor, the sharper it gets.
    "retry_words": [
        "You wake up again.",
        "Again.",
        "Are you tired?",
        "This place is learning your footsteps.",
        "They don't need to look for you anymore.",
        "The flashlight still works. Do you?",
    ],
    "retry_words_late": [
        "How many times now?",
        "Rest. No one is waiting.",
        "You're still here.",
    ],
    # (text, font size, bright?)
    "credits": [
        ("GEMA", 30, True),
        ("", 10, False),
        ("by v.obscura", 18, True),
        ("", 10, False),
        ("made with pygame-ce and numpy", 15, False),
        ("without a single image or sound file", 15, False),
    ],

    # --- ending ----------------------------------------------------------
    "note_prompt": "Write something for the next one.",
    "note_keys": "Enter: save     Esc: skip",
    "result_title": "Out of the {name}",
    "result_line1": "Time {time}    Deaths {deaths}{retried}    Notes {notes}/{total}",
    "result_retried": "    Floor restarts {n}",
    "result_line2": "Sonar {pings}    Stones {stones}    Walls broken {walls}    Watcher banished {banished}",
    "assisted": "This attempt was assisted (dev mode, or not started on Floor 1). No achievements.",
    "new_achievements": "New achievements",
    "no_new": "No new achievements this time.",
    "achievements_total": "Achievements: {got} of {total}",
    "note_saved": "Your note has been kept.",
    "continue_hint": "Enter: continue",
    "next_attempt": "Attempt {n}.",

    # --- achievements ----------------------------------------------------
    "achievements_title": "Achievements",
    "achievements_count": "{got} of {total}",
    "achievements": {
        "tamat_redup": ("Out of the Dim", "Finish on Dim."),
        "tamat_gelap": ("Out of the Dark", "Finish on Dark."),
        "tamat_pekat": ("Out of the Pitch Black", "Finish on Pitch Black."),
        "tak_tersentuh": ("Untouched", "Finish without dying once."),
        "tak_lari": ("Never Ran", "Finish without ever running."),
        "tanpa_cahaya": ("Without Light", "Finish with the flashlight on for less than a minute."),
        "tangan_kosong": ("Empty Hands", "Finish without stones and without breaking walls."),
        "tidak_menoleh": ("Don't Look Back", "Finish in under 12 minutes."),
        "pengalih": ("Decoy", "Lure away a Listener that's hunting you with a stone."),
        "lagi": ("Again.", "Finish twice."),
        "jalan_pintas": ("Shortcut", "Break 10 walls."),
        "menatap_balik": ("Staring Back", "Banish the Watcher 10 times."),
        "seribu_gema": ("A Thousand Echoes", "Use the sonar 1000 times."),
        "kembali_lagi": ("Back Again", "Start 10 attempts."),
    },

    # --- dev mode --------------------------------------------------------
    "dev_title": "Dev mode",
    "dev_options": {
        "god": ("Invincible (can't die)", "invincible"),
        "no_cooldown": ("Sonar without cooldown", "no sonar cooldown"),
        "infinite_light": ("Unlimited flashlight", "unlimited light"),
        "infinite_tools": ("Unlimited stones & walls", "unlimited tools"),
    },
    "dev_keys": [
        "F5: collect every fragment on this floor",
        "F6: jump to the exit",
        "F3: debug overlay",
    ],
}
