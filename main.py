import csv
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import defaultdict

# ===== ตั้งค่าฟอนต์ไทย =====
pdfmetrics.registerFont(TTFont('THSarabun', 'fonts/THSarabunNew/THSarabunNew.ttf'))

# ===== โฟลเดอร์เก็บรายงาน =====
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# ===== ฟังก์ชันรับข้อมูลจากผู้ใช้แล้วบันทึกเป็น CSV =====
def input_data():
    report_name = input("📄 ตั้งชื่อรายงาน (เช่น report_june_2025): ").strip()
    if not report_name:
        print("❌ ชื่อรายงานไม่ควรเว้นว่าง")
        return

    csv_path = os.path.join(REPORT_DIR, report_name + ".csv")
    if os.path.exists(csv_path):
        print("⚠️ รายงานนี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น หรือเลือกเมนูดูรายงาน")
        return

    data = []
    print("\n📋 เริ่มกรอกข้อมูล")
    print("พิมพ์ '1' หรือ '2' เพื่อเลือกประเภท, 'back' เพื่อย้อนกลับ, 'done' เพื่อเสร็จสิ้น, 'cancel' เพื่อยกเลิกทั้งหมด")

    while True:
        # เลือกประเภท
        print("\nเลือกประเภท:")
        print("1) รายรับ")
        print("2) รายจ่าย")
        type_choice = input("เลือก: ").strip().lower()

        if type_choice == 'done':
            # จบการกรอกข้อมูล
            break
        elif type_choice == 'cancel':
            print("🛑 ยกเลิกการสร้างรายงาน")
            return
        elif type_choice == 'back':
            # ลบข้อมูลรายการล่าสุดถ้ามี
            if data:
                removed = data.pop()
                print(f"⏪ ลบรายการล่าสุด: {removed}")
            else:
                print("❌ ยังไม่มีข้อมูลให้ย้อนกลับ")
            continue
        elif type_choice == '1':
            type_ = "รายรับ"
        elif type_choice == '2':
            type_ = "รายจ่าย"
        else:
            print("พิมพ์ '1' หรือ '2' เพื่อเลือกประเภท, 'back' เพื่อย้อนกลับ, 'done' เพื่อเสร็จสิ้น, 'cancel' เพื่อยกเลิกทั้งหมด")
            continue

        # กรอกหมวดหมู่
        category = input("หมวดหมู่ (หรือพิมพ์ 'back' เพื่อย้อนกลับ, 'cancel' เพื่อยกเลิก): ").strip()
        if category.lower() == 'back':
            continue
        if category.lower() == 'cancel':
            print("🛑 ยกเลิกการสร้างรายงาน")
            return
        if not category:
            print("❌ กรุณากรอกหมวดหมู่")
            continue

        # กรอกรายละเอียด
        detail = input("รายละเอียด (หรือพิมพ์ 'back' เพื่อย้อนกลับ, 'cancel' เพื่อยกเลิก): ").strip()
        if detail.lower() == 'back':
            continue
        if detail.lower() == 'cancel':
            print("🛑 ยกเลิกการสร้างรายงาน")
            return
        if not detail:
            print("❌ กรุณากรอกรายละเอียด")
            continue

        # กรอกจำนวนเงิน
        amount_input = input("จำนวนเงิน (หรือพิมพ์ 'back' เพื่อย้อนกลับ, 'cancel' เพื่อยกเลิก): ").strip()
        if amount_input.lower() == 'back':
            continue
        if amount_input.lower() == 'cancel':
            print("🛑 ยกเลิกการสร้างรายงาน")
            return

        try:
            amount = float(amount_input)
        except ValueError:
            print("❌ ต้องใส่จำนวนเงินเป็นตัวเลข")
            continue

        # เพิ่มข้อมูลใหม่
        data.append([type_, category, detail, amount])
        print("✅ เพิ่มข้อมูลเรียบร้อย")

    # บันทึกไฟล์ CSV ถ้ามีข้อมูล
    if data:
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["ประเภท", "หมวดหมู่", "รายละเอียด", "จำนวนเงิน"])
            writer.writerows(data)
        print(f"\n✅ รายงานถูกบันทึกไว้ที่: {csv_path}")
    else:
        print("❌ ไม่มีข้อมูลที่ถูกบันทึก")


