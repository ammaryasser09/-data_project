#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Review workbook for the team's native check of the Egyptian Arabic text.

    python3 06_Scripts/generation/build_review_file.py
    → 05_Evaluation/review/egyptian_review.xlsx

Sheets: Instructions (legend, example, progress), FAQ_Answers (one row per distinct Egyptian
answer with every question that uses it), Conversations (every Egyptian assistant turn with the
guest turn before it), Test_Questions (does each realistic question sound like a real caller?).
Reviewers fill only the yellow columns. Corrections are applied back through
06_Scripts/repair/policy_update_v4_data.py (FAQ) or conv_templates_v4.py (conversations).
"""
import csv, json, os
from collections import OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); os.chdir(ROOT)
def rd(p): return list(csv.DictReader(open(p, encoding='utf-8-sig')))
F = Font(name='Arial', size=11); FB = Font(name='Arial', size=11, bold=True, color='FFFFFF')
HEAD = PatternFill('solid', start_color='1F4E78'); EDIT = PatternFill('solid', start_color='FFF2CC')
WRAP = Alignment(wrap_text=True, vertical='top', horizontal='right', readingOrder=2)
VERDICTS = '"تمام,محتاج تعديل,مش متأكد"'

def sheet(wb, name, headers, widths, rows, edit_cols):
    ws = wb.create_sheet(name); ws.sheet_view.rightToLeft = True; ws.freeze_panes = 'A2'
    ws.append(headers)
    for i, (h, w) in enumerate(zip(headers, widths), 1):
        c = ws.cell(row=1, column=i); c.font, c.fill, c.alignment = FB, HEAD, Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.column_dimensions[c.column_letter].width = w
    for r in rows: ws.append(r)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font, c.alignment = F, WRAP
            if c.column in edit_cols: c.fill = EDIT
    dv = DataValidation(type='list', formula1=VERDICTS, allow_blank=True); ws.add_data_validation(dv)
    vcol = ws.cell(row=1, column=min(edit_cols)).column_letter
    dv.add(f'{vcol}2:{vcol}{ws.max_row}')
    ws.auto_filter.ref = ws.dimensions
    return ws, vcol

g = [r for r in rd('02_Data/04_Gold/hotel_faq_gold.csv') if r['language'] == 'Arabic-Egyptian']
groups = OrderedDict()
for r in g: groups.setdefault(r['answer_egyptian'], []).append(r)
faq_rows = []
for k, (egy, rs) in enumerate(groups.items(), 1):
    faq_rows.append([f'E{k:03d}', (k - 1) % 4 + 1, rs[0]['intent_id'], ', '.join(r['faq_id'] for r in rs),
                     '\n'.join(r['question'] for r in rs), egy, rs[0]['answer'], '', '', '', ''])
conv_rows = []
for c in rd('02_Data/04_Gold/conversations_gold.csv'):
    if c['language'] != 'Arabic-Egyptian': continue
    turns = json.loads(c['conversation_json']); prev = ''
    for i, t in enumerate(turns, 1):
        if t['role'] == 'user': prev = t['message']; continue
        conv_rows.append([c['conversation_id'], c['flow_id'], i, prev, t['message'], '', '', ''])
test_rows = [[r['test_id'], r['category'], r['question'], r['tags'], '', '', ''] for r in rd('05_Evaluation/realistic_test/realistic_test_egyptian.csv')]

wb = Workbook(); ins = wb.active; ins.title = 'Instructions'; ins.sheet_view.rightToLeft = True
ins.column_dimensions['A'].width = 34; ins.column_dimensions['B'].width = 90
lines = [
    ('مراجعة اللهجة المصرية — Nile Pearl Hotel', ''),
    ('الهدف', 'نتأكد إن الكلام المصري طبيعي، صح لغوياً، وبيقول نفس معلومة الإجابة الفصحى بالظبط.'),
    ('تملى إيه', 'الأعمدة الصفرا بس: الحكم (من القايمة)، التصحيح، ملاحظات، اسم المراجع. متعدلش أي عمود تاني.'),
    ('الحكم', 'تمام = الجملة طبيعية وصح. محتاج تعديل = اكتب الجملة الصح في عمود التصحيح. مش متأكد = اكتب السبب في الملاحظات.'),
    ('تقسيم الشغل', 'في شيت FAQ_Answers عمود "الدفعة" من 1 لـ 4، كل واحد ياخد دفعة. المحادثات والأسئلة تتقسم بعدد الصفوف.'),
    ('انتبه لـ', 'الأرقام والأسعار والمواعيد لازم تفضل زي الفصحى بالظبط. لو الإجابة المصري بتقول معلومة مش في الفصحى أو ناقصة حاجة، علّم "محتاج تعديل".'),
    ('مثال', 'السؤال: "الجيم بفلوس؟" | المصري: "الجيم شغال 24 ساعة وببلاش للنزلاء" | الحكم: تمام'),
    ('مثال تعديل', 'المصري: "الاستقبال بيشتغل على مدار الساعة" | الحكم: محتاج تعديل | التصحيح: "الاستقبال شغال 24 ساعة" | ملاحظات: "على مدار الساعة" فصحى'),
    ('', ''),
    ('التقدم', 'تمام / محتاج تعديل / مش متأكد / لسه'),
]
for a, b in lines: ins.append([a, b])
sheets = [('FAQ_Answers', ['رقم', 'الدفعة', 'الـ intent', 'أرقام الأسئلة', 'الأسئلة', 'الإجابة المصري', 'الإجابة الفصحى (مرجع)', 'الحكم', 'التصحيح', 'ملاحظات', 'المراجع'],
           [8, 7, 10, 16, 42, 55, 55, 14, 45, 30, 12], faq_rows, {8, 9, 10, 11}),
          ('Conversations', ['المحادثة', 'الـ flow', 'رقم الدور', 'كلام الضيف قبلها', 'رد الموظف (مصري)', 'الحكم', 'التصحيح', 'ملاحظات'],
           [12, 14, 8, 45, 60, 14, 45, 30], conv_rows, {6, 7, 8}),
          ('Test_Questions', ['رقم', 'النوع', 'السؤال', 'tags', 'الحكم: شكله كلام حقيقي؟', 'صياغة أطبع', 'ملاحظات'],
           [8, 16, 55, 20, 18, 45, 30], test_rows, {5, 6, 7})]
r0 = ins.max_row + 1
for name, h, w, rows, ed in sheets:
    ws, vcol = sheet(wb, name, h, w, rows, ed)
    rng = f"'{name}'!{vcol}2:{vcol}{ws.max_row}"
    ins.append([f'{name} ({len(rows)})', f'=COUNTIF({rng},"تمام")&" / "&COUNTIF({rng},"محتاج تعديل")&" / "&COUNTIF({rng},"مش متأكد")&" / "&COUNTBLANK({rng})'])
for row in ins.iter_rows():
    for c in row: c.font, c.alignment = F, WRAP
ins['A1'].font = Font(name='Arial', size=14, bold=True)
for c in ('A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A10'): ins[c].font = Font(name='Arial', size=11, bold=True)
out = '05_Evaluation/review/egyptian_review.xlsx'; wb.save(out)
print(f'{out}: FAQ answers {len(faq_rows)} | conversation turns {len(conv_rows)} | test questions {len(test_rows)}')
