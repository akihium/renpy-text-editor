# RenPy Text Editor — Generated file; do not edit manually

label adv_opening:
    # Change background
    scene adv_image_5f79e3ef605c06ba with fade
    # Smile
    aki "Show the first half.{w}{b}Click to reveal the second half.{/b}" id d_sample_001
    mei "Wait{w=0.5}, let’s go together." id d_sample_002
    "What will you do?" id d_menu_001
    menu:
        "Say hello to her":
            jump adv_greeting
        "Replay the opening":
            jump adv_opening
    return

label adv_greeting:
    "The afternoon sunlight streams in." id d_sample_003
    return
