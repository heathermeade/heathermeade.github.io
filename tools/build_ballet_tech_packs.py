from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import TABLOID, landscape
from reportlab.lib.colors import HexColor, Color, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)

PAGE_W, PAGE_H = landscape(TABLOID)
BOARD_W, BOARD_H = 24*72, 18*72
INK = HexColor("#20221F")
MUTED = HexColor("#6A6B65")
PAPER = HexColor("#FAFAF7")
PANEL = HexColor("#F0F0EB")
RULE = HexColor("#D2D2CA")
RED = HexColor("#B64E45")
LINING = HexColor("#F1C5A9")


def font_setup():
    candidates = [
        ("Inter", "/System/Library/Fonts/Supplemental/Arial.ttf"),
        ("InterBold", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ]
    for name, path in candidates:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(name, path))


font_setup()
REG = "Inter" if "Inter" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
BOLD = "InterBold" if "InterBold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"


def label(c, text, x, y, size=8, color=INK, font=REG):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def right_label(c, text, x, y, size=8, color=INK, font=REG):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawRightString(x, y, text)


def fit_text(c, text, x, y, max_width, size=8, min_size=6, color=INK, font=REG):
    use_size = size
    while use_size > min_size and stringWidth(text, font, use_size) > max_width:
        use_size -= 0.25
    label(c, text, x, y, use_size, color, font)


def paragraph(c, text, x, y, width, size=7.5, leading=10, color=INK, font=REG, max_lines=4):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    for i, line in enumerate(lines[:max_lines]):
        label(c, line, x, y - i * leading, size, color, font)
    return y - min(len(lines), max_lines) * leading


def rounded_panel(c, x, y, w, h, fill=PANEL, radius=6):
    c.setFillColor(fill)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def header(c, spec):
    c.setFillColor(INK)
    c.rect(0, PAGE_H - 74, PAGE_W, 74, fill=1, stroke=0)
    label(c, "MOTION FLAT", 28, PAGE_H - 30, 20, white, BOLD)
    label(c, "CONVERTIBLE STRAP BALLET FLAT", 28, PAGE_H - 48, 8, HexColor("#D5D8D1"), BOLD)
    c.setStrokeColor(HexColor("#60625E"))
    c.line(256, PAGE_H - 60, 256, PAGE_H - 14)
    label(c, "STYLE ID", 274, PAGE_H - 27, 7, HexColor("#B9BBB5"), BOLD)
    label(c, "MF-CB-001", 274, PAGE_H - 47, 12, white, BOLD)
    c.line(414, PAGE_H - 60, 414, PAGE_H - 14)
    label(c, "COLORWAY", 432, PAGE_H - 27, 7, HexColor("#B9BBB5"), BOLD)
    fit_text(c, spec["name"].upper(), 432, PAGE_H - 47, 260, 12, 8, white, BOLD)
    right_label(c, "REV C / 21 SEP 2026", PAGE_W - 28, PAGE_H - 27, 7, HexColor("#B9BBB5"), BOLD)
    right_label(c, "WOMEN'S FOOTWEAR", PAGE_W - 28, PAGE_H - 47, 9, white, BOLD)


