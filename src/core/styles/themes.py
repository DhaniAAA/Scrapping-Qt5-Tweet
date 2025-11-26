"""
Theme definitions for the application.
"""

LIGHT_THEME = """
    QWidget {
        font-size: 14px;
        background-color: #ffffff;
        color: #333333;
    }
    QLabel {
        font-weight: bold;
        color: #333333;
    }
    QPushButton#startBtn {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        border: none;
    }
    QPushButton#startBtn:hover {
        background-color: #45a049;
    }
    QPushButton#startBtn:disabled {
        background-color: #A5D6A7;
    }
    QPushButton#stopBtn {
        background-color: #f44336;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        border: none;
    }
    QPushButton#stopBtn:hover {
        background-color: #da190b;
    }
    QPushButton#stopBtn:disabled {
        background-color: #ef9a9a;
    }
    QPushButton#themeBtn {
        background-color: #2196F3;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        border: none;
        font-size: 14px;
    }
    QPushButton#themeBtn:hover {
        background-color: #1976D2;
    }
    QTextEdit, QTableWidget {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        color: #333333;
    }
    QLineEdit, QDateEdit, QSpinBox, QComboBox {
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: #ffffff;
        color: #333333;
        font-size: 13px;
        min-height: 20px;
    }
    QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 2px solid #4CAF50;
    }
    QProgressBar {
        text-align: center;
        border: 1px solid #ccc;
        border-radius: 3px;
        background-color: #f0f0f0;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 2px;
    }
    QGroupBox {
        font-weight: bold;
        border: 2px solid #ccc;
        border-radius: 8px;
        margin-top: 1ex;
        padding-top: 15px;
        margin-bottom: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px 0 8px;
        font-size: 13px;
    }
    QTabWidget::pane {
        border: 1px solid #ccc;
        background-color: #ffffff;
    }
    QTabBar::tab {
        background-color: #f0f0f0;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: 2px solid #4CAF50;
    }
"""

DARK_THEME = """
    QWidget {
        font-size: 14px;
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QLabel {
        font-weight: bold;
        color: #ffffff;
    }
    QPushButton#startBtn {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        border: none;
    }
    QPushButton#startBtn:hover {
        background-color: #45a049;
    }
    QPushButton#startBtn:disabled {
        background-color: #2e5930;
    }
    QPushButton#stopBtn {
        background-color: #f44336;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        border: none;
    }
    QPushButton#stopBtn:hover {
        background-color: #da190b;
    }
    QPushButton#stopBtn:disabled {
        background-color: #5c2e2e;
    }
    QPushButton#themeBtn {
        background-color: #FF9800;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        border: none;
        font-size: 14px;
    }
    QPushButton#themeBtn:hover {
        background-color: #F57C00;
    }
    QTextEdit, QTableWidget {
        background-color: #3c3c3c;
        border: 1px solid #555;
        border-radius: 5px;
        color: #ffffff;
    }
    QLineEdit, QDateEdit, QSpinBox, QComboBox {
        padding: 8px;
        border: 1px solid #555;
        border-radius: 4px;
        background-color: #3c3c3c;
        color: #ffffff;
        font-size: 13px;
        min-height: 20px;
    }
    QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 2px solid #4CAF50;
    }
    QProgressBar {
        text-align: center;
        border: 1px solid #555;
        border-radius: 3px;
        background-color: #3c3c3c;
        color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 2px;
    }
    QGroupBox {
        font-weight: bold;
        border: 2px solid #555;
        border-radius: 8px;
        margin-top: 1ex;
        padding-top: 15px;
        margin-bottom: 10px;
        color: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px 0 8px;
        font-size: 13px;
    }
    QTabWidget::pane {
        border: 1px solid #555;
        background-color: #2b2b2b;
    }
    QTabBar::tab {
        background-color: #3c3c3c;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        color: #ffffff;
    }
    QTabBar::tab:selected {
        background-color: #2b2b2b;
        border-bottom: 2px solid #4CAF50;
    }
"""
