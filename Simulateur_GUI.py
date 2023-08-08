import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt


class DragDropWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')

        self.text_edit = QLineEdit(self)
        self.text_edit.setAcceptDrops(True)

        self.button = QPushButton('Select File', self)
        self.button.clicked.connect(self.chooseFile)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasText():
            self.text_edit.setText(mime_data.text())

    def chooseFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier", "", "Tous les fichiers (*)", options=options)
        if file_path:
            self.text_edit.setText(file_path)


def main():
    app = QApplication(sys.argv)
    window = DragDropWidget()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
