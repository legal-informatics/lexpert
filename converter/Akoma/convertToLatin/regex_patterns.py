import re

# PATTERN_STULE = "\\.[a-zA-Z\\-0-9# {\\n\\t:;]*}"
PATTERN_STYLE_TAG = "<style([\\t\\n]|.)*<\\/style>"
PATTERN_TAGS = "<[^>]*>"
PATTERN_HTML = "(" + PATTERN_TAGS + "|\t|&nbsp;)"
EXEPTION_TAG = ["p", "table", "tr", "td", "th"]


def clean_nl(text: str):
    while re.search("(\n\n\n|  )", text) is not None:
        text = text.replace("\n\n\n", "\n\n")
        text = text.replace("  ", " ")
    text = text.replace("</thead>", "")
    text = text.replace("<thead>", "")
    return text


def clean_style(text: str):
    find1 = text.find("<style")
    find2 = text.find("</style>")
    text = text[0: find1:] + text[find2 + 8::]
    return text


def strip_html_tags_exept(text: str, list_allowed_tags=EXEPTION_TAG):
    text = clean_style(text)
    s_allow = ""
    separator = ""
    for i in range(0, len(list_allowed_tags)):
        s_allow = s_allow + separator + list_allowed_tags[i] + "|\\/" + list_allowed_tags[i]
        separator = "|"
    allowing = "(?!"
    pattern_tags = allowing + s_allow + ")"
    pattern_html = "(<" + pattern_tags + PATTERN_TAGS[1:] + "|\t|&nbsp;)"
    returning = re.sub(pattern=pattern_html, repl="", string=text)
    return clean_nl(returning)


def strip_html_tags(text: str):
    text = clean_style(text)
    got = re.sub(pattern=PATTERN_HTML, repl="", string=text)
    return clean_nl(got)


if __name__ == "__main__":
    f = open("../data/dow_acts/51.html", mode="r", encoding="utf-8")
    lines = "".join(f.readlines())
    got = strip_html_tags(lines)
    # print(got)
    got = strip_html_tags_exept(lines, ['tr'])
    print(got)
