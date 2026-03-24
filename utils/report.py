from PyQt5.QtWidgets import QFileDialog, QMessageBox
from datetime import datetime

def save_table(table, parent=None):
    path = QFileDialog.getSaveFileName(parent, "Сохранить отчёт", "Отчет.txt", "Text files (*.txt);;All Files (*)")[0]
    if not path:
        return None
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"Отчёт службы доставки\nДата формирования: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            headers = []
            for col in range(table.columnCount()):
                headers.append(table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else "")
            f.write("\t".join(headers) + "\n")
            
            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                f.write("\t".join(row_data) + "\n")
    except Exception as e:
        QMessageBox.critical(parent or None, "Ошибка", f"Не удалось сохранить файл:\n{e}")
        return None
    QMessageBox.information(parent or None, "", "Файл сохранен успешно")
    return path