# ===== ฟังก์ชันดูรายงานเก่าและสร้าง PDF จาก CSV ได้ =====
def list_reports():
    reports = [f for f in os.listdir(REPORT_DIR) if f.endswith(".csv")]
    if not reports:
        print("📭 ยังไม่มีรายงาน")
        return

    print("\n📑 รายงานทั้งหมด:")
    for i, r in enumerate(reports, 1):
        print(f"{i}) {r}")

    choice = input("เลือกหมายเลขรายงาน หรือพิมพ์ 'back' เพื่อย้อนกลับ: ")
    if choice.lower() == "back":
        return

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(reports):
            print("❌ หมายเลขไม่ถูกต้อง")
            return
        report_file = reports[index]
        csv_path = os.path.join(REPORT_DIR, report_file)

        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            reader = list(csv.reader(f))
            print("\n🔍 รายละเอียดรายงาน:")
            for i, row in enumerate(reader):
                if i == 0:
                    print(f"{row[0]:<10} | {row[1]:<20} | {row[2]:<30} | {row[3]}")
                    print("-" * 85)
                else:
                    print(f"{row[0]:<10} | {row[1]:<20} | {row[2]:<30} | {float(row[3]):,.2f}")

        generate_pdf_from_csv(csv_path, report_file.replace(".csv", ""))
    except Exception as e:
        print("❌ ผิดพลาด:", e)


