import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import csv
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import defaultdict

pdfmetrics.registerFont(TTFont('THSarabun', 'fonts/THSarabunNew/THSarabunNew.ttf'))
pdfmetrics.registerFont(TTFont('THSarabun-Bold', 'fonts/THSarabunNew/THSarabunNew Bold.ttf'))
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# บันทึกข้อมูลลง CSV
def save_to_csv(report_name, data):
    csv_path = os.path.join(REPORT_DIR, report_name + ".csv")
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["ประเภท", "หมวดหมู่", "รายละเอียด", "จำนวนเงิน"])
        writer.writerows(data)
    return csv_path

# อ่านรายงานทั้งหมด
def list_all_reports():
    return [f for f in os.listdir(REPORT_DIR) if f.endswith(".csv")]

# สร้าง PDF จาก CSV
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
        current_main = ""

        for section, entries in items.items():
            parts = [s.strip() for s in section.split(">")]
            main_cat = parts[0]
            sub_cat = parts[1] if len(parts) > 1 else None

            # วาดหมวดหมู่หลัก ถ้ายังไม่เคยวาด
            if current_main != main_cat:
                current_main = main_cat
                c.setFont("THSarabun-Bold", 16)
                c.drawString(x, y, main_cat)
                y -= 20

            # วาดหมวดย่อย (ถ้ามี)
            if sub_cat:
                c.setFont("THSarabun-Bold", 15)
                c.drawString(x + 20, y, sub_cat)
                y -= 18

            # วาดรายละเอียด
            for name, amount in entries:
                c.setFont("THSarabun", 15)
                c.drawString(x + 20, y, name)
                c.drawRightString(x + 200, y, f"{amount:,.2f}")
                total += amount
                y -= 18

            y -= 10
        return y, total

    # หัวข้อ
    c.setFont("THSarabun-Bold", 18)
    c.drawString(x_income, y, "รายรับ")
    c.drawString(x_expense, y, "รายจ่าย")
    y -= 25

    # แสดงรายการรายรับ-รายจ่าย
    y_income, total_income = draw_section(income, x_income, y)
    y_expense, total_expense = draw_section(expense, x_expense, y)

    # ส่วนรวมยอด
    y_total = min(y_income, y_expense) - 30
    c.setFont("THSarabun-Bold", 16)

    c.drawString(x_income, y_total, "รวมรายรับ")
    c.drawRightString(x_income + 200, y_total, f"{total_income:,.2f}")

    c.drawString(x_expense, y_total, "รวมรายจ่าย")
    c.drawRightString(x_expense + 200, y_total, f"{total_expense:,.2f}")

    # รายรับสูง/ต่ำกว่ารายจ่าย
    y_total -= 20
    diff = total_income - total_expense

    if diff > 0:
        c.drawString(x_expense, y_total, "รายรับ สูง กว่า รายจ่าย")
        c.drawRightString(x_expense + 200, y_total, f"({abs(diff):,.2f})")
    elif diff < 0:
        c.drawString(x_expense, y_total, "รายรับ ต่ำ กว่า รายจ่าย")
        c.drawRightString(x_expense + 200, y_total, f"({abs(diff):,.2f})")
    else:
        c.drawString(x_expense, y_total, "รายรับ เท่ากับ รายจ่าย")
        c.drawRightString(x_expense + 200, y_total, f"{0:,.2f}")

    c.save()
    return pdf_path

# === สร้าง UI หลัก ===
root = tk.Tk()
root.title("📊 ระบบรายรับรายจ่าย")
root.geometry("400x550")

