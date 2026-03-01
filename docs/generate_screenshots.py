from PIL import Image, ImageDraw, ImageFont
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)

BG = (15, 23, 42)
SIDEBAR = (30, 41, 59)
CARD = (30, 41, 59)
BORDER = (51, 65, 85)
TEXT_PRIMARY = (226, 232, 240)
TEXT_SECONDARY = (148, 163, 184)
TEXT_MUTED = (71, 85, 105)
ACCENT = (59, 130, 246)
ACCENT_DARK = (37, 99, 235)
GREEN = (34, 197, 94)
RED = (239, 68, 68)
VIOLET = (139, 92, 246)
YELLOW = (234, 179, 8)

W, H = 1280, 780


def base_font(size=13):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    if fill:
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + 2 * radius, y1 + 2 * radius], fill=fill)
        draw.ellipse([x2 - 2 * radius, y1, x2, y1 + 2 * radius], fill=fill)
        draw.ellipse([x1, y2 - 2 * radius, x1 + 2 * radius, y2], fill=fill)
        draw.ellipse([x2 - 2 * radius, y2 - 2 * radius, x2, y2], fill=fill)
    if outline:
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)


def draw_sidebar(draw, active_item="dashboard"):
    draw.rectangle([0, 0, 220, H], fill=SIDEBAR)
    draw.line([220, 0, 220, H], fill=BORDER)
    draw.rectangle([0, 0, 220, 64], fill=SIDEBAR)
    draw.line([0, 64, 220, 64], fill=BORDER)
    draw_rounded_rect(draw, [16, 18, 44, 46], 6, fill=ACCENT)
    draw.text((20, 25), "FA", fill=TEXT_PRIMARY, font=base_font(14))
    draw.text((52, 20), "Face Attendance", fill=TEXT_PRIMARY, font=base_font(13))
    draw.text((52, 38), "System v2", fill=(96, 165, 250), font=base_font(11))

    items = [
        ("Dashboard", "dashboard", 84),
        ("Live Attendance", "live", 116),
        ("People", "persons", 148),
        ("Subjects", "subjects", 180),
        ("Reports", "reports", 212),
    ]
    for label, key, y in items:
        if key == active_item:
            draw_rounded_rect(draw, [8, y, 212, y + 30], 6, fill=(30, 64, 175))
            draw.text((36, y + 8), label, fill=(191, 219, 254), font=base_font(13))
        else:
            draw.text((36, y + 8), label, fill=TEXT_SECONDARY, font=base_font(13))

    draw.line([0, H - 60, 220, H - 60], fill=BORDER)
    draw_rounded_rect(draw, [10, H - 50, 210, H - 10], 8, fill=(15, 23, 42))
    draw.text((18, H - 40), "Model ready", fill=GREEN, font=base_font(12))
    draw.text((18, H - 24), "142 encodings", fill=TEXT_MUTED, font=base_font(11))


def draw_topbar(draw, title="Overview"):
    draw.rectangle([221, 0, W, 64], fill=SIDEBAR)
    draw.line([221, 64, W, 64], fill=BORDER)
    draw.text((240, 24), title, fill=TEXT_SECONDARY, font=base_font(13))
    draw_rounded_rect(draw, [W - 160, 20, W - 20, 44], 8, fill=ACCENT_DARK)
    draw.text((W - 148, 28), "Register Person", fill=(255, 255, 255), font=base_font(12))


def draw_stat_card(draw, x, y, w, h, label, value, sub, color=TEXT_PRIMARY):
    draw.rectangle([x, y, x + w, y + h], fill=CARD)
    draw.rectangle([x, y, x + w, y + h], outline=BORDER)
    draw.text((x + 18, y + 18), label.upper(), fill=TEXT_MUTED, font=base_font(10))
    draw.text((x + 18, y + 38), str(value), fill=color, font=base_font(28))
    draw.text((x + 18, y + 72), sub, fill=TEXT_MUTED, font=base_font(11))


def draw_card_outline(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=CARD)
    draw.rectangle([x, y, x + w, y + h], outline=BORDER)