def draw_shoe(c, x, y, scale, spec, strap_on=True):
    body = HexColor(spec["body"])
    toe = HexColor(spec["toe"])
    sole = HexColor(spec["sole"])
    stitch = Color(1, 1, 1, alpha=0.48) if sum(body.rgb()) < 1.55 else HexColor("#9A8782")
    # Sole unit
    p = c.beginPath()
    p.moveTo(x + 18*scale, y + 25*scale)
    p.curveTo(x + 90*scale, y + 9*scale, x + 275*scale, y + 10*scale, x + 355*scale, y + 25*scale)
    p.curveTo(x + 352*scale, y + 39*scale, x + 324*scale, y + 42*scale, x + 292*scale, y + 43*scale)
    p.lineTo(x + 53*scale, y + 43*scale)
    p.curveTo(x + 36*scale, y + 42*scale, x + 23*scale, y + 36*scale, x + 18*scale, y + 25*scale)
    c.setFillColor(sole); c.setStrokeColor(INK); c.setLineWidth(1.4)
    c.drawPath(p, fill=1, stroke=1)
    # outsole traction line
    c.setStrokeColor(Color(0,0,0,alpha=.4)); c.setLineWidth(.7)
    for i in range(22, 348, 13):
        c.line(x+i*scale, y+24*scale, x+(i+5)*scale, y+18*scale)
    # Upper body
    p = c.beginPath()
    p.moveTo(x + 34*scale, y + 45*scale)
    p.curveTo(x + 36*scale, y + 82*scale, x + 54*scale, y + 108*scale, x + 92*scale, y + 115*scale)
    p.curveTo(x + 155*scale, y + 127*scale, x + 207*scale, y + 115*scale, x + 250*scale, y + 112*scale)
    p.curveTo(x + 290*scale, y + 109*scale, x + 329*scale, y + 89*scale, x + 349*scale, y + 63*scale)
    p.curveTo(x + 357*scale, y + 52*scale, x + 350*scale, y + 45*scale, x + 331*scale, y + 43*scale)
    p.lineTo(x + 57*scale, y + 43*scale)
    p.curveTo(x + 44*scale, y + 43*scale, x + 37*scale, y + 43*scale, x + 34*scale, y + 45*scale)
    c.setFillColor(body); c.setStrokeColor(INK); c.setLineWidth(1.6)
    c.drawPath(p, fill=1, stroke=1)
    # Opening with visible lining
    p = c.beginPath()
    p.moveTo(x + 57*scale, y + 104*scale)
    p.curveTo(x + 96*scale, y + 119*scale, x + 151*scale, y + 108*scale, x + 199*scale, y + 105*scale)
    p.curveTo(x + 220*scale, y + 104*scale, x + 224*scale, y + 95*scale, x + 205*scale, y + 91*scale)
    p.curveTo(x + 159*scale, y + 82*scale, x + 111*scale, y + 91*scale, x + 69*scale, y + 90*scale)
    p.curveTo(x + 58*scale, y + 91*scale, x + 52*scale, y + 97*scale, x + 57*scale, y + 104*scale)
    c.setFillColor(LINING); c.setStrokeColor(INK); c.setLineWidth(1)
    c.drawPath(p, fill=1, stroke=1)
    # Topline binding
    c.setStrokeColor(stitch); c.setLineWidth(2.3)
    p = c.beginPath(); p.moveTo(x+40*scale,y+96*scale)
    p.curveTo(x+82*scale,y+122*scale,x+152*scale,y+109*scale,x+206*scale,y+106*scale)
    c.drawPath(p, fill=0, stroke=1)
    # Toe cap panel (same material construction even when tonal)
    p = c.beginPath(); p.moveTo(x + 270*scale, y + 43*scale)
    p.curveTo(x + 273*scale, y + 69*scale, x + 273*scale, y + 92*scale, x + 265*scale, y + 106*scale)
    p.curveTo(x + 306*scale, y + 101*scale, x + 337*scale, y + 81*scale, x + 349*scale, y + 62*scale)
    p.curveTo(x + 356*scale, y + 52*scale, x + 349*scale, y + 45*scale, x + 330*scale, y + 43*scale)
    p.close()
    c.setFillColor(toe); c.setStrokeColor(INK); c.setLineWidth(1)
    c.drawPath(p, fill=1, stroke=1)
    c.setDash(3*scale, 2*scale); c.setStrokeColor(stitch); c.setLineWidth(.8)
    c.line(x+275*scale,y+49*scale,x+270*scale,y+98*scale); c.setDash()
    # Bow
    c.setStrokeColor(INK); c.setFillColor(body); c.setLineWidth(1)
    c.ellipse(x+243*scale,y+96*scale,x+260*scale,y+108*scale,fill=1,stroke=1)
    c.ellipse(x+258*scale,y+96*scale,x+275*scale,y+108*scale,fill=1,stroke=1)
    c.circle(x+259*scale,y+102*scale,3.2*scale,fill=1,stroke=1)
    # Removable straps
    if strap_on:
        for sx in (142, 194):
            p = c.beginPath()
            p.moveTo(x+(sx-8)*scale,y+47*scale)
            p.lineTo(x+(sx+2)*scale,y+111*scale)
            p.lineTo(x+(sx+15)*scale,y+109*scale)
            p.lineTo(x+(sx+6)*scale,y+47*scale)
            p.close()
            c.setFillColor(body); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.drawPath(p,fill=1,stroke=1)
            # low-profile clip indication
            c.setFillColor(INK)
            c.circle(x+(sx-1)*scale,y+49*scale,2.2*scale,fill=1,stroke=0)
    return {
        "upper": (x+100*scale, y+70*scale),
        "toe": (x+306*scale, y+76*scale),
        "sole": (x+215*scale, y+25*scale),
        "lining": (x+150*scale, y+99*scale),
        "strap": (x+190*scale, y+82*scale),
        "bow": (x+259*scale, y+103*scale),
    }


def prepare_product_image(source):
    """Trim the studio whitespace while retaining a soft margin and shadow."""
    source = ROOT / source
    target = source.with_name(source.stem + "-cropped.png")
    with Image.open(source).convert("RGB") as im:
        background = Image.new("RGB", im.size, (255, 255, 255))
        difference = ImageChops.difference(im, background).convert("L")
        # Ignore imperceptible compression/lighting variation in the white field.
        mask = difference.point(lambda px: 255 if px > 8 else 0)
        bbox = mask.getbbox()
        if bbox:
            left, top, right, bottom = bbox
            pad_x, pad_y = 35, 28
            bbox = (
                max(0, left-pad_x), max(0, top-pad_y),
                min(im.width, right+pad_x), min(im.height, bottom+pad_y),
            )
            im = im.crop(bbox)
        im.save(target, "PNG", optimize=True)
    return target


def draw_product_image(c, spec):
    image_path = prepare_product_image(spec["render"])
    with Image.open(image_path) as im:
        iw, ih = im.size
    max_w, max_h = 515, 182
    ratio = min(max_w/iw, max_h/ih)
    draw_w, draw_h = iw*ratio, ih*ratio
    x = 330 + (515-draw_w)/2
    y = 332 + (182-draw_h)/2
    c.drawImage(ImageReader(str(image_path)), x, y, draw_w, draw_h,
                preserveAspectRatio=True, anchor="c", mask="auto")
    # Anchors follow the stable lateral composition of the approved product renders.
    return {
        "upper": (x + draw_w*.30, y + draw_h*.48),
        "toe": (x + draw_w*.84, y + draw_h*.48),
        "sole": (x + draw_w*.60, y + draw_h*.12),
        "lining": (x + draw_w*.38, y + draw_h*.72),
        "strap": (x + draw_w*.54, y + draw_h*.65),
        "bow": (x + draw_w*.76, y + draw_h*.70),
    }