def create_report_ui():
    win = tk.Toplevel(root)
    win.title("สร้างรายงานใหม่")
    win.geometry("1000x600")

    tk.Label(win, text="ชื่อรายงาน (ไม่ต้องใส่ .csv)", font=("TH Sarabun New", 16)).pack(pady=5)
    name_var = tk.StringVar()
    tk.Entry(win, textvariable=name_var, font=("TH Sarabun New", 16)).pack(pady=5)

    data = []

    style = ttk.Style()
    style.configure("Treeview", font=("TH Sarabun New", 16), rowheight=28)
    style.configure("Treeview.Heading", font=("TH Sarabun New", 16, "bold"))

    tree_frame = tk.Frame(win)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=("ประเภท", "หมวดหมู่", "รายละเอียด", "จำนวนเงิน"),
                        show="headings", yscrollcommand=tree_scroll.set)
    tree_scroll.config(command=tree.yview)

    for col in ("ประเภท", "หมวดหมู่", "รายละเอียด", "จำนวนเงิน"):
        tree.heading(col, text=col)
        tree.column(col, width=140)
    tree.pack(fill="both", expand=True)

    def add_entry():
        CATEGORY_OPTIONS = {
            "รายรับ": [
                "กองทุนกรรมการ", "กองทุนการศึกษา", "งานไหว้บรรพบุรุษ (ตรุษจีน)",
                "งานไหว้พระจันทร์", "สนับสนุนหนังสือทำเนียบ", "ค่าทำป้ายแกะสลัก",
                "ค่าตั้งป้ายบรรพบุรุษ", "ดอกเบี้ยรับ", "รับบริจาคทั่วไป",
                "รับบริจาคสนับสนุนโครงการ", "อื่นๆ"
            ],
            "รายจ่าย": [
                "เงินเดือน", "ค่ารถ ค่าล่วงเวลาผจก.", "การดำเนินงานและกิจกรรม",
                "การศึกษา และเยาวชน", "เครื่องใช้สำนักงาน และวัสดุสิ้นเปลือง",
                "ซ่อมแซม ค่าจ้างและค่าแรง", "ค่าสาธารณูปโภค", "อื่นๆ"
            ]
        }

        top = tk.Toplevel(win)
        top.title("เพิ่มข้อมูล")
        top.geometry("600x600")

        form_frame = tk.Frame(top)
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # ประเภท
        tk.Label(form_frame, text="ประเภท:", font=("TH Sarabun New", 16)).grid(row=0, column=0, sticky="w")
        type_var = tk.StringVar(value="รายรับ")
        type_menu = ttk.Combobox(form_frame, textvariable=type_var, values=["รายรับ", "รายจ่าย"],
                                 state="readonly", font=("TH Sarabun New", 16))
        type_menu.grid(row=0, column=1, sticky="w")

        # หมวดหมู่หลัก
        tk.Label(form_frame, text="หมวดหมู่หลัก:", font=("TH Sarabun New", 16)).grid(row=1, column=0, sticky="w")
        cat_var = tk.StringVar()
        cat_menu = ttk.Combobox(form_frame, textvariable=cat_var, state="readonly", font=("TH Sarabun New", 16))
        cat_menu.grid(row=1, column=1, sticky="w")

        def update_categories(*args):
            selected_type = type_var.get()
            options = CATEGORY_OPTIONS[selected_type]
            cat_menu['values'] = options
            cat_var.set(options[0])

        type_var.trace("w", update_categories)
        update_categories()

        # หมวดย่อย (พิมพ์เอง)
        use_subcat_var = tk.BooleanVar()
        subcat_var = tk.StringVar()

        tk.Checkbutton(form_frame, text="เพิ่มหมวดย่อย", variable=use_subcat_var,
                       font=("TH Sarabun New", 16),
                       command=lambda: subcat_entry.grid() if use_subcat_var.get() else subcat_entry.grid_remove()
                       ).grid(row=2, column=0, sticky="w")

        subcat_entry = tk.Entry(form_frame, textvariable=subcat_var, font=("TH Sarabun New", 16))
        subcat_entry.grid(row=2, column=1, sticky="w")
        subcat_entry.grid_remove()

        # รายละเอียดและจำนวนเงิน
        tk.Label(form_frame, text="รายละเอียดและจำนวนเงิน:", font=("TH Sarabun New", 16)).grid(row=3, column=0, sticky="w")
        details_frame = tk.Frame(form_frame)
        details_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky="w")

        detail_entries = []

        def add_detail_row():
            row_frame = tk.Frame(details_frame)
            row_frame.pack(pady=2, anchor="w")
            d_var = tk.StringVar()
            a_var = tk.StringVar()
            tk.Entry(row_frame, textvariable=d_var, font=("TH Sarabun New", 16), width=30).pack(side="left", padx=5)
            tk.Entry(row_frame, textvariable=a_var, font=("TH Sarabun New", 16), width=10).pack(side="left", padx=5)
            detail_entries.append((d_var, a_var))

        add_detail_row()

        tk.Button(form_frame, text="+ เพิ่มแถว", font=("TH Sarabun New", 14), command=add_detail_row).grid(row=5, column=0, columnspan=2, pady=5)

        def confirm_add_all():
            valid_rows = []
            for d_var, a_var in detail_entries:
                desc = d_var.get().strip()
                try:
                    amt = float(a_var.get())
                    if desc:
                        valid_rows.append((desc, amt))
                except:
                    continue

            if not valid_rows:
                messagebox.showwarning("ยังไม่มีรายการ", "กรุณากรอกรายละเอียดพร้อมจำนวนเงินอย่างน้อย 1 รายการ")
                return

            category = cat_var.get()
            if use_subcat_var.get():
                sub = subcat_var.get().strip()
                if sub:
                    category = f"{category} > {sub}"

            for desc, amt in valid_rows:
                data.append([type_var.get(), category, desc, amt])

            refresh()
            top.destroy()

        tk.Button(top, text="เพิ่มทั้งหมด", command=confirm_add_all, font=("TH Sarabun New", 16)).pack(pady=10)

    def refresh():
        for i in tree.get_children():
            tree.delete(i)
        for row in data:
            tree.insert('', 'end', values=row)

    def save():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("คำเตือน", "กรุณากรอกชื่อรายงาน")
            return
        if not data:
            messagebox.showwarning("คำเตือน", "ไม่มีข้อมูลให้บันทึก")
            return

        file_path = os.path.join(REPORT_DIR, name + ".csv")
        if os.path.exists(file_path):
            messagebox.showerror("ชื่อซ้ำ", f"มีรายงานชื่อ '{name}.csv' อยู่แล้ว กรุณาใช้ชื่ออื่น")
            return

        save_to_csv(name, data)
        messagebox.showinfo("สำเร็จ", f"บันทึก {name}.csv สำเร็จแล้ว")
        win.destroy()

    button_frame = tk.Frame(win)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="เพิ่มข้อมูล", command=add_entry, font=("TH Sarabun New", 16), width=20).pack(pady=5)
    tk.Button(button_frame, text="บันทึกทั้งหมด", command=save, font=("TH Sarabun New", 16), width=20).pack(pady=5)

