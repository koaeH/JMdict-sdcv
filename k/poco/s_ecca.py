from k.core import Cantatio

class Pass(Cantatio):
    def do(self, entry, data):
        ne_language = self.settings["by_ne_language"]

        senses = []
        for i, sense in entry["senses"]:
            if "glossae" in sense:
                glossae = []

                for gloss in sense["glossae"]:
                    if gloss["lang"] == ne_language:
                        if gloss["text"]:
                            glossae.append(gloss)
                    else:
                        break
                else:
                    if glossae:
                        sense["glossae"] = glossae

                        senses.append((i, sense))

        entry["senses"] = senses
