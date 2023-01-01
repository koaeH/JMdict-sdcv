from k.core import Cantatio

class Pass(Cantatio):
    def do(self, entry, _):
        for _, sense in entry["senses"]:
            if "glossae" in sense:
                glossae = []
                for gloss in sense["glossae"]:
                    gloss["text"] = gloss["text"].strip()

                    glossae.append(gloss)

                sense["glossae"] = glossae