# ==== ดูรายงานและแปลงเป็น PDF (placeholder) ====
def view_report_ui():
    reports = list_all_reports()
    if not reports:
        messagebox.showinfo("ไม่มีรายงาน", "ยังไม่มีรายงานในระบบ")
        return

    def open_and_generate(report_file):
        csv_path = os.path.join(REPORT_DIR, report_file)
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            reader = list(csv.reader(f))
            view_win = tk.Toplevel(root)
            view_win.title(f"ดูรายงาน: {report_file}")
            view_win.geometry("800x400")

            tree = ttk.Treeview(view_win, columns=reader[0], show="headings")
            for col in reader[0]:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            for row in reader[1:]:
                tree.insert('', 'end', values=row)
            tree.pack(expand=True, fill="both", padx=10, pady=10)

            def export_pdf():
                pdf_path = generate_pdf_from_csv(csv_path, report_file.replace(".csv", ""))
                os.startfile(pdf_path)
                view_win.destroy()
                messagebox.showinfo("สำเร็จ", f"แปลงเป็น PDF สำเร็จแล้วบันทึกที่: {pdf_path}")

            tk.Button(view_win, text="แปลงเป็น PDF", command=export_pdf).pack(pady=10)

    selector = tk.Toplevel(root)
    selector.title("เลือกไฟล์รายงานเพื่อดู")
    selector.geometry("400x550")

    tk.Label(selector, text="รายงานทั้งหมด", font=("TH Sarabun New", 16, "bold")).pack(pady=5)

    # ✅ เพิ่ม Scrollbar
    frame = tk.Frame(selector)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(frame, font=("TH Sarabun New", 16), height=10, yscrollcommand=scrollbar.set)
    for r in reports:
        listbox.insert(tk.END, r)
    listbox.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=listbox.yview)

    def on_select():
        selected = listbox.curselection()
        if not selected:
            return
        selector.destroy()
        open_and_generate(reports[selected[0]])

    tk.Button(selector, text="ดูรายงาน", command=on_select, font=("TH Sarabun New", 16)).pack(pady=10)