def draw_mode_image(c, source, x, y, max_w=155, max_h=58):
    image_path = prepare_product_image(source)
    with Image.open(image_path) as im:
        iw, ih = im.size
    ratio = min(max_w/iw, max_h/ih)
    draw_w, draw_h = iw*ratio, ih*ratio
    c.drawImage(ImageReader(str(image_path)), x+(max_w-draw_w)/2, y+(max_h-draw_h)/2,
                draw_w, draw_h, preserveAspectRatio=True, anchor="c", mask="auto")


def prepare_view_crops(source):
    source = ROOT / source
    with Image.open(source).convert("RGB") as im:
        w, h = im.size
        boxes = {
            "front": (0, 0, int(w*.245), int(h*.56)),
            "back": (int(w*.245), 0, int(w*.455), int(h*.56)),
            "medial": (int(w*.465), 0, w, int(h*.56)),
            "top": (0, int(h*.50), int(w*.49), h),
            "outsole": (int(w*.50), int(h*.50), w, h),
        }
        results = {}
        for name, box in boxes.items():
            crop = im.crop(box)
            bg = Image.new("RGB", crop.size, (255, 255, 255))
            mask = ImageChops.difference(crop, bg).convert("L").point(lambda px: 255 if px > 8 else 0)
            bbox = mask.getbbox()
            if bbox:
                left, top, right, bottom = bbox
                pad = 18
                crop = crop.crop((max(0,left-pad), max(0,top-pad), min(crop.width,right+pad), min(crop.height,bottom+pad)))
            target = source.with_name(f"{source.stem}-{name}.png")
            crop.save(target, "PNG", optimize=True)
            results[name] = target
    return results


def draw_view_card(c, x, y, w, h, title, image_path, subtitle):
    rounded_panel(c, x, y, w, h, white)
    c.setFillColor(INK); c.roundRect(x, y+h-28, w, 28, 6, fill=1, stroke=0)
    c.rect(x, y+h-28, w, 8, fill=1, stroke=0)
    label(c, title.upper(), x+14, y+h-18, 8, white, BOLD)
    right_label(c, subtitle.upper(), x+w-14, y+h-18, 6, HexColor("#C8CAC4"), BOLD)
    with Image.open(image_path) as im:
        iw, ih = im.size
    max_w, max_h = w-24, h-48
    ratio = min(max_w/iw, max_h/ih)
    dw, dh = iw*ratio, ih*ratio
    c.drawImage(ImageReader(str(image_path)), x+(w-dw)/2, y+10+(max_h-dh)/2,
                dw, dh, preserveAspectRatio=True, anchor="c", mask="auto")


def draw_attachment_detail(c, spec, x, y, w, h):
    rounded_panel(c, x, y, w, h, PANEL)
    label(c, "REMOVABLE STRAP ATTACHMENT / DEVELOPMENT DETAIL", x+16, y+h-22, 8.5, INK, BOLD)
    label(c, "Four low-profile attachment points total - two ends per strap", x+16, y+h-35, 6.5, MUTED, REG)
    body = HexColor(spec["body"])
    # Strap end
    c.setFillColor(body); c.setStrokeColor(INK); c.setLineWidth(1)
    c.roundRect(x+36, y+24, 155, 26, 10, fill=1, stroke=1)
    c.setFillColor(HexColor("#B9B8B1")); c.circle(x+180, y+37, 6, fill=1, stroke=1)
    label(c, "STRAP END", x+36, y+12, 6.3, MUTED, BOLD)
    # Direction arrow
    c.setStrokeColor(RED); c.setLineWidth(1.4)
    c.line(x+205, y+37, x+264, y+37)
    c.line(x+257, y+42, x+264, y+37); c.line(x+257, y+32, x+264, y+37)
    label(c, "PRESS TO ATTACH", x+207, y+51, 6.2, RED, BOLD)
    # Shoe-side tab and socket
    c.setFillColor(body); c.setStrokeColor(INK)
    c.roundRect(x+278, y+20, 182, 34, 8, fill=1, stroke=1)
    c.setFillColor(PAPER); c.circle(x+300, y+37, 7, fill=1, stroke=1)
    c.setFillColor(HexColor("#AFAEA7")); c.circle(x+300, y+37, 3.5, fill=1, stroke=1)
    label(c, "CONCEALED SHOE-SIDE TAB", x+278, y+9, 6.3, MUTED, BOLD)
    # Callout box
    c.setFillColor(white); c.setStrokeColor(RULE)
    c.roundRect(x+490, y+16, w-510, 54, 5, fill=1, stroke=1)
    label(c, "LOW-PROFILE SNAP / CLIP", x+506, y+54, 7.2, INK, BOLD)
    paragraph(c, "Hardware may be a snap-button or spring clip after prototype testing. It must sit flush, resist accidental release, and remain discreet when straps are removed.", x+506, y+40, w-536, 6.2, 8, MUTED, REG, 4)