# ===== ฟังก์ชันสร้าง PDF จาก CSV =====
def generate_pdf_from_csv(csv_path, report_title):
    income = defaultdict(list)
    expense = defaultdict(list)

    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = (row["รายละเอียด"], float(row["จำนวนเงิน"]))
            if row["ประเภท"] == "รายรับ":
                income[row["หมวดหมู่"]].append(entry)
            else:
                expense[row["หมวดหมู่"]].append(entry)

    pdf_path = os.path.join(REPORT_DIR, report_title + ".pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    c.setFont("THSarabun", 16)

    x_income = 40
    x_expense = 320
    y = height - 50

    def draw_section(items, x, y_start):
        y = y_start
        total = 0
        for section, entries in items.items():
            c.drawString(x, y, f"{section}")
            y -= 18
            for name, amount in entries:
                c.drawString(x + 20, y, f"{name}")
                c.drawRightString(x + 200, y, f"{amount:,.2f}")
                total += amount
                y -= 18
            y -= 8
        return y, total

    c.drawString(x_income, y, "รายรับ")
    c.drawString(x_expense, y, "รายจ่าย")
    y -= 25

    y_income, total_income = draw_section(income, x_income, y)
    y_expense, total_expense = draw_section(expense, x_expense, y)

    y_total = min(y_income, y_expense) - 20
    c.drawString(x_income, y_total, "รวมรายรับ")
    c.drawRightString(x_income + 200, y_total, f"{total_income:,.2f}")
    c.drawString(x_expense, y_total, "รวมรายจ่าย")
    c.drawRightString(x_expense + 200, y_total, f"{total_expense:,.2f}")

    y_total -= 18
    diff = total_income - total_expense
    c.drawString(x_expense, y_total, "รายรับ สูง ต่ำ กว่ารายจ่าย")
    c.drawRightString(x_expense + 200, y_total, f"({abs(diff):,.2f})")

    c.save()
    print(f"📄 สร้าง PDF แล้ว: {pdf_path}")

def edit_report():
    reports = [f for f in os.listdir(REPORT_DIR) if f.endswith(".csv")]
    if not reports:
        print("📭 ยังไม่มีรายงานให้แก้ไข")
        return

    print("\n📝 รายงานที่สามารถแก้ไขได้:")
    for i, r in enumerate(reports, 1):
        print(f"{i}) {r}")

    choice = input("เลือกหมายเลขรายงานที่ต้องการแก้ไข หรือพิมพ์ 'back' เพื่อย้อนกลับ: ").strip()
    if choice.lower() == "back":
        return

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(reports):
            print("❌ หมายเลขไม่ถูกต้อง")
            return
        report_file = reports[index]
        csv_path = os.path.join(REPORT_DIR, report_file)

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = list(csv.reader(f))

        if len(reader) <= 1:
            print("❌ ไม่มีข้อมูลให้แก้ไข")
            return

        while True:
            print(f"\n📋 รายการใน {report_file}:")
            for i, row in enumerate(reader):
                if i == 0:
                    print(f"{'No.':<4} | {row[0]:<10} | {row[1]:<15} | {row[2]:<20} | {row[3]}")
                    print("-" * 80)
                else:
                    print(f"{i:<4} | {row[0]:<10} | {row[1]:<15} | {row[2]:<20} | {float(row[3]):,.2f}")

            print("\n🛠️ ตัวเลือก:")
            print("1) แก้ไขแถว")
            print("2) ลบแถว")
            print("3) เพิ่มแถวใหม่")
            print("4) กลับเมนูหลัก")
            action = input("เลือกหมายเลขการดำเนินการ: ").strip()

            if action == '1':
                row_choice = input("กรุณาเลือกหมายเลขแถวที่ต้องการ *แก้ไข* (ยกเว้นหัวตาราง): ").strip()
                if not row_choice.isdigit():
                    continue
                row_index = int(row_choice)
                if row_index <= 0 or row_index >= len(reader):
                    print("❌ หมายเลขแถวไม่ถูกต้อง")
                    continue

                old_row = reader[row_index]
                print(f"\n🔧 กำลังแก้ไข: {old_row}")

                type_ = input(f"ประเภท (รายรับ/รายจ่าย) [{old_row[0]}]: ").strip() or old_row[0]
                category = input(f"หมวดหมู่ [{old_row[1]}]: ").strip() or old_row[1]
                detail = input(f"รายละเอียด [{old_row[2]}]: ").strip() or old_row[2]
                amount_input = input(f"จำนวนเงิน [{old_row[3]}]: ").strip() or old_row[3]

                try:
                    amount = float(amount_input)
                except ValueError:
                    print("❌ จำนวนเงินต้องเป็นตัวเลข")
                    continue

                reader[row_index] = [type_, category, detail, amount]
                print("✅ แก้ไขสำเร็จ")

            elif action == '2':
                row_choice = input("กรุณาเลือกหมายเลขแถวที่ต้องการ *ลบ* (ยกเว้นหัวตาราง): ").strip()
                if not row_choice.isdigit():
                    continue
                row_index = int(row_choice)
                if row_index <= 0 or row_index >= len(reader):
                    print("❌ หมายเลขแถวไม่ถูกต้อง")
                    continue

                confirm = input(f"คุณแน่ใจหรือไม่ที่จะลบรายการนี้: {reader[row_index]} (yes/no): ").strip().lower()
                if confirm == 'yes':
                    removed = reader.pop(row_index)
                    print(f"🗑️ ลบสำเร็จ: {removed}")
                else:
                    print("❎ ยกเลิกการลบ")

            elif action == '3':
                print("\n➕ เพิ่มรายการใหม่")
                type_ = input("ประเภท (รายรับ/รายจ่าย): ").strip()
                if type_ not in ["รายรับ", "รายจ่าย"]:
                    print("❌ ประเภทไม่ถูกต้อง")
                    continue
                category = input("หมวดหมู่: ").strip()
                detail = input("รายละเอียด: ").strip()
                amount_input = input("จำนวนเงิน: ").strip()
                try:
                    amount = float(amount_input)
                except ValueError:
                    print("❌ จำนวนเงินไม่ถูกต้อง")
                    continue

                reader.append([type_, category, detail, amount])
                print("✅ เพิ่มรายการสำเร็จ")

            elif action == '4':
                break
            else:
                print("❌ กรุณาเลือก 1-4 เท่านั้น")
                continue

            # เขียนกลับไฟล์ CSV ทุกครั้งที่มีการเปลี่ยนแปลง
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(reader)

    except Exception as e:
        print("❌ ผิดพลาด:", e)


# ===== เมนูหลัก =====
def main():
    while True:
        print("\n======= ระบบจัดการรายงานรายรับรายจ่าย =======")
        print("1) สร้างรายงานใหม่")
        print("2) ดูรายงานเดิม และแปลงเป็น PDF")
        print("3) แก้ไขรายงาน CSV")
        print("4) ออกจากโปรแกรม")
        choice = input("เลือกเมนู: ")

        if choice == '1':
            input_data()
        elif choice == '2':
            list_reports()
        elif choice == '3':
            edit_report()
        elif choice == '4':
            print("👋 ออกจากโปรแกรมแล้ว")
            break
        else:
            print("❌ กรุณาเลือกเมนู 1, 2 หรือ 3 เท่านั้น")


if __name__ == "__main__":
    main()
