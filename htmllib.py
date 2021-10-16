
# taken from https://github.com/thecavemanlogic/open-contest/blob/master/opencontest/contest/pages/lib/htmllib.py
class HTML_Tag:
    def __init__(self, tag: str, contents: list, options: dict):
        self.tag = tag
        self.contents = list(contents)

        if "cls" in options:
            options["class"] = options["cls"]
            del options["cls"]
        
        if "contents" in options:
            if isinstance(options["contents"], list):
                self.contents.extend([item for item in options["contents"]])
            else:
                self.contents.append(options["contents"])
            del options["contents"]

        self.options = options
    
    def to_html(self):
        options = ""
        for option in self.options:
            options += f' {option}="{self.options[option]}"'
        contents = "".join(map(str, self.contents))
        return f"<{self.tag}{options}>{contents}</{self.tag}>"
    
    def __str__(self):
        return self.to_html()

class HTML:
    def __getattr__(self, tag):
        return lambda *a, **b: HTML_Tag(tag, a, b)

html = HTML()

head = html.head
body = html.body
div = html.div
a = html.a
h1 = html.h1
h2 = html.h2
p = html.p

def grid(*items):
    return div(
        *items,
        cls="grid",
        style=""
    )