def draw_multiview_page(c, spec):
    c.setFillColor(PAPER); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    header(c, spec)
    label(c, "02 / ORTHOGRAPHIC PRODUCT VIEWS + ATTACHMENT DETAIL", 28, PAGE_H-96, 9, MUTED, BOLD)
    crops = prepare_view_crops(spec["multiview_render"])
    draw_view_card(c, 28, 421, 250, 245, "Front view", crops["front"], "Toe facing camera")
    draw_view_card(c, 292, 421, 250, 245, "Back view", crops["back"], "Heel facing camera")
    draw_view_card(c, 556, 421, 320, 245, "Medial view", crops["medial"], "Inside profile")
    draw_view_card(c, 28, 184, 410, 220, "Top view", crops["top"], "Straps installed")
    draw_view_card(c, 452, 184, 424, 220, "Outsole", crops["outsole"], "Traction layout")
    draw_attachment_detail(c, spec, 28, 38, 848, 126)
    c.setStrokeColor(RULE); c.line(28, 22, PAGE_W-28, 22)
    label(c, "MOTION FLAT / DESIGN DEVELOPMENT / CONFIDENTIAL", 28, 10, 6, MUTED, BOLD)
    right_label(c, "02 / 02", PAGE_W-28, 10, 6.5, INK, BOLD)


def callout(c, num, title, detail, anchor, tx, ty, align="left"):
    ax, ay = anchor
    c.setStrokeColor(RED); c.setLineWidth(.8)
    endx = tx + (2 if align == "left" else -2)
    c.line(ax, ay, endx, ty+2)
    c.setFillColor(RED); c.circle(ax, ay, 2.2, fill=1, stroke=0)
    c.setFillColor(INK); c.circle(tx, ty, 10, fill=1, stroke=0)
    c.setFillColor(white); c.setFont(BOLD, 7); c.drawCentredString(tx, ty-2.5, str(num))
    if align == "left":
        label(c, title.upper(), tx+15, ty+3, 8, INK, BOLD)
        paragraph(c, detail, tx+15, ty-9, 130, 6.5, 8, MUTED, REG, 2)
    else:
        right_label(c, title.upper(), tx-15, ty+3, 8, INK, BOLD)
        # right aligned single detail line to keep the callout compact
        right_label(c, detail, tx-15, ty-9, 6.5, MUTED, REG)


def swatch(c, x, y, color, title, hexcode, detail, width=185):
    c.setFillColor(HexColor(color)); c.setStrokeColor(INK); c.setLineWidth(.7)
    c.rect(x, y-4, 16, 16, fill=1, stroke=1)
    label(c, title.upper(), x+24, y+5, 7.5, INK, BOLD)
    right_label(c, hexcode.upper(), x+width, y+5, 7.2, INK, BOLD)
    fit_text(c, detail, x+24, y-6, width-24, 6.3, 5.5, MUTED, REG)


def table(c, x, y, col_widths, row_h, rows, header=True):
    total_w = sum(col_widths)
    for r, row in enumerate(rows):
        yy = y - r*row_h
        c.setFillColor(INK if header and r == 0 else (white if r % 2 else HexColor("#F5F5F1")))
        c.rect(x, yy-row_h, total_w, row_h, fill=1, stroke=0)
        xx = x
        for idx, cell in enumerate(row):
            c.setStrokeColor(RULE); c.setLineWidth(.5)
            c.rect(xx, yy-row_h, col_widths[idx], row_h, fill=0, stroke=1)
            color = white if header and r == 0 else INK
            font = BOLD if header and r == 0 else REG
            fit_text(c, str(cell), xx+5, yy-row_h+5.5, col_widths[idx]-10, 6.4, 5.2, color, font)
            xx += col_widths[idx]


