"""Fill midterm Word report from template fields."""
from __future__ import annotations

from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt

FOLDER = Path(r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\MIdterm project")
SRC = next(FOLDER.glob("*รายงาน*.docx"))
OUT = FOLDER / "รายงานโครงงานเกม_กล่องข้าวน้อย.docx"
DEMO1 = Path(r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\docs\demo1.jpg")
DEMO2 = Path(r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\docs\demo2.jpg")
UI_MENU = Path(r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\Assets\Generated\UI\ui_menu.png")


def main() -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "TH Sarabun New"
    style.font.size = Pt(16)

    doc.add_heading("โครงงานเกม 2D", level=0)
    doc.add_paragraph("วิชา [x] CP410844 Computer Game Development")
    doc.add_paragraph("ภาคการศึกษาต้น ปีการศึกษา 2569")
    doc.add_paragraph("ชื่อเกม: A Mother's Walk (กล่องข้าวน้อย)")
    doc.add_paragraph("กลุ่มที่: 4")
    doc.add_paragraph("จัดทำโดย:")
    doc.add_paragraph("673380348-4 นายสรวิศ สำราญบึงแก สาขา CP-AI")
    doc.add_paragraph("673380308-6 นายจักรภัทร เวียงสิมมา สาขา CP-AI")
    doc.add_paragraph("673380328-0 นายพรหมพัฒน ศิริภัคกุลวัฒน์ สาขา CP-AI")

    doc.add_heading("ธีม หรือ แนวเกม (Game Genres)", level=1)
    doc.add_paragraph(
        "2D Platformer / Adventure ที่ตีความนิทานพื้นบ้านไทย "
        "“กล่องข้าวน้อยฆ่าแม่” ในมุมมองของมารดา โทนศิลปะพิกเซลแนวชนบทไทย"
    )

    doc.add_heading("กลุ่มเป้าหมาย", level=1)
    doc.add_paragraph(
        "นักเรียนนักศึกษาและผู้เล่นทั่วไปที่สนใจเกมสั้นเล่นง่าย "
        "อายุประมาณ 12 ปีขึ้นไป เล่นได้ทั้งคีย์บอร์ดและหน้าจอสัมผัส"
    )

    doc.add_heading("เนื้อเรื่องย่อ", level=1)
    doc.add_paragraph(
        "แม่ของไอ้ทองออกจากหมู่บ้านเพื่อนำกล่องข้าวไปส่งลูกชายที่กำลังทำนา "
        "ระหว่างทางต้องฝ่าสัตว์ป่า กับดัก และอุปสรรคธรรมชาติ "
        "ขณะที่ความอดทนของไอ้ทองลดลงเรื่อยๆ หากไปไม่ทัน แม่จะล้มเหลวในภารกิจ "
        "ผู้เล่นอาจแวะช่วยชาวบ้านเพื่อชะลอความอดทนของลูก "
        "จนถึงด่านสุดท้ายที่ส่งกล่องข้าวให้อ้ายทองสำเร็จ"
    )

    doc.add_heading("รูปแบบการเล่น และ กติกา", level=1)
    bullets = [
        "เดินซ้าย/ขวาด้วย A/D หรือลูกศร กระโดดด้วย Space ปาหินด้วย J",
        "มีพลังชีวิต (หลอดเลือด) และหัวใจชีวิต หากเลือดหมดจะเสียชีวิต 1 ดวง",
        "หลอดความอดทนของไอ้ทองลดลงตามเวลา หมดแล้วถือว่าภารกิจล้มเหลว",
        "หินมีจำนวนจำกัด เก็บก้อนหินเพื่อเติมกระสุน",
        "หมูป่าต้องยิงหลายครั้ง ชนแล้วเลือดเหลือครึ่ง / ควายยิงหลายครั้ง ชนแล้วตายทันที",
        "มีจุดพัก (checkpoint) กลางด่าน ตายแล้วเกิดที่จุดล่าสุด",
        "บางจุดช่วยชาวบ้านได้เพื่อเพิ่มความอดทนและกระสุน",
        "ด่าน 5 มีปริศนาสวิตช์เปิดประตู/สะพานก่อนไปต่อ",
        "ผ่าน 6 ด่านจนส่งกล่องข้าวสำเร็จ",
    ]
    for b in bullets:
        doc.add_paragraph(b, style="List Bullet")

    doc.add_heading("ตัวละคร", level=1)
    chars = [
        "แม่ (ผู้เล่น) — นางเอก ถือกระติ๊บข้าว เดินทางส่งอาหารให้ลูก",
        "ไอ้ทอง — ลูกชายที่รออยู่กลางทุ่ง ความอดทนลดลงตามเวลา",
        "หมูป่า / งู / นกกา / ควาย — ศัตรูตามเส้นทาง",
        "ชาวบ้าน — NPC ที่ขอความช่วยเหลือระหว่างทาง",
    ]
    for c in chars:
        doc.add_paragraph(c, style="List Bullet")

    doc.add_heading("ไอเทม ปริศนา และ กับดักต่าง ๆ", level=1)
    items = [
        "กระติ๊บข้าว — คะแนน",
        "หัวใจ — ฟื้นเลือด (บางดวงเพิ่มชีวิต)",
        "ก้อนหิน — เติมกระสุน",
        "น้ำเต้าความเร็ว / ใบพลู — บูสต์ชั่วคราว",
        "จุดพักศาล — checkpoint",
        "สวิตช์และประตู — ปริศนาด่าน 5",
        "กับดัก: หนาม หอก ใบมีด ลูกตุ้มหิน",
        "แพเลื่อน / ลิฟต์ / กระดานดีด",
    ]
    for i in items:
        doc.add_paragraph(i, style="List Bullet")

    doc.add_heading("ด่าน/ฉาก", level=1)
    levels = [
        "ด่าน 1 — ออกจากหมู่บ้าน: เรียนรู้การควบคุม ช่วยชาวบ้าน",
        "ด่าน 2 — ป่าไผ่: แพเลื่อน จุดพัก อีกา",
        "ด่าน 3 — ทางขรุขระ: ลิฟต์ ควาย ลูกตุ้ม",
        "ด่าน 4 — ทุ่งนากลางทาง: ศัตรูผสม กระดานดีด",
        "ด่าน 5 — คูน้ำกลางคืน: ปริศนาสวิตช์เปิดประตู",
        "ด่าน 6 — ส่งกล่องข้าวให้อ้ายทอง: climax ส่งอาหารสำเร็จ",
    ]
    for lv in levels:
        doc.add_paragraph(lv, style="List Bullet")

    doc.add_paragraph("ภาพตัวอย่างหน้าจอเกม:")
    if DEMO1.exists():
        doc.add_picture(str(DEMO1), width=Inches(4.5))
    if DEMO2.exists():
        doc.add_picture(str(DEMO2), width=Inches(4.5))
    if UI_MENU.exists():
        doc.add_picture(str(UI_MENU), width=Inches(4.5))

    doc.add_heading("ประโยชน์ของเกม", level=1)
    doc.add_paragraph(
        "ส่งเสริมการอนุรักษ์นิทานพื้นบ้านผ่านสื่ออินเทอร์แอคทีฟ "
        "ฝึกการแก้ปัญหาและการบริหารเวลา (หลอดความอดทน) "
        "และเป็นผลงานการเรียนรู้การพัฒนาเกม 2D ด้วย Godot ของนักศึกษา"
    )

    doc.add_heading("ลิงก์ผลงาน", level=1)
    doc.add_paragraph("GitHub: https://github.com/ppppppwaqrd/a-mothers-walk-midterm")
    doc.add_paragraph("GitHub Pages: https://ppppppwaqrd.github.io/a-mothers-walk-midterm/")
    doc.add_paragraph("itch.io: (ใส่ลิงก์หลังอัปโหลด)")

    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