def make_dashboard():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_sidebar(draw, "dashboard")
    draw_topbar(draw, "Overview")

    stat_cards = [
        ("Total People", "48", "registered", TEXT_PRIMARY),
        ("Subjects", "12", "active", TEXT_PRIMARY),
        ("Today", "31", "attendance marks", (96, 165, 250)),
        ("Model", "142", "face encodings", TEXT_PRIMARY),
    ]
    card_w = 240
    for i, (lbl, val, sub, col) in enumerate(stat_cards):
        x = 240 + i * (card_w + 10)
        draw_stat_card(draw, x, 84, card_w, 100, lbl, val, sub, col)

    # Weekly chart card
    cx, cy = 240, 204
    cw, ch = 630, 240
    draw_card_outline(draw, cx, cy, cw, ch)
    draw.text((cx + 18, cy + 16), "Weekly Attendance", fill=TEXT_PRIMARY, font=base_font(13))
    draw.text((cx + cw - 90, cy + 16), "Last 7 days", fill=TEXT_MUTED, font=base_font(11))

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    values = [18, 22, 31, 27, 35, 12, 8]
    bar_w = 60
    max_v = max(values)
    chart_h = 150
    chart_y_base = cy + ch - 40
    for i, (day, val) in enumerate(zip(days, values)):
        bx = cx + 30 + i * (bar_w + 10)
        bh = int((val / max_v) * chart_h)
        draw.rectangle([bx, chart_y_base - bh, bx + bar_w, chart_y_base], fill=ACCENT)
        draw.text((bx + 18, chart_y_base + 6), day, fill=TEXT_MUTED, font=base_font(10))

    # Quick actions card
    ax, ay = 890, 204
    aw, ah = 360, 240
    draw_card_outline(draw, ax, ay, aw, ah)
    draw.text((ax + 18, ay + 16), "Quick Actions", fill=TEXT_PRIMARY, font=base_font(13))
    actions = [
        ("Start Live Session", ACCENT_DARK),
        ("Register Person", (51, 65, 85)),
        ("Retrain Model", (51, 65, 85)),
        ("Download Reports", (51, 65, 85)),
    ]
    for j, (label, color) in enumerate(actions):
        by = ay + 46 + j * 42
        draw.rectangle([ax + 14, by, ax + aw - 14, by + 30], fill=color)
        draw.text((ax + 26, by + 8), label, fill=(255, 255, 255), font=base_font(12))

    # Recent sessions
    rx, ry = 240, 464
    rw = W - rx - 20
    draw_card_outline(draw, rx, ry, rw, 280)
    draw.text((rx + 18, ry + 16), "Recent Sessions", fill=TEXT_PRIMARY, font=base_font(13))
    draw.text((rx + rw - 70, ry + 16), "View all", fill=(96, 165, 250), font=base_font(11))

    headers = ["Subject", "Title", "Date", "Status"]
    hx = [rx + 18, rx + 220, rx + 420, rx + 680]
    for hdr, hxp in zip(headers, hx):
        draw.text((hxp, ry + 50), hdr.upper(), fill=TEXT_MUTED, font=base_font(10))
    draw.line([rx + 10, ry + 66, rx + rw - 10, ry + 66], fill=BORDER)

    sessions = [
        ("Machine Learning", "Week 8 Lab", "01 Mar 2026, 09:00", "active"),
        ("Data Structures", "Lecture 14", "28 Feb 2026, 11:00", "completed"),
        ("Algorithms", "Tutorial", "27 Feb 2026, 14:00", "completed"),
        ("Computer Networks", "Lab 5", "26 Feb 2026, 10:00", "completed"),
    ]
    for k, (subj, title, date, status) in enumerate(sessions):
        sy = ry + 78 + k * 40
        draw.text((hx[0], sy), subj, fill=TEXT_PRIMARY, font=base_font(12))
        draw.text((hx[1], sy), title, fill=TEXT_SECONDARY, font=base_font(12))
        draw.text((hx[2], sy), date, fill=TEXT_MUTED, font=base_font(11))
        s_col = GREEN if status == "active" else TEXT_MUTED
        s_bg = (20, 83, 45) if status == "active" else (30, 41, 59)
        draw.rectangle([hx[3], sy - 3, hx[3] + 80, sy + 17], fill=s_bg)
        draw.text((hx[3] + 8, sy), status, fill=s_col, font=base_font(11))

    img.save(os.path.join(OUT, "dashboard.png"), "PNG", optimize=True)
    print("dashboard.png saved")


def make_live():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_sidebar(draw, "live")
    draw_topbar(draw, "Live Attendance")

    # Camera feed
    draw_card_outline(draw, 240, 84, 700, 440)
    draw.text((258, 100), "Camera Feed", fill=TEXT_PRIMARY, font=base_font(13))
    # Simulated camera view
    cam_area = [240, 124, 940, 500]
    draw.rectangle(cam_area, fill=(10, 15, 28))

    # Simulated face boxes
    faces = [
        (320, 160, 500, 390, "Riya Sharma", "94%", GREEN),
        (580, 145, 760, 385, "Arjun Mehta", "91%", GREEN),
        (800, 200, 920, 380, "Unknown", "", RED),
    ]
    for fx1, fy1, fx2, fy2, name, conf, color in faces:
        draw.rectangle([fx1, fy1, fx2, fy2], outline=color, width=2)
        draw.rectangle([fx1, fy2 - 26, fx2, fy2], fill=color)
        label = f"{name} {conf}" if conf else name
        draw.text((fx1 + 6, fy2 - 20), label, fill=(255, 255, 255), font=base_font(12))

    draw.ellipse([W - 135, 84, W - 109, 110], fill=(20, 83, 45))
    draw.ellipse([W - 128, 91, W - 116, 103], fill=GREEN)
    draw.text((W - 104, 91), "Live", fill=GREEN, font=base_font(12))

    # Session info
    draw_card_outline(draw, 240, 538, 700, 100)
    draw.rectangle([258, 556, 274, 608], fill=(34, 197, 94))
    draw.text((284, 556), "Session Active", fill=GREEN, font=base_font(13))
    draw.text((284, 576), "Machine Learning — started 09:00", fill=TEXT_MUTED, font=base_font(11))
    draw.rectangle([820, 560, 920, 590], fill=(185, 28, 28))
    draw.text((835, 568), "End Session", fill=(255, 255, 255), font=base_font(11))

    # Present list
    draw_card_outline(draw, 960, 84, 300, 310)
    draw.text((978, 100), "Present", fill=TEXT_PRIMARY, font=base_font(13))
    draw.text((1225, 100), "27", fill=GREEN, font=base_font(16))

    present = [
        ("Riya Sharma", "09:02"),
        ("Arjun Mehta", "09:03"),
        ("Priya Nair", "09:05"),
        ("Dev Patel", "09:07"),
        ("Meena Roy", "09:09"),
        ("Rahul Verma", "09:11"),
        ("Sneha Joshi", "09:13"),
    ]
    for m, (pname, ptime) in enumerate(present):
        py = 126 + m * 40
        initials = pname[0]
        draw.ellipse([978, py, 1002, py + 24], fill=ACCENT)
        draw.text((983, py + 4), initials, fill=(255, 255, 255), font=base_font(12))
        draw.text((1010, py + 2), pname, fill=TEXT_PRIMARY, font=base_font(12))
        draw.text((1010, py + 16), ptime, fill=TEXT_MUTED, font=base_font(10))
        draw.line([968, py + 36, 1250, py + 36], fill=(30, 41, 59))

    # Manual mark
    draw_card_outline(draw, 960, 414, 300, 170)
    draw.text((978, 430), "Manual Mark", fill=TEXT_PRIMARY, font=base_font(13))
    draw.rectangle([978, 452, 1248, 476], fill=(15, 23, 42), outline=BORDER)
    draw.text((988, 458), "Search person...", fill=TEXT_MUTED, font=base_font(12))

    img.save(os.path.join(OUT, "live_attendance.png"), "PNG", optimize=True)
    print("live_attendance.png saved")


def make_persons():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_sidebar(draw, "persons")
    draw_topbar(draw, "People")

    draw.rectangle([240, 84, W - 20, 116], fill=(15, 23, 42), outline=BORDER)
    draw.text((258, 96), "Search by name, ID or department...", fill=TEXT_MUTED, font=base_font(12))
    draw.rectangle([W - 180, 82, W - 20, 118], fill=ACCENT_DARK)
    draw.text((W - 166, 94), "+ Register Person", fill=(255, 255, 255), font=base_font(12))

    people = [
        ("Riya Sharma", "STU001", "Computer Science", 12, True),
        ("Arjun Mehta", "STU002", "Electronics", 10, True),
        ("Priya Nair", "STU003", "Mathematics", 14, True),
        ("Dev Patel", "STU004", "Computer Science", 8, True),
        ("Meena Roy", "STU005", "Physics", 11, True),
        ("Rahul Verma", "STU006", "Chemistry", 9, True),
        ("Sneha Joshi", "STU007", "Computer Science", 0, False),
        ("Kiran Das", "STU008", "Electronics", 13, True),
    ]

    card_w = 240
    card_h = 140
    cols = 4
    for idx, (name, pid, dept, fcount, active) in enumerate(people):
        col = idx % cols
        row = idx // cols
        cx = 240 + col * (card_w + 14)
        cy = 134 + row * (card_h + 14)
        draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=CARD, outline=BORDER)

        grad_colors = [ACCENT, VIOLET, GREEN, (234, 88, 12), (236, 72, 153), (6, 182, 212), (245, 158, 11), ACCENT]
        gc = grad_colors[idx % len(grad_colors)]
        draw.ellipse([cx + 14, cy + 14, cx + 58, cy + 58], fill=gc)
        draw.text((cx + 28, cy + 25), name[0], fill=(255, 255, 255), font=base_font(18))

        draw.text((cx + 70, cy + 16), name, fill=TEXT_PRIMARY, font=base_font(12))
        draw.text((cx + 70, cy + 33), pid, fill=TEXT_SECONDARY, font=base_font(11))
        draw.text((cx + 70, cy + 49), dept, fill=TEXT_MUTED, font=base_font(10))

        dot_col = GREEN if fcount > 0 else YELLOW
        draw.ellipse([cx + 14, cy + 74, cx + 22, cy + 82], fill=dot_col)
        draw.text((cx + 28, cy + 72), f"{fcount} samples", fill=TEXT_MUTED, font=base_font(10))

        badge_col = (20, 83, 45) if active else (51, 65, 85)
        badge_text_col = GREEN if active else TEXT_MUTED
        draw.rectangle([cx + card_w - 70, cy + 70, cx + card_w - 14, cy + 88], fill=badge_col)
        draw.text((cx + card_w - 62, cy + 74), "active" if active else "inactive", fill=badge_text_col, font=base_font(10))

        draw.line([cx + 10, cy + card_h - 34, cx + card_w - 10, cy + card_h - 34], fill=BORDER)
        for bi, btn in enumerate(["History", "Export", "Delete"]):
            bx = cx + 14 + bi * 70
            draw.text((bx, cy + card_h - 22), btn, fill=TEXT_MUTED, font=base_font(10))

    img.save(os.path.join(OUT, "persons.png"), "PNG", optimize=True)
    print("persons.png saved")


def make_register():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_sidebar(draw, "persons")
    draw_topbar(draw, "Register New Person")

    # Details form card
    draw_card_outline(draw, 240, 84, 580, 230)
    draw.text((258, 100), "Person Details", fill=TEXT_PRIMARY, font=base_font(13))

    fields = [
        ("Full Name *", "Riya Sharma", 130, 240 + 18),
        ("Person ID *", "STU042", 130, 540 + 4),
        ("Department", "Computer Science", 190, 240 + 18),
        ("Email", "riya@college.edu", 190, 540 + 4),
    ]
    for label, placeholder, fy, fx in fields:
        draw.text((fx, fy - 16), label, fill=TEXT_SECONDARY, font=base_font(10))
        draw.rectangle([fx, fy, fx + 252, fy + 28], fill=(15, 23, 42), outline=BORDER)
        draw.text((fx + 10, fy + 8), placeholder, fill=TEXT_SECONDARY, font=base_font(11))

    draw.rectangle([258, 260, 360, 288], fill=ACCENT_DARK)
    draw.text((274, 268), "Create Profile", fill=(255, 255, 255), font=base_font(12))

    # Camera capture card
    draw_card_outline(draw, 240, 330, 580, 420)
    draw.text((258, 346), "Capture Face Samples", fill=TEXT_PRIMARY, font=base_font(13))
    draw.text((258, 366), "Position face clearly in frame. Capture at least 5 samples.", fill=TEXT_MUTED, font=base_font(11))

    cam_x, cam_y = 360, 392
    draw.rectangle([cam_x - 120, cam_y, cam_x + 240, cam_y + 200], fill=(10, 15, 28), outline=BORDER)

    face_cx, face_cy = cam_x + 60, cam_y + 80
    draw.ellipse([face_cx - 55, face_cy - 70, face_cx + 55, face_cy + 70], fill=(60, 40, 30))
    draw.ellipse([face_cx - 55, face_cy - 70, face_cx + 55, face_cy + 70], outline=GREEN, width=2)
    draw.ellipse([face_cx - 18, face_cy - 20, face_cx - 6, face_cy - 8], fill=(200, 160, 100))
    draw.ellipse([face_cx + 6, face_cy - 20, face_cx + 18, face_cy - 8], fill=(200, 160, 100))
    draw.arc([face_cx - 20, face_cy + 10, face_cx + 20, face_cy + 35], 10, 170, fill=(200, 160, 100), width=2)
    draw.text((cam_x - 110, cam_y + 206), "Face detected", fill=GREEN, font=base_font(10))

    btns = [
        ("Start Camera", (51, 65, 85), cam_x - 240),
        ("Capture Sample", ACCENT_DARK, cam_x - 130),
        ("Auto Capture (5x)", (109, 40, 217), cam_x + 20),
    ]
    for btn_label, btn_color, bx in btns:
        draw.rectangle([bx, cam_y + 224, bx + 110, cam_y + 250], fill=btn_color)
        draw.text((bx + 6, cam_y + 232), btn_label, fill=(255, 255, 255), font=base_font(10))

    draw.text((cam_x - 120, cam_y + 260), "5 samples captured", fill=TEXT_SECONDARY, font=base_font(11))

    for si in range(5):
        tx = cam_x - 115 + si * 70
        draw.rectangle([tx, cam_y + 280, tx + 60, cam_y + 340], fill=(20, 30, 50), outline=BORDER)
        draw.ellipse([tx + 15, cam_y + 295, tx + 45, cam_y + 330], fill=(60, 40, 30))

    draw.rectangle([258, cam_y + 358, 258 + 560, cam_y + 388], fill=(21, 128, 61))
    draw.text((440, cam_y + 366), "Save Person & Train Model", fill=(255, 255, 255), font=base_font(13))

    # Side info
    draw_card_outline(draw, 840, 84, 420, 440)
    draw.text((858, 100), "Registration Tips", fill=TEXT_PRIMARY, font=base_font(13))
    tips = [
        "Face front camera directly",
        "Ensure good lighting",
        "Capture from slight angles",
        "Aim for 8-15 samples",
        "Remove glasses for one set",
        "Try different expressions",
    ]
    for ti, tip in enumerate(tips):
        ty = 130 + ti * 36
        draw.ellipse([858, ty + 4, 868, ty + 14], fill=ACCENT)
        draw.text((876, ty), tip, fill=TEXT_SECONDARY, font=base_font(12))

    draw_card_outline(draw, 840, 544, 420, 116)
    draw.text((858, 560), "Current Status", fill=TEXT_PRIMARY, font=base_font(13))
    draw.ellipse([858, 590, 874, 606], fill=(20, 83, 45))
    draw.text((882, 590), "Profile created", fill=GREEN, font=base_font(12))
    draw.ellipse([858, 616, 874, 632], fill=(20, 83, 45))
    draw.text((882, 616), "5 face samples saved", fill=GREEN, font=base_font(12))

    img.save(os.path.join(OUT, "register_person.png"), "PNG", optimize=True)
    print("register_person.png saved")


