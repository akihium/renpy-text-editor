# RenPy Text Editor — Generated file; do not edit manually

label adv_opening:
    # Smile
    aki "Hello, {b}world{/b}!" id d_sample_001
    mei "Wait{w=0.5}, let’s go together." id d_sample_002
    nvl clear
    nvl_narrator "What will you do?" id d_nvl_menu_001
    menu (nvl=True):
        "Say hello to her":
            nvl clear
            jump adv_greeting
        "Replay the opening":
            nvl clear
            jump adv_opening
    return

label adv_greeting:
    "The afternoon sunlight streams in." id d_sample_003
    nvl clear
    return
