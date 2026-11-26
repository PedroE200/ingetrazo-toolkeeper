# SPDX-License-Identifier: GPL-3.0-or-later
"""Los parámetros de Toolkeeper: solo sus valores de serie (no hay
diálogo para cambiarlos) y la impresión de tablas en HTML."""
from __future__ import annotations

from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QMessageBox

from ._i18n import _t

DEFECTOS = {
    "cerrar_master_al_ejecutar": True,      # el gestor de barras se cierra al ejecutar un comando
    "backup_auto": "sesion",                # copia automática: «sesion», «dia» o «no»
    "backup_purga_dias": 30,                # las copias se borran solas pasados N días
    "nombre_barra": "Toolkeeper",
    "iconos_barra": ["master"],
}


def imprimir_html(padre, html: str) -> None:
    try:
        from PySide6.QtPrintSupport import QPrintDialog, QPrinter
    except ImportError:
        QMessageBox.information(padre, _t("Print"), _t("Printing is not available in this IngeTrazo build."))
        return
    impresora = QPrinter(QPrinter.HighResolution)
    dlg = QPrintDialog(impresora, padre)
    if dlg.exec():
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(impresora)
