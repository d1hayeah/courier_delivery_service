from PyQt5.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime
import os
import reportlab
from reportlab.lib.pagesizes import A4

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def save_table(table, parent=None):
    font_path = 'C:/Windows/Fonts/Arial.ttf'  
        
    font_name = 'CyrillicFont'
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    path = QFileDialog.getSaveFileName(parent, "Сохранить отчёт", "Отчет.pdf", "PDF files (*.pdf);;All Files (*)")[0]
    if not path:
        return None
    try:
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 40
        c.setFont(font_name, 14)
        c.drawString(40, y, "Отчёт службы доставки")
        y -= 20
        c.setFont(font_name, 10)
        c.drawString(40, y, f"Дата формирования: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 30
        headers = []
        for col in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else "")
        c.setFont(font_name, 10)
        c.drawString(40, y, " | ".join(headers))
        y -= 18
        c.setFont(font_name, 10)
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            c.drawString(40, y, " | ".join(row_data))
            y -= 15
            if y < 40:
                c.showPage()
                y = height - 40
        c.save()
    except Exception as e:
        QMessageBox.critical(parent or None, "Ошибка", f"Не удалось сохранить PDF-файл:\n{e}")
        return None
    QMessageBox.information(parent or None, "", "PDF-файл сохранён успешно")
    return path
