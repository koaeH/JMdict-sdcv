SETTINGS = {
    "moderatrix" : {
        "passes" : [
            ("k.poco.s_ecca", {
                "by_ne_language" : "eng",
            }),
        ]
    },
    "precantrix" : {
        "passes" : [
            ("k.magi.g_refactor", {}),
            ("k.magi.p_abridged", {}),
            ("k.magi.e_priority", {}),
            ("k.magi.x_argonaut", {}),
        ]
    },
    "monstrifer" : {
        "khromikon" : [ 0xC4, 0xCA, 0xDC, 0x76, 0x2C, 0x1E, 0xC6 ],
        "aesthetic" : [ [ 72, 64, 56, 48, ], [ 56, 48, 40, ] ],
        "frequency" : [ 0x258E, 0x258C, 0x258A, 0x2588, ],
        "clavicula" : tuple("* † ‡ Я И ∆ Ξ Г".split()),
        "ornamenta" : 0b11,
    },
}

COMMANDS = {
    "artifex" : "k.ipse.artifex",
    "package" : "k.ipse.package",
}
