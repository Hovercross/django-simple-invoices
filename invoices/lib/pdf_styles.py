#!/usr/bin/python

import os
from copy import copy

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_RIGHT

font_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")

for font_file in os.listdir(font_folder):
    font_name, extension = os.path.splitext(font_file)
    if (extension) == ".ttf":
        pdfmetrics.registerFont(TTFont(font_name, os.path.join(font_folder, font_file)))


styles = getSampleStyleSheet()

accent_color = colors.Color(red=0.325, green=0.484, blue=0.612)

normal_style = copy(styles["Normal"])

table_name_style = copy(styles["Normal"])
table_name_style.fontSize = 16
table_name_style.fontName = "HelveticaNeue-Light"
table_name_style.textColor = accent_color
table_name_style.leftIndent = -6
table_name_style.leading = 22

table_header_style = copy(styles["Normal"])
table_header_style.fontSize = 10
table_header_style.fontName = "HelveticaNeue-Bold"
table_header_style.textColor = colors.white
# tableHeaderStyle.fontSize = 14

table_header_style_right = copy(table_header_style)
table_header_style_right.alignment = TA_RIGHT

table_item_style = copy(styles["Normal"])
table_item_style_right = copy(table_item_style)
table_item_style_right.alignment = TA_RIGHT

table_total_style = copy(table_item_style)
table_total_style.alignment = TA_RIGHT

invoice_sub_total_style = copy(table_item_style)
invoice_sub_total_style.alignment = TA_RIGHT
invoice_sub_total_style.fontName = "HelveticaNeue-Light"
invoice_sub_total_style.fontSize = 10

invoice_total_style = copy(invoice_sub_total_style)
invoice_total_style.fontName = "HelveticaNeue-Bold"

default_table_style = [
    ("BACKGROUND", (0, 0), (-1, 0), accent_color),
    ("LINEBEFORE", (1, 0), (-1, 0), 1, colors.white),
    ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
    ("LINEABOVE", (0, 0), (-1, -2), 0.25, colors.grey),
    ("SPAN", (0, -1), (-2, -1)),
]

line_item_date_format = "%Y-%m-%d"
