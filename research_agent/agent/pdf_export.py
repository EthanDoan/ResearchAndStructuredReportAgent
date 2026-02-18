from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def _wrap_text(c, text: str, max_width: float, font_name: str, font_size: int):
    """
    Wrap text into lines that fit max_width using current canvas font metrics.
    """
    c.setFont(font_name, font_size)
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = (" ".join(cur + [w])).strip()
        if c.stringWidth(test, font_name, font_size) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def markdown_to_pdf(markdown: str, out_path: Path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out_path), pagesize=LETTER)
    width, height = LETTER

    left = 0.75 * inch
    right = 0.75 * inch
    top = 0.75 * inch
    bottom = 0.75 * inch
    max_width = width - left - right

    y = height - top

    def new_page():
        nonlocal y
        c.showPage()
        y = height - top

    def ensure_space(lines_count: int, line_height: float):
        nonlocal y
        if y - (lines_count * line_height) < bottom:
            new_page()

    # Basic styles
    body_font = ("Helvetica", 11)
    h1_font = ("Helvetica-Bold", 18)
    h2_font = ("Helvetica-Bold", 14)
    h3_font = ("Helvetica-Bold", 12)

    line_height = 14

    for raw in markdown.splitlines():
        line = raw.rstrip()

        # blank line
        if not line.strip():
            y -= line_height * 0.6
            if y < bottom:
                new_page()
            continue

        # headings
        if line.startswith("# "):
            text = line[2:].strip()
            ensure_space(2, line_height * 1.4)
            c.setFont(*h1_font)
            y -= line_height * 0.2
            c.drawString(left, y, text)
            y -= line_height * 1.6
            continue

        if line.startswith("## "):
            text = line[3:].strip()
            ensure_space(2, line_height * 1.2)
            c.setFont(*h2_font)
            c.drawString(left, y, text)
            y -= line_height * 1.3
            continue

        if line.startswith("### "):
            text = line[4:].strip()
            ensure_space(2, line_height * 1.1)
            c.setFont(*h3_font)
            c.drawString(left, y, text)
            y -= line_height * 1.2
            continue

        # bullets
        is_bullet = line.lstrip().startswith(("- ", "* "))
        if is_bullet:
            text = line.lstrip()[2:].strip()
            bullet_prefix = "• "
            wrapped = _wrap_text(c, text, max_width - 18, body_font[0], body_font[1])
            ensure_space(len(wrapped), line_height)

            # first line with bullet
            c.setFont(*body_font)
            c.drawString(left, y, bullet_prefix + wrapped[0])
            y -= line_height

            # continuation lines indented
            for cont in wrapped[1:]:
                if y < bottom:
                    new_page()
                c.drawString(left + 18, y, cont)
                y -= line_height
            continue

        # normal paragraph line
        wrapped = _wrap_text(c, line.strip(), max_width, body_font[0], body_font[1])
        ensure_space(len(wrapped), line_height)
        c.setFont(*body_font)
        for wline in wrapped:
            if y < bottom:
                new_page()
            c.drawString(left, y, wline)
            y -= line_height

    c.save()