def make_reports():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_sidebar(draw, "reports")
    draw_topbar(draw, "Reports")

    draw_card_outline(draw, 240, 84, 490, 170)
    draw.text((258, 100), "Export Session Report", fill=TEXT_PRIMARY, font=base_font(13))
    draw.rectangle([258, 124, 710, 152], fill=(15, 23, 42), outline=BORDER)
    draw.text((268, 132), "Machine Learning — 01 Mar 2026 09:00 (active)", fill=TEXT_SECONDARY, font=base_font(12))
    draw.rectangle([258, 162, 458, 188], fill=(51, 65, 85))
    draw.text((310, 170), "View Records", fill=(255, 255, 255), font=base_font(12))
    draw.rectangle([468, 162, 710, 188], fill=ACCENT_DARK)
    draw.text((540, 170), "Export CSV", fill=(255, 255, 255), font=base_font(12))

    draw_card_outline(draw, 750, 84, 510, 170)
    draw.text((768, 100), "Export Person Report", fill=TEXT_PRIMARY, font=base_font(13))
    draw.rectangle([768, 124, 1240, 152], fill=(15, 23, 42), outline=BORDER)
    draw.text((778, 132), "Riya Sharma (STU001)", fill=TEXT_SECONDARY, font=base_font(12))
    draw.rectangle([768, 162, 1240, 188], fill=ACCENT_DARK)
    draw.text((950, 170), "Export CSV", fill=(255, 255, 255), font=base_font(12))

    draw_card_outline(draw, 240, 274, 1020, 480)
    draw.text((258, 290), "All Sessions", fill=TEXT_PRIMARY, font=base_font(13))

    headers = ["ID", "Subject", "Title", "Start", "End", "Status", "Export"]
    hxs = [258, 308, 490, 680, 860, 1010, 1210]
    for hdr, hxp in zip(headers, hxs):
        draw.text((hxp, 320), hdr.upper(), fill=TEXT_MUTED, font=base_font(10))
    draw.line([248, 338, 1248, 338], fill=BORDER)

    rows = [
        ("#12", "Machine Learning", "Week 8 Lab", "01 Mar 09:00", "—", "active"),
        ("#11", "Data Structures", "Lecture 14", "28 Feb 11:00", "12:30", "completed"),
        ("#10", "Algorithms", "Tutorial", "27 Feb 14:00", "15:00", "completed"),
        ("#9", "Computer Networks", "Lab 5", "26 Feb 10:00", "11:30", "completed"),
        ("#8", "Machine Learning", "Week 7 Lab", "22 Feb 09:00", "10:30", "completed"),
        ("#7", "Data Structures", "Lecture 13", "21 Feb 11:00", "12:00", "completed"),
        ("#6", "Algorithms", "Problem Set", "20 Feb 14:00", "15:30", "completed"),
        ("#5", "Database Systems", "Lab 4", "19 Feb 10:00", "11:00", "completed"),
        ("#4", "Computer Networks", "Lab 4", "18 Feb 10:00", "11:30", "completed"),
    ]
    for ri, row in enumerate(rows):
        ry2 = 352 + ri * 42
        values = list(row)
        for ci, (val, hxp) in enumerate(zip(values, hxs)):
            if ci == 5:
                s_col = GREEN if val == "active" else TEXT_MUTED
                s_bg = (20, 83, 45) if val == "active" else (30, 41, 59)
                draw.rectangle([hxp, ry2 - 2, hxp + 80, ry2 + 16], fill=s_bg)
                draw.text((hxp + 8, ry2), val, fill=s_col, font=base_font(11))
            else:
                draw.text((hxp, ry2), val, fill=TEXT_SECONDARY if ci > 0 else TEXT_MUTED, font=base_font(11))
        if ci < len(rows) - 1:
            draw.line([248, ry2 + 28, 1248, ry2 + 28], fill=(22, 30, 46))
        draw.text((hxs[6], ry2), "CSV", fill=(96, 165, 250), font=base_font(11))

    img.save(os.path.join(OUT, "reports.png"), "PNG", optimize=True)
    print("reports.png saved")


if __name__ == "__main__":
    make_dashboard()
    make_live()
    make_persons()
    make_register()
    make_reports()
    print("All screenshots generated.")
