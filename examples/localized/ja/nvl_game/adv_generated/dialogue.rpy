# RenPy Text Editor — Generated file; do not edit manually

label adv_opening:
    # 笑顔
    aki "こんにちは、{b}世界{/b}！" id d_sample_001
    mei "ちょっと待って{w=0.5}、一緒に行こう。" id d_sample_002
    nvl clear
    nvl_narrator "どうしますか？" id d_nvl_menu_001
    menu (nvl=True):
        "彼女にあいさつする":
            nvl clear
            jump adv_greeting
        "冒頭をもう一度見る":
            nvl clear
            jump adv_opening
    return

label adv_greeting:
    "午後の日差しが差し込む。" id d_sample_003
    nvl clear
    return
