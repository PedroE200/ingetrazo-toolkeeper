# SPDX-License-Identifier: GPL-3.0-or-later
"""Entrada por voz en las cajas de texto y la ventanita para pedir un texto.

``con_microfono(campo)`` pone un micrófono dentro del campo, a la derecha. Al
pulsarlo, el foco va al campo (al final de lo que haya) y se abre el dictado
del sistema (Win+H), en el sitio que el sistema decida: esa ventanita no se
puede mover y, si se arrastra una vez, el sistema recuerda dónde se dejó.
"""
from __future__ import annotations

import ctypes
import logging
import os

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ._catalogo import PREFIJO
from ._i18n import _t

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

COLOR = "#909090"           # se ve bien tanto en tema claro como oscuro
TRAS_FOCO_MS = 150          # que el foco se asiente antes de pulsar Win+H
VK_LWIN, VK_H, KEYUP = 0x5B, 0x48, 0x0002


def _icono() -> QIcon:
    pm = QPixmap(32, 32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(COLOR), 2.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(QColor(COLOR))
    p.drawRoundedRect(QRectF(11.0, 3.0, 10.0, 17.0), 5.0, 5.0)
    p.setBrush(Qt.NoBrush)
    arco = QPainterPath()
    arco.moveTo(7.0, 14.0)
    arco.cubicTo(7.0, 27.0, 25.0, 27.0, 25.0, 14.0)
    p.drawPath(arco)
    p.drawLine(QPointF(16.0, 24.0), QPointF(16.0, 29.0))
    p.drawLine(QPointF(11.0, 29.0), QPointF(21.0, 29.0))
    p.end()
    return QIcon(pm)


def _win_h() -> None:
    if os.name != "nt":
        return
    for vk, sube in ((VK_LWIN, 0), (VK_H, 0), (VK_H, KEYUP), (VK_LWIN, KEYUP)):
        ctypes.windll.user32.keybd_event(vk, 0, sube, 0)


def _dictar(campo: QLineEdit) -> None:
    try:
        w = campo.window()
        w.activateWindow()
        w.raise_()
        campo.setFocus(Qt.OtherFocusReason)
        campo.end(False)
        QTimer.singleShot(TRAS_FOCO_MS, _win_h)
    except Exception:  # noqa: BLE001 — sin dictado, el campo sigue funcionando
        log.exception("no se pudo abrir el dictado del sistema")


def con_microfono(campo: QLineEdit) -> QLineEdit:
    act = campo.addAction(_icono(), QLineEdit.TrailingPosition)
    act.setToolTip(_t("Dictate by voice"))
    act.triggered.connect(lambda _c=False, c=campo: _dictar(c))
    return campo


def pedir_texto(padre, titulo: str, etiqueta: str, texto: str = "") -> tuple[str, bool]:
    """Pide un texto en una ventanita oscura con micrófono. Devuelve (texto, aceptado)."""
    from ._maestro_dlg import ESTILO        # aquí: ese módulo también usa este
    dlg = QDialog(padre)
    dlg.setObjectName(PREFIJO + "_dlg_texto")
    dlg.setWindowTitle(titulo)
    dlg.setStyleSheet(ESTILO)
    dlg.setMinimumWidth(340)
    lay = QVBoxLayout(dlg)
    lay.addWidget(QLabel(etiqueta))
    campo = con_microfono(QLineEdit(texto))
    campo.selectAll()
    lay.addWidget(campo)
    fila = QHBoxLayout()
    fila.addStretch(1)
    cancelar = QPushButton(_t("Cancel"))
    cancelar.setAutoDefault(False)
    cancelar.clicked.connect(dlg.reject)
    fila.addWidget(cancelar)
    guardar = QPushButton(_t("Save"))
    guardar.setDefault(True)
    guardar.clicked.connect(dlg.accept)
    fila.addWidget(guardar)
    lay.addLayout(fila)
    aceptado = dlg.exec() == QDialog.Accepted
    resultado = campo.text().strip()
    dlg.deleteLater()
    return resultado, aceptado
