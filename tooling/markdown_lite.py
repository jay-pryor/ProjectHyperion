"""A small markdown-to-HTML converter shared by every renderer in tooling/.

The console's handbook renders framework documents, and any other renderer that turns a
Hyperion document into HTML must produce the same HTML for the same text (P3), so the
conversion lives here once. Deliberately small: the subset the framework documents use,
nothing more. Headings, paragraphs, lists (nested by indentation), tables, fenced and
indented code, block quotes, inline code, links, bold and italic. A ```mermaid fence
becomes a `<pre class="mermaid">` block for the page to draw. Derived from the console
design (M8); no document is the rule here, this is a renderer.

Library API:
    html = render(text, heading_prefix="", resolve_link=None)
`heading_prefix` is prepended to every heading id so several documents can share one
page. `resolve_link(href) -> href` lets the caller turn relative document paths into
in-page anchors. Only the standard library is used.
"""

import html
import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^```\s*(\S*)")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])")


def slug(heading):
    return re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")


# ------------------------------------------------------------------ inline

def inline(text, resolve_link=None):
    """Escape, then code spans (protected), links, bold, italic."""
    spans = []

    def keep(m):
        spans.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(spans) - 1}\x00"

    out = CODE_SPAN_RE.sub(keep, text)
    out = html.escape(out, quote=False)

    def link(m):
        href = m.group(2)
        if resolve_link:
            href = resolve_link(href)
        return f'<a href="{html.escape(href, quote=True)}">{m.group(1)}</a>'

    out = LINK_RE.sub(link, out)
    out = BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = ITALIC_RE.sub(r"<em>\1</em>", out)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], out)


# ------------------------------------------------------------------ blocks

def _table(lines, resolve_link):
    rows = []
    for line in lines:
        cells = line.strip().strip("|").split("|")
        rows.append([inline(c.strip(), resolve_link) for c in cells])
    head, body = rows[0], rows[1:]
    out = ['<div class="tw"><table>', "<thead><tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead>"]
    if body:
        out.append("<tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body) + "</tbody>")
    out.append("</table></div>")
    return "\n".join(out)


def _list(items, resolve_link):
    """items: [(indent, marker, text)] -> nested <ul>/<ol> by indentation."""
    out = []
    stack = []                                   # [(indent, tag)]

    def close_to(indent):
        while stack and stack[-1][0] > indent:
            out.append(f"</li></{stack.pop()[1]}>")

    for indent, marker, text in items:
        tag = "ol" if marker[0].isdigit() else "ul"
        if not stack or indent > stack[-1][0]:
            stack.append((indent, tag))
            out.append(f"<{tag}><li>{inline(text, resolve_link)}")
            continue
        close_to(indent)
        if stack and stack[-1][1] != tag:        # a new list type at the same level
            out.append(f"</li></{stack.pop()[1]}>")
            stack.append((indent, tag))
            out.append(f"<{tag}><li>{inline(text, resolve_link)}")
        else:
            out.append(f"</li><li>{inline(text, resolve_link)}")
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "\n".join(out)


def _code(lines, info):
    body = html.escape("\n".join(lines), quote=False)
    if info.startswith("mermaid"):
        return f'<pre class="mermaid">{body}</pre>'
    lang = f' class="language-{html.escape(info, quote=True)}"' if info else ""
    return f"<pre><code{lang}>{body}</code></pre>"


def render(text, heading_prefix="", resolve_link=None):
    lines = COMMENT_RE.sub("", text).splitlines()
    out, i, n = [], 0, len(lines)
    para = []

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(s.strip() for s in para), resolve_link)}</p>")
            para.clear()

    while i < n:
        line = lines[i]
        fence = FENCE_RE.match(line)
        if fence:
            flush()
            info, i, block = fence.group(1), i + 1, []
            while i < n and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            out.append(_code(block, info))
            i += 1
            continue
        h = HEADING_RE.match(line)
        if h:
            flush()
            level, title = len(h.group(1)), h.group(2)
            out.append(f'<h{level} id="{heading_prefix}{slug(title)}">{inline(title, resolve_link)}</h{level}>')
            i += 1
            continue
        if line.startswith("|") and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
            flush()
            block = [line]
            i += 2
            while i < n and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(_table(block, resolve_link))
            continue
        if LIST_RE.match(line):
            flush()
            items = []
            while i < n and lines[i].strip():
                m = LIST_RE.match(lines[i])
                if m:
                    items.append((len(m.group(1)), m.group(2), m.group(3)))
                elif items and lines[i].startswith(" "):      # continuation of the previous item
                    items[-1] = (items[-1][0], items[-1][1], items[-1][2] + " " + lines[i].strip())
                else:
                    break
                i += 1
            out.append(_list(items, resolve_link))
            continue
        if line.startswith(">"):
            flush()
            block = []
            while i < n and lines[i].startswith(">"):
                block.append(lines[i].lstrip(">").strip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(block), resolve_link)}</p></blockquote>")
            continue
        if line.startswith("    ") and not para:
            flush()
            block = []
            while i < n and (lines[i].startswith("    ") or not lines[i].strip()):
                block.append(lines[i][4:])
                i += 1
            while block and not block[-1].strip():
                block.pop()
            out.append(_code(block, ""))
            continue
        if not line.strip():
            flush()
        else:
            para.append(line)
        i += 1
    flush()
    return "\n".join(out)