def make_pack(spec):
    path = OUT / spec["filename"]
    c = canvas.Canvas(str(path), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle(f"Motion Flat Tech Pack - {spec['name']}")
    c.setAuthor("Design Development")
    c.setSubject("Convertible strap ballet flat colorway specification")
    c.setFillColor(PAPER); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    header(c, spec)
    # Section bar
    label(c, "01 / LATERAL COLOR + MATERIAL SPECIFICATION", 28, PAGE_H-96, 9, MUTED, BOLD)

    # Left material palette
    rounded_panel(c, 28, 336, 215, 190, white)
    label(c, "COLOR + MATERIAL KEY", 44, 505, 9, INK, BOLD)
    swatch(c, 44, 477, spec["body"], "Main upper + straps", spec["body"], "Soft leather; body and removable straps match", 178)
    swatch(c, 44, 442, spec["toe"], "Toe cap", spec["toe"], "Firm leather reinforcement; tonal on CW02/CW03", 178)
    swatch(c, 44, 407, spec["sole"], "Sole unit", spec["sole"], "Flexible rubber with low-profile traction", 178)
    swatch(c, 44, 372, "#F1C5A9", "Interior", "#F1C5A9", "Neutral skin-tone lining and sockliner", 178)
    label(c, "Finish intent", 44, 346, 6.5, MUTED, BOLD)
    paragraph(c, spec["finish"], 96, 346, 130, 6.2, 8, MUTED, REG, 2)

    # Main flat and callouts
    rounded_panel(c, 258, 246, 618, 280, white)
    refs = draw_product_image(c, spec)
    callout(c, 1, "Leather upper", "Soft structure for all-day wear", refs["upper"], 290, 490, "left")
    callout(c, 2, "Removable straps", "Matching leather; low-profile clips", refs["strap"], 290, 288, "left")
    callout(c, 3, "Protective toe", "Firm leather cap with edge stitch", refs["toe"], 842, 480, "right")
    callout(c, 4, "Rubber sole", "Flexible traction compound", refs["sole"], 842, 286, "right")
    callout(c, 5, "Neutral lining", "Soft skin-tone interior", refs["lining"], 708, 504, "left")
    callout(c, 6, "Decorative bow", "Fixed tonal leather bow", refs["bow"], 800, 435, "left")
    label(c, "VIEW: LATERAL / STRAPS INSTALLED", 278, 258, 7, MUTED, BOLD)
    right_label(c, "DRAWING NOT TO SCALE", 856, 258, 6.5, MUTED, BOLD)

    # Bottom left: functional modes
    rounded_panel(c, 28, 116, 360, 126, white)
    label(c, "CONVERTIBLE WEAR MODES / CLIP-ON STRAPS", 44, 224, 8.5, INK, BOLD)
    draw_mode_image(c, spec["render"], 38, 154)
    draw_mode_image(c, spec["strapless_render"], 216, 154)
    label(c, "COMMUTE MODE", 48, 143, 6.8, INK, BOLD)
    label(c, "Four snap/clip points engaged", 48, 131, 6.2, MUTED, REG)
    label(c, "PROFESSIONAL MODE", 226, 143, 6.8, INK, BOLD)
    label(c, "Straps released; tabs stay discreet", 226, 131, 6.2, MUTED, REG)

    # Bottom center: component/BOM
    rounded_panel(c, 402, 116, 474, 126, white)
    label(c, "BILL OF MATERIALS / DEVELOPMENT BASIS", 418, 224, 8.5, INK, BOLD)
    rows = [
        ["REF", "COMPONENT", "MATERIAL / FINISH", "COLOR"],
        ["01", "Upper body", "Soft leather, smooth matte", spec["body"].upper()],
        ["02", "Toe reinforcement", "Firm leather, edge stitched", spec["toe"].upper()],
        ["03", "Removable straps", "Matching upper leather + hidden clip", spec["body"].upper()],
        ["04", "Lining + sockliner", "Soft lining over cushioned insole", "#F1C5A9"],
        ["05", "Sole", "Flexible traction rubber", spec["sole"].upper()],
    ]
    table(c, 418, 209, [30, 105, 205, 92], 14, rows)

    # Footer requirements + notes
    rounded_panel(c, 28, 34, 848, 74, PANEL)
    label(c, "DESIGN INTENT", 44, 89, 7, INK, BOLD)
    paragraph(c, "A polished ballet flat that transitions from commuting to work and social plans without requiring a second pair.", 44, 76, 245, 6.4, 8, MUTED, REG, 3)
    label(c, "CONSTRUCTION NOTES", 318, 89, 7, INK, BOLD)
    paragraph(c, "Two removable instep straps. Conceal or minimize attachment hardware. Add cushioned insole, flexible forefoot, and slip-resistant tread.", 318, 76, 280, 6.4, 8, MUTED, REG, 3)
    label(c, "DEVELOPMENT STATUS", 630, 89, 7, INK, BOLD)
    paragraph(c, "Concept tech pack. Last, grading, supplier, leather grade, thickness, clip mechanism, and performance testing remain to be confirmed.", 630, 76, 225, 6.4, 8, MUTED, REG, 3)

    c.setStrokeColor(RULE); c.line(28, 22, PAGE_W-28, 22)
    label(c, "MOTION FLAT / DESIGN DEVELOPMENT / CONFIDENTIAL", 28, 10, 6, MUTED, BOLD)
    right_label(c, "01 / 02", PAGE_W-28, 10, 6.5, INK, BOLD)
    c.showPage()
    draw_multiview_page(c, spec)
    c.showPage(); c.save()
    # Basic structural validation
    reader = PdfReader(str(path))
    assert len(reader.pages) == 2
    return path


def board_header(c, spec):
    c.setFillColor(INK); c.rect(0, BOARD_H-96, BOARD_W, 96, fill=1, stroke=0)
    label(c, "MOTION FLAT", 36, BOARD_H-38, 25, white, BOLD)
    label(c, "CONVERTIBLE STRAP BALLET FLAT", 36, BOARD_H-62, 9, HexColor("#D5D8D1"), BOLD)
    c.setStrokeColor(HexColor("#62645F")); c.setLineWidth(1)
    c.line(340, BOARD_H-80, 340, BOARD_H-16)
    label(c, "STYLE ID", 366, BOARD_H-34, 8, HexColor("#B9BBB5"), BOLD)
    label(c, "MF-CB-001", 366, BOARD_H-61, 16, white, BOLD)
    c.line(566, BOARD_H-80, 566, BOARD_H-16)
    label(c, "COLORWAY", 592, BOARD_H-34, 8, HexColor("#B9BBB5"), BOLD)
    label(c, spec["name"].upper(), 592, BOARD_H-61, 16, white, BOLD)
    right_label(c, "REV D / 21 SEP 2026", BOARD_W-36, BOARD_H-34, 8, HexColor("#B9BBB5"), BOLD)
    right_label(c, "ONE-PAGE MASTER TECH PACK", BOARD_W-36, BOARD_H-61, 11, white, BOLD)


def draw_fit(c, source, x, y, w, h):
    source = Path(source)
    with Image.open(source) as im:
        iw, ih = im.size
    ratio = min(w/iw, h/ih)
    dw, dh = iw*ratio, ih*ratio
    c.drawImage(ImageReader(str(source)), x+(w-dw)/2, y+(h-dh)/2, dw, dh,
                preserveAspectRatio=True, anchor="c", mask="auto")
    return x+(w-dw)/2, y+(h-dh)/2, dw, dh


def board_materials(c, spec, x, y, w, h):
    rounded_panel(c, x, y, w, h, white)
    label(c, "COLOR + MATERIAL KEY", x+20, y+h-28, 12, INK, BOLD)
    entries = [
        (spec["body"], "MAIN UPPER + STRAPS", "Soft leather; straps match body"),
        (spec["toe"], "PROTECTIVE TOE CAP", "Firm leather reinforcement"),
        (spec["sole"], "SOLE UNIT", "Flexible low-profile traction rubber"),
        ("#F1C5A9", "INTERIOR", "Soft lining over cushioned sockliner"),
    ]
    yy = y+h-76
    for color, title, detail in entries:
        c.setFillColor(HexColor(color)); c.setStrokeColor(INK); c.setLineWidth(.8)
        c.rect(x+20, yy-10, 28, 28, fill=1, stroke=1)
        label(c, title, x+62, yy+9, 9, INK, BOLD)
        right_label(c, color.upper(), x+w-18, yy+9, 8.5, INK, BOLD)
        label(c, detail, x+62, yy-7, 7.5, MUTED, REG)
        yy -= 66
    c.setStrokeColor(RULE); c.line(x+20, y+76, x+w-20, y+76)
    label(c, "FINISH INTENT", x+20, y+56, 7.5, MUTED, BOLD)
    paragraph(c, spec["finish"], x+104, y+56, w-124, 7.5, 10, MUTED, REG, 3)


def board_hero(c, spec, x, y, w, h):
    rounded_panel(c, x, y, w, h, white)
    label(c, "LATERAL VIEW / STRAPS INSTALLED", x+20, y+h-28, 11, INK, BOLD)
    right_label(c, "REALISTIC PRODUCT RENDERING / NOT TO SCALE", x+w-20, y+h-28, 7.5, MUTED, BOLD)
    image_path = prepare_product_image(spec["render"])
    ix, iy, iw, ih = draw_fit(c, image_path, x+35, y+80, w-70, h-145)
    # Concise numbered component callouts.
    points = [
        (1, "LEATHER UPPER", ix+iw*.25, iy+ih*.48, x+38, y+h-62),
        (2, "REMOVABLE STRAPS", ix+iw*.52, iy+ih*.62, x+38, y+42),
        (3, "PROTECTIVE TOE", ix+iw*.86, iy+ih*.48, x+w-188, y+h-62),
        (4, "TRACTION SOLE", ix+iw*.62, iy+ih*.10, x+w-188, y+42),
        (5, "NEUTRAL LINING", ix+iw*.38, iy+ih*.75, x+w*.52, y+h-62),
        (6, "TONAL BOW", ix+iw*.78, iy+ih*.72, x+w-188, y+h-104),
    ]
    for num, text_value, ax, ay, tx, ty in points:
        c.setStrokeColor(RED); c.setLineWidth(.8); c.line(ax, ay, tx, ty)
        c.setFillColor(RED); c.circle(ax, ay, 2.4, fill=1, stroke=0)
        c.setFillColor(INK); c.circle(tx, ty, 10, fill=1, stroke=0)
        c.setFillColor(white); c.setFont(BOLD, 7); c.drawCentredString(tx, ty-2.5, str(num))
        label(c, text_value, tx+15, ty-3, 7.3, INK, BOLD)


def board_view_card(c, x, y, w, h, title, image_path):
    rounded_panel(c, x, y, w, h, white)
    c.setFillColor(INK); c.roundRect(x, y+h-26, w, 26, 5, fill=1, stroke=0)
    c.rect(x, y+h-26, w, 6, fill=1, stroke=0)
    label(c, title.upper(), x+12, y+h-17, 8, white, BOLD)
    draw_fit(c, image_path, x+8, y+7, w-16, h-40)


def board_multiview(c, spec, x, y, w, h):
    crops = prepare_view_crops(spec["multiview_render"])
    gap = 10
    top_h = 216
    bottom_h = h-top_h-gap
    front_w = 150; back_w = 150; medial_w = w-front_w-back_w-gap*2
    board_view_card(c, x, y+bottom_h+gap, front_w, top_h, "Front", crops["front"])
    board_view_card(c, x+front_w+gap, y+bottom_h+gap, back_w, top_h, "Back", crops["back"])
    board_view_card(c, x+front_w+back_w+gap*2, y+bottom_h+gap, medial_w, top_h, "Medial", crops["medial"])
    board_view_card(c, x, y, (w-gap)/2, bottom_h, "Top", crops["top"])
    board_view_card(c, x+(w+gap)/2, y, (w-gap)/2, bottom_h, "Outsole", crops["outsole"])


def board_modes(c, spec, x, y, w, h):
    rounded_panel(c, x, y, w, h, white)
    label(c, "CONVERTIBLE WEAR MODES / CLIP-ON STRAPS", x+18, y+h-28, 11, INK, BOLD)
    draw_mode_image(c, spec["render"], x+18, y+122, 210, 92)
    draw_mode_image(c, spec["strapless_render"], x+252, y+122, 210, 92)
    label(c, "COMMUTE MODE", x+28, y+100, 9, INK, BOLD)
    label(c, "Four snap/clip points engaged", x+28, y+84, 7.5, MUTED, REG)
    label(c, "PROFESSIONAL MODE", x+262, y+100, 9, INK, BOLD)
    label(c, "Straps released; tabs stay discreet", x+262, y+84, 7.5, MUTED, REG)
    c.setStrokeColor(RED); c.setLineWidth(1)
    for px in (x+104, x+126):
        c.circle(px, y+157, 5, fill=0, stroke=1)
    c.line(x+126, y+157, x+190, y+63)
    label(c, "VISIBLE SIDE: TWO LOW-PROFILE SNAP / CLIP POINTS", x+28, y+49, 7.2, RED, BOLD)
    label(c, "Two corresponding points sit on the opposite side of the shoe.", x+28, y+34, 7, MUTED, REG)


def board_bom(c, spec, x, y, w, h):
    rounded_panel(c, x, y, w, h, white)
    label(c, "BILL OF MATERIALS / DEVELOPMENT BASIS", x+18, y+h-28, 11, INK, BOLD)
    rows = [
        ["REF", "COMPONENT", "MATERIAL / FINISH", "COLOR"],
        ["01", "Upper body", "Soft leather, smooth matte", spec["body"].upper()],
        ["02", "Toe reinforcement", "Firm leather, edge stitched", spec["toe"].upper()],
        ["03", "Removable straps", "Matching leather + concealed clip/snap", spec["body"].upper()],
        ["04", "Lining + sockliner", "Soft lining over cushioned insole", "#F1C5A9"],
        ["05", "Sole", "Flexible traction rubber", spec["sole"].upper()],
    ]
    colw = [44, 145, w-44-145-110-36, 110]
    row_h = 38
    top = y+h-54
    for ri, row in enumerate(rows):
        yy = top-ri*row_h
        c.setFillColor(INK if ri == 0 else (white if ri%2 else HexColor("#F4F4EF")))
        c.rect(x+18, yy-row_h, w-36, row_h, fill=1, stroke=0)
        xx=x+18
        for ci, cell in enumerate(row):
            c.setStrokeColor(RULE); c.rect(xx, yy-row_h, colw[ci], row_h, fill=0, stroke=1)
            fit_text(c, str(cell), xx+7, yy-row_h+13, colw[ci]-14, 8, 6.5,
                     white if ri==0 else INK, BOLD if ri==0 else REG)
            xx += colw[ci]


def board_attachment(c, spec, x, y, w, h):
    rounded_panel(c, x, y, w, h, PANEL)
    label(c, "REMOVABLE STRAP ATTACHMENT DETAIL", x+18, y+h-28, 11, INK, BOLD)
    label(c, "Four total attachment points - two ends per strap", x+18, y+h-47, 7.5, MUTED, REG)
    body=HexColor(spec["body"])
    c.setFillColor(body); c.setStrokeColor(INK); c.setLineWidth(1.2)
    c.roundRect(x+28, y+165, 190, 34, 12, fill=1, stroke=1)
    c.setFillColor(HexColor("#B9B8B1")); c.circle(x+203, y+182, 7, fill=1, stroke=1)
    label(c, "REMOVABLE STRAP END", x+28, y+147, 7.2, MUTED, BOLD)
    c.setStrokeColor(RED); c.setLineWidth(1.6); c.line(x+236, y+182, x+300, y+182)
    c.line(x+292, y+188, x+300, y+182); c.line(x+292, y+176, x+300, y+182)
    label(c, "PRESS TO ATTACH", x+237, y+198, 7, RED, BOLD)
    c.setFillColor(body); c.setStrokeColor(INK)
    c.roundRect(x+318, y+160, w-346, 44, 10, fill=1, stroke=1)
    c.setFillColor(PAPER); c.circle(x+338, y+182, 8, fill=1, stroke=1)
    c.setFillColor(HexColor("#AFAEA7")); c.circle(x+338, y+182, 4, fill=1, stroke=1)
    label(c, "CONCEALED SHOE-SIDE TAB", x+318, y+143, 7.2, MUTED, BOLD)
    c.setFillColor(white); c.setStrokeColor(RULE); c.roundRect(x+28, y+28, w-56, 92, 6, fill=1, stroke=1)
    label(c, "LOW-PROFILE SNAP / CLIP", x+44, y+96, 8.5, INK, BOLD)
    paragraph(c, "Hardware may be finalized as a snap-button or spring clip after prototype testing. It must sit flush, resist accidental release during commuting, and remain discreet when the straps are removed.", x+44, y+79, w-88, 7.4, 11, MUTED, REG, 5)


def board_notes(c, x, y, w, h):
    rounded_panel(c, x, y, w, h, PANEL)
    cols = [
        ("DESIGN INTENT", "A polished ballet flat that transitions from commuting to work and social plans without requiring a second pair."),
        ("CONSTRUCTION NOTES", "Two removable instep straps, concealed attachment hardware, cushioned insole, flexible forefoot, edge-stitched toe reinforcement, and slip-resistant tread."),
        ("DEVELOPMENT STATUS", "Concept tech pack. Last, grading, supplier, leather grade, thickness, finalized clip mechanism, tolerances, and performance testing remain to be confirmed."),
    ]
    col_w=(w-72)/3
    for i,(title,text_value) in enumerate(cols):
        xx=x+20+i*(col_w+16)
        label(c,title,xx,y+h-28,9,INK,BOLD)
        paragraph(c,text_value,xx,y+h-49,col_w,8,12,MUTED,REG,7)
    c.setStrokeColor(RULE); c.line(x+20, y+h-112, x+w-20, y+h-112)
    label(c, "USER NEED / PROBLEM STATEMENT", x+20, y+h-140, 9.5, INK, BOLD)
    paragraph(c, "Young urban professionals with unpredictable schedules need footwear that transitions comfortably between commuting, work, changing weather, errands, and spontaneous social plans without forcing a choice between style, support, protection, and versatility - or requiring an extra pair.", x+20, y+h-160, w-40, 9, 13, MUTED, REG, 3)
    c.setStrokeColor(RULE); c.line(x+20, y+92, x+w-20, y+92)
    label(c, "FUNCTIONAL REQUIREMENTS", x+20, y+66, 9.5, INK, BOLD)
    requirements = [
        "Secure retention while commuting",
        "Discreet hardware when straps are removed",
        "Cushioned all-day support",
        "Flexible forefoot movement",
        "Protective toe reinforcement",
        "Slip-resistant traction",
    ]
    req_w=(w-40)/3
    for i, req in enumerate(requirements):
        xx=x+20+(i%3)*req_w
        yy=y+43-(i//3)*23
        c.setFillColor(RED); c.circle(xx+4, yy+2, 3, fill=1, stroke=0)
        label(c, req, xx+14, yy-1, 8, INK, REG)


def make_board_pack(spec):
    path = OUT / spec["filename"]
    c = canvas.Canvas(str(path), pagesize=(BOARD_W, BOARD_H), pageCompression=1)
    c.setTitle(f"Motion Flat One-Page Tech Pack - {spec['name']}")
    c.setAuthor("Design Development")
    c.setFillColor(PAPER); c.rect(0,0,BOARD_W,BOARD_H,fill=1,stroke=0)
    board_header(c,spec)
    label(c,"ONE-PAGE PRODUCT SPECIFICATION / ALL VIEWS",36,BOARD_H-126,11,MUTED,BOLD)
    board_materials(c,spec,36,752,286,400)
    board_hero(c,spec,338,752,640,400)
    board_multiview(c,spec,994,752,698,400)
    board_modes(c,spec,36,392,480,330)
    board_bom(c,spec,532,392,580,330)
    board_attachment(c,spec,1128,392,564,330)
    board_notes(c,36,72,1656,290)
    c.setStrokeColor(RULE); c.line(36,48,BOARD_W-36,48)
    label(c,"MOTION FLAT / DESIGN DEVELOPMENT / CONFIDENTIAL / DRAWINGS NOT TO SCALE",36,27,7,MUTED,BOLD)
    right_label(c,"01 / 01",BOARD_W-36,27,8,INK,BOLD)
    c.showPage(); c.save()
    reader=PdfReader(str(path)); assert len(reader.pages)==1
    return path


SPECS = [
    {
        "filename": "motion-flat-tech-pack-01-noir.pdf",
        "name": "Noir Espresso Graphite",
        "render": "assets/tech-pack-renders/noir-realistic.png",
        "strapless_render": "assets/tech-pack-renders/noir-strapless.png",
        "multiview_render": "assets/tech-pack-renders/noir-multiview.png",
        "toe": "#262525", "body": "#251B1A", "sole": "#3A363B",
        "finish": "Subtle tonal contrast; matte upper with a lightly polished toe cap.",
    },
    {
        "filename": "motion-flat-tech-pack-02-blush.pdf",
        "name": "Blush Terracotta",
        "render": "assets/tech-pack-renders/blush-realistic.png",
        "strapless_render": "assets/tech-pack-renders/blush-strapless.png",
        "multiview_render": "assets/tech-pack-renders/blush-multiview.png",
        "toe": "#F8B1AB", "body": "#F8B1AB", "sole": "#BD7559",
        "finish": "Single-color blush upper; toe reinforcement remains tonal and discreet.",
    },
    {
        "filename": "motion-flat-tech-pack-03-petal.pdf",
        "name": "Petal Rose",
        "render": "assets/tech-pack-renders/petal-realistic.png",
        "strapless_render": "assets/tech-pack-renders/petal-strapless.png",
        "multiview_render": "assets/tech-pack-renders/petal-multiview.png",
        "toe": "#F8EDEB", "body": "#F8EDEB", "sole": "#F3D1CB",
        "finish": "Soft monochrome upper with a low-contrast rose sole and tonal hardware.",
    },
]


if __name__ == "__main__":
    for item in SPECS:
        print(make_board_pack(item))