CATEGORY_OPTIONS = {
    "รายรับ": [
        "กองทุนกรรมการ", "กองทุนการศึกษา", "งานไหว้บรรพบุรุษ (ตรุษจีน)",
        "งานไหว้พระจันทร์", "สนับสนุนหนังสือทำเนียบ", "ค่าทำป้ายแกะสลัก",
        "ค่าตั้งป้ายบรรพบุรุษ", "ดอกเบี้ยรับ", "รับบริจาคทั่วไป",
        "รับบริจาคสนับสนุนโครงการ", "อื่นๆ"
    ],
    "รายจ่าย": [
        "เงินเดือน", "ค่ารถ ค่าล่วงเวลาผจก.", "การดำเนินงานและกิจกรรม",
        "การศึกษา และเยาวชน", "เครื่องใช้สำนักงาน และวัสดุสิ้นเปลือง",
        "ซ่อมแซม ค่าจ้างและค่าแรง", "ค่าสาธารณูปโภค", "อื่นๆ"
    ]
}

# ===== ฟังก์ชันแก้ไขรายงาน =====
def edit_report_ui():
    reports = list_all_reports()
    if not reports:
        messagebox.showinfo("ไม่มีรายงาน", "ยังไม่มีรายงานในระบบ")
        return

    def open_report_editor(report_file):
        data = []

        def load_selected_report():
            path = os.path.join(REPORT_DIR, report_file)
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
                data.clear()
                data.extend(rows[1:])
                refresh_table()

        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            for i, row in enumerate(data):
                if search_var.get().lower() in str(row).lower():
                    tree.insert('', 'end', iid=i, values=row)

        def delete_selected():
            selected = tree.selection()
            if not selected:
                return
            confirm = messagebox.askyesno("ยืนยันการลบ", "คุณแน่ใจหรือไม่ว่าต้องการลบรายการที่เลือก?")
            if not confirm:
                return
            for item in selected:
                tree.delete(item)
                del data[int(item)]
            refresh_table()

        def update_selected():
            selected = tree.selection()
            if not selected:
                return
            item = selected[0]
            values = tree.item(item, 'values')

            update_win = tk.Toplevel(win)
            update_win.title("แก้ไขรายการ")
            update_win.geometry("400x370")

            tk.Label(update_win, text="ประเภท:", font=("TH Sarabun New", 16)).pack()
            type_var = tk.StringVar(value=values[0])
            type_menu = ttk.Combobox(update_win, textvariable=type_var, values=["รายรับ", "รายจ่าย"],
                                     state="readonly", font=("TH Sarabun New", 16))
            type_menu.pack()

            main_cat = values[1].split(">")[0].strip()
            sub_cat = values[1].split(">")[1].strip() if ">" in values[1] else ""

            tk.Label(update_win, text="หมวดหมู่หลัก:", font=("TH Sarabun New", 16)).pack()
            cat_var = tk.StringVar(value=main_cat)
            cat_menu = ttk.Combobox(update_win, textvariable=cat_var,
                                    font=("TH Sarabun New", 16), state="readonly")
            cat_menu.pack()

            def update_cat_options(*args):
                cat_menu['values'] = CATEGORY_OPTIONS[type_var.get()]
                if cat_var.get() not in CATEGORY_OPTIONS[type_var.get()]:
                    cat_var.set(CATEGORY_OPTIONS[type_var.get()][0])

            type_var.trace("w", update_cat_options)
            update_cat_options()

            subcat_frame = tk.Frame(update_win)
            subcat_frame.pack(pady=5)

            use_subcat_var = tk.BooleanVar(value=bool(sub_cat))
            subcat_var = tk.StringVar(value=sub_cat)

            tk.Checkbutton(subcat_frame, text="มีหมวดย่อย", variable=use_subcat_var,
                           font=("TH Sarabun New", 16),
                           command=lambda: subcat_entry.grid(row=0, column=1, padx=5)
                           if use_subcat_var.get() else subcat_entry.grid_remove()
                           ).grid(row=0, column=0, sticky="w")

            subcat_entry = tk.Entry(subcat_frame, textvariable=subcat_var, font=("TH Sarabun New", 16))
            if sub_cat:
                subcat_entry.grid(row=0, column=1, padx=5)
            else:
                subcat_entry.grid_remove()

            tk.Label(update_win, text="รายละเอียด:", font=("TH Sarabun New", 16)).pack()
            detail_var = tk.StringVar(value=values[2])
            tk.Entry(update_win, textvariable=detail_var, font=("TH Sarabun New", 16)).pack()

            tk.Label(update_win, text="จำนวนเงิน:", font=("TH Sarabun New", 16)).pack()
            amount_var = tk.StringVar(value=values[3])
            tk.Entry(update_win, textvariable=amount_var, font=("TH Sarabun New", 16)).pack()

            def save_changes():
                try:
                    amount = float(amount_var.get())
                except ValueError:
                    messagebox.showwarning("คำเตือน", "จำนวนเงินต้องเป็นตัวเลข")
                    return
                category = cat_var.get()
                if use_subcat_var.get() and subcat_var.get().strip():
                    category += f" > {subcat_var.get().strip()}"
                new_row = [type_var.get(), category, detail_var.get(), amount]
                data[int(item)] = new_row
                refresh_table()
                update_win.destroy()

            tk.Button(update_win, text="บันทึก", command=save_changes,
                      font=("TH Sarabun New", 16)).pack(pady=10)

        def add_new_entry():
            top = tk.Toplevel(win)
            top.title("เพิ่มรายการใหม่")
            top.geometry("600x500")

            form_frame = tk.Frame(top)
            form_frame.pack(pady=10, padx=20)

            tk.Label(form_frame, text="ประเภท:", font=("TH Sarabun New", 16)).grid(row=0, column=0, sticky="w")
            type_var = tk.StringVar(value="รายรับ")
            type_menu = ttk.Combobox(form_frame, textvariable=type_var, values=["รายรับ", "รายจ่าย"], state="readonly", font=("TH Sarabun New", 16))
            type_menu.grid(row=0, column=1, sticky="w")

            tk.Label(form_frame, text="หมวดหมู่หลัก:", font=("TH Sarabun New", 16)).grid(row=1, column=0, sticky="w")
            cat_var = tk.StringVar()
            cat_menu = ttk.Combobox(form_frame, textvariable=cat_var, font=("TH Sarabun New", 16), state="readonly")
            cat_menu.grid(row=1, column=1, sticky="w")

            def update_categories(*args):
                selected = type_var.get()
                cat_menu['values'] = CATEGORY_OPTIONS[selected]
                cat_var.set(CATEGORY_OPTIONS[selected][0])
            type_var.trace("w", update_categories)
            update_categories()

            use_subcat_var = tk.BooleanVar()
            subcat_var = tk.StringVar()
            tk.Checkbutton(form_frame, text="เพิ่มหมวดย่อย", variable=use_subcat_var,
                           font=("TH Sarabun New", 16),
                           command=lambda: subcat_entry.grid() if use_subcat_var.get() else subcat_entry.grid_remove()
            ).grid(row=2, column=0, sticky="w")

            subcat_entry = tk.Entry(form_frame, textvariable=subcat_var, font=("TH Sarabun New", 16))
            subcat_entry.grid(row=2, column=1, sticky="w")
            subcat_entry.grid_remove()

            tk.Label(form_frame, text="รายละเอียดและจำนวนเงิน:", font=("TH Sarabun New", 16)).grid(row=3, column=0, sticky="w")
            details_frame = tk.Frame(form_frame)
            details_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="w")

            detail_entries = []
            def add_detail_row():
                row = tk.Frame(details_frame)
                row.pack(pady=2, anchor="w")
                d_var = tk.StringVar()
                a_var = tk.StringVar()
                tk.Entry(row, textvariable=d_var, font=("TH Sarabun New", 16), width=30).pack(side="left", padx=5)
                tk.Entry(row, textvariable=a_var, font=("TH Sarabun New", 16), width=10).pack(side="left", padx=5)
                detail_entries.append((d_var, a_var))

            add_detail_row()
            tk.Button(form_frame, text="+ เพิ่มแถว", font=("TH Sarabun New", 14), command=add_detail_row).grid(row=5, column=0, columnspan=2)

            def confirm_add():
                valid_rows = []
                for d_var, a_var in detail_entries:
                    desc = d_var.get().strip()
                    try:
                        amt = float(a_var.get())
                        if desc:
                            valid_rows.append((desc, amt))
                    except:
                        continue

                if not valid_rows:
                    messagebox.showwarning("เตือน", "กรุณากรอกรายละเอียดและจำนวนเงิน")
                    return

                category = cat_var.get()
                if use_subcat_var.get() and subcat_var.get().strip():
                    category += f" > {subcat_var.get().strip()}"

                for desc, amt in valid_rows:
                    data.append([type_var.get(), category, desc, amt])
                refresh_table()
                top.destroy()

            tk.Button(top, text="เพิ่มทั้งหมด", command=confirm_add, font=("TH Sarabun New", 16)).pack(pady=10)

        def save_changes_to_file():
            path = os.path.join(REPORT_DIR, report_file)
            save_to_csv(report_file.replace(".csv", ""), data)
            messagebox.showinfo("สำเร็จ", f"บันทึกเรียบร้อยที่ {path}")
            win.destroy()

        win = tk.Toplevel(root)
        win.title(f"แก้ไข: {report_file}")
        win.geometry("800x550")

        search_var = tk.StringVar()
        tk.Entry(win, textvariable=search_var, font=("TH Sarabun New", 16)).pack(fill="x", padx=10)
        search_var.trace("w", lambda *args: refresh_table())

        style = ttk.Style()
        style.configure("Treeview", font=("TH Sarabun New", 16), rowheight=28)
        style.configure("Treeview.Heading", font=("TH Sarabun New", 16, "bold"))

        tree = ttk.Treeview(win, columns=("ประเภท", "หมวดหมู่", "รายละเอียด", "จำนวนเงิน"), show="headings")
        for col in ("ประเภท", "หมวดหมู่", "รายละเอียด", "จำนวนเงิน"):
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(expand=True, fill="both", padx=10, pady=10)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="เพิ่มรายการใหม่", command=add_new_entry, font=("TH Sarabun New", 16)).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="ลบรายการที่เลือก", command=delete_selected, font=("TH Sarabun New", 16)).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="แก้ไขรายการที่เลือก", command=update_selected, font=("TH Sarabun New", 16)).grid(row=0, column=2, padx=5)
        tk.Button(win, text="บันทึกการเปลี่ยนแปลง", command=save_changes_to_file, font=("TH Sarabun New", 16)).pack(pady=10)

        load_selected_report()

    selector = tk.Toplevel(root)
    selector.title("เลือกไฟล์รายงานที่จะแก้ไข")
    selector.geometry("400x550")

    tk.Label(selector, text="รายงานทั้งหมด", font=("TH Sarabun New", 16, "bold")).pack(pady=5)

    frame = tk.Frame(selector)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(frame, font=("TH Sarabun New", 16), yscrollcommand=scrollbar.set, height=12)
    for r in reports:
        listbox.insert(tk.END, r)
    listbox.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=listbox.yview)

    def on_select():
        selected = listbox.curselection()
        if not selected:
            return
        selector.destroy()
        open_report_editor(reports[selected[0]])

    tk.Button(selector, text="ตกลง", command=on_select, font=("TH Sarabun New", 16)).pack(pady=10)



# ===== เมนูหลัก =====
def main_menu():
    tk.Label(root, text="ระบบจัดการรายงานรายรับรายจ่าย", font=("TH Sarabun New", 20, "bold")).pack(pady=20)
    tk.Button(root, text="1) สร้างรายงานใหม่", font=("TH Sarabun New", 14, "bold"), width=35, height=2, command=create_report_ui).pack(pady=5)
    tk.Button(root, text="2) ดูรายงาน และแปลงเป็น PDF", font=("TH Sarabun New", 14, "bold"), width=35, height=2, command=view_report_ui).pack(pady=5)
    tk.Button(root, text="3) แก้ไข/ลบ รายการ", font=("TH Sarabun New", 14, "bold"), width=35, height=2, command=edit_report_ui).pack(pady=5)
    tk.Button(root, text="4) ออกจากโปรแกรม", font=("TH Sarabun New", 14, "bold"), width=35, height=2, command=root.quit).pack(pady=20)


main_menu()
root.mainloop()
