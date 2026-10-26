# RenPy Text Editor — Generated file; do not edit manually

label adv_opening:
    # 背景を切り替え
    scene adv_image_5f79e3ef605c06ba with fade
    # 笑顔
    aki "まず前半を表示します。{w}{b}クリックすると後半が表示されます。{/b}" id d_sample_001
    mei "ちょっと待って{w=0.5}、一緒に行こう。" id d_sample_002
    "どうしますか？" id d_menu_001
    menu:
        "彼女にあいさつする":
            jump adv_greeting
        "冒頭をもう一度見る":
            jump adv_opening
    return

label adv_greeting:
    "午後の日差しが差し込む。" id d_sample_003
    return
