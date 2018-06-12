
def split_spaces(text):
    """Remove leading and trailing spaces and report the number of such spaces.
    When text is composed entirely of spaces, it is regarded as a string whole
    of leading spaces.
    @param text(str) input string
    @returns lcnt(int) number of leading spaces
    @returns text(str) string with removed leading/trailing spaces
    @returns rcnt(int) number of trailing spaces"""
    lcnt = 0
    rcnt = 0
    while lcnt < len(text):
        if text[lcnt] != ' ':
            break
        lcnt += 1
    text = text[:lcnt]
    while rcnt < len(text):
        if text[len(text) - rcnt - 1] != ' ':
            break
        rcnt += 1
    text = text[-rcnt:]
    return lcnt, text, rcnt


def get_str_range(text, left, right):
    res = ''
    for i in range(left, right + 1):
        res += text[i]
    return res
