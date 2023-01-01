from k.core import Cantatio

F = TABLE = {
    "ichi1" : 1.0, "ichi2" : 0.5,
    "spec1" : 1.0, "spec2" : 0.5,

    ** {
        "nf%02d" % n : (49 - n) / 48 for n in range(1, 49)
    },
}

class Pass(Cantatio):
    def of(self, pris):
        n = 0
        for m, s in enumerate(pris):
            try: n += TABLE[s]
            except KeyError:
                continue

        return n / (m or 1)

    def do(self, entry, _):
        for k_ele in entry["k_eles"]:
            if "ke_pris" in k_ele:
                k_ele["ko_frequency"] = self.of(k_ele["ke_pris"])

        for r_ele in entry["r_eles"]:
            if "re_pris" in r_ele:
                r_ele["ko_frequency"] = self.of(r_ele["re_pris"])
