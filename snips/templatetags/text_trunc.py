import re

re_words = re.compile(r'<.*?>|((?:\w[-\w]*|&.*?;)+)', re.S)
re_chars = re.compile(r'<.*?>|(.)', re.S)
re_tag = re.compile(r'<(/)?([^ ]+?)(?:(\s*/)| .*?)?>', re.S)
re_newlines = re.compile(r'\r\n|\r')  # Used in normalize_newlines
re_camel_case = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')
text_split = """\u200B"""
readmore_html = """<span class="moreelipses">...</span>"""


def truncate_html(text, length, words=True):
    """
    Truncate HTML to a certain number of chars (not counting tags and
    comments), or, if words is True, then to a certain number of words.
    Close opened tags if they were correctly closed in the given HTML.
    Preserve newlines in the HTML.
    """
    if words and length <= 0:
        return '', ''

    truncate_len = length

    html4_singlets = (
        'br', 'col', 'link', 'base', 'img',
        'param', 'area', 'hr', 'input'
    )

    # Count non-HTML chars/words and keep note of open tags
    pos = 0
    end_text_pos = 0
    current_len = 0
    open_tags = []

    regex = re_words if words else re_chars

    while current_len <= length:
        m = regex.search(text, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word or char
            current_len += 1
            if current_len == truncate_len:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or current_len >= truncate_len:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        # Element names are always case-insensitive
        tagname = tagname.lower()
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)

    if current_len <= length:
        return text, ''
    first = text[:end_text_pos]
    second = text[end_text_pos:]
    # Close any tags still open
    first += text_split
    first += readmore_html
    for tag in open_tags:
        first += '</%s>' % tag
    # Return string
    return first, second