"""Application QSS themes."""
from __future__ import annotations

DARK_QSS = """
* { box-sizing: border-box; }
QMainWindow, QWidget { background: #171C26; color: #F2F4F7; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
#Sidebar { background: #121722; border-right: 1px solid #2B3245; }
#TopBar { background: #171C26; border-bottom: 1px solid #2B3245; }
#Panel, #Card, #Module { background: #1D2330; border: 1px solid #2B3245; border-radius: 10px; }
#TableWrap { background: #202737; border: 1px solid #2B3245; border-radius: 10px; }
QLabel#ScreenTitle { font-size: 26px; font-weight: 700; }
QLabel#SectionTitle { font-size: 16px; font-weight: 700; }
QLabel#Muted, QLabel[muted="true"] { color: #A4ACB8; font-size: 12px; }
QPushButton { background: #202737; border: 1px solid #2B3245; border-radius: 8px; padding: 8px 12px; color: #F2F4F7; text-align: left; }
QPushButton:hover { border-color: #4C8DFF; }
QPushButton[primary="true"] { background: #4C8DFF; border-color: #4C8DFF; color: white; font-weight: 600; text-align: center; }
QPushButton[nav="true"] { border: 0; border-radius: 8px; background: transparent; padding: 10px 14px; font-size: 14px; }
QPushButton[nav="true"]:checked { background: #202737; color: #4C8DFF; }
QLineEdit { background: #202737; border: 1px solid #2B3245; border-radius: 8px; padding: 8px 12px; min-height: 38px; color: #F2F4F7; }
QTableWidget { background: #202737; gridline-color: #2B3245; border: 0; selection-background-color: #26334F; }
QHeaderView::section { background: #1D2330; color: #A4ACB8; border: 0; border-bottom: 1px solid #2B3245; padding: 9px 8px; font-weight: 600; }
QTableWidget::item { border-bottom: 1px solid #2B3245; padding: 7px 8px; }
QFrame#StatusPill { border-radius: 9px; padding: 3px 8px; }
QScrollArea { border: 0; background: transparent; }
"""
