# RenPy Text Editor — Generated file; do not edit manually

label adv_opening:
    # 切换背景
    scene adv_image_5f79e3ef605c06ba with fade
    # 微笑
    aki "先显示前半句。{w}{b}点击后再显示后半句。{/b}" id d_sample_001
    mei "等一下{w=0.5}，一起走吧。" id d_sample_002
    "你要怎么做？" id d_menu_001
    menu:
        "跟她打招呼":
            jump adv_greeting
        "再看一次开场":
            jump adv_opening
    return

label adv_greeting:
    "午后的阳光洒落。" id d_sample_003
    return
