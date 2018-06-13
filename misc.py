
def split_spaces(text):
    """Remove leading and trailing spaces and report the number of such spaces.
    When text is composed entirely of spaces, it is regarded as a string whole
    of leading spaces.
    @param text(str) input string
    @returns lcnt(int) number of leading spaces
    @returns text(str) string with removed leading/trailing spaces
    @returns rcnt(int) number of trailing spaces"""
    t2 = text.lstrip(' ')
    lcnt = len(text) - len(t2)
    text = t2.rstrip(' ')
    rcnt = len(t2) - len(text)
    return lcnt, text, rcnt


def get_str_range(text, left, right):
    """Get substring text[left...right]."""
    res = ''
    for i in range(left, right + 1):
        res += text[i]
    return res


def get_indent(text):
    """Get the number of leading spaces in text."""
    res = 0
    for i in text:
        if i == ' ':
            res += 1
        else:
            break
    return res


def get_block_indent(text):
    """Get block minimum indentation."""
    lines = text.split('\n')
    cnt = []
    for i in lines:
        if i != '' and not i.isspace():
            cnt.append(get_indent(i))
    return min(cnt)
