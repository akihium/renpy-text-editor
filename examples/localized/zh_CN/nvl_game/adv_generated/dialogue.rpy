# RenPy Text Editor — Generated file; do not edit manually

label adv_opening:
    # 微笑
    aki "你好，{b}世界{/b}！" id d_sample_001
    mei "等一下{w=0.5}，一起走吧。" id d_sample_002
    nvl clear
    nvl_narrator "你要怎么做？" id d_nvl_menu_001
    menu (nvl=True):
        "跟她打招呼":
            nvl clear
            jump adv_greeting
        "再看一次开场":
            nvl clear
            jump adv_opening
    return

label adv_greeting:
    "午后的阳光洒落。" id d_sample_003
    nvl clear
    return
