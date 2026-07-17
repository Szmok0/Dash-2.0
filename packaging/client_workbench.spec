# -*- mode: python ; coding: utf-8 -*-
"""Specyfikacja PyInstaller dla Client Workbench.

Budowanie (Windows):  pyinstaller packaging/client_workbench.spec
Wynik: dist/ClientWorkbench/ClientWorkbench.exe (onedir).
"""
import os
from pathlib import Path

ROOT = Path(os.getcwd())
SRC = ROOT / "src"

datas = [
    (str(SRC / "database" / "schema.sql"), "database"),
    (str(ROOT / "resources" / "fonts"), "resources/fonts"),
    (str(ROOT / "resources" / "app_icon.png"), "resources"),
    (str(ROOT / "resources" / "app_icon.ico"), "resources"),
]

hiddenimports = [
    "openpyxl", "reportlab", "reportlab.graphics.barcode",
    "PySide6.QtPrintSupport",
]

a = Analysis(
    [str(SRC / "app.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy.testing", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ClientWorkbench",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # aplikacja okienkowa, bez konsoli
    icon=str(ROOT / "resources" / "app_icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ClientWorkbench",
)
