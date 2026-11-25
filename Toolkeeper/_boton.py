# SPDX-License-Identifier: GPL-3.0-or-later
"""El botón de icono del gestor de barras y el arrastre de iconos hacia las
barras personalizadas."""
from __future__ import annotations

import json

from PySide6.QtCore import QEvent, QMimeData, QObject, QPoint, QSize, Qt
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QApplication, QToolBar, QToolButton

from ._catalogo import vivo
from ._i18n import _t

MIME = "application/x-igz-toolkeeper"      # Rosco acepta los arrastres por este tipo


def datos_arrastre(key: str, origen: str, indice: int) -> QMimeData:
    md = QMimeData()
    md.setData(MIME, json.dumps({"key": key, "origen": origen, "indice": indice}).encode("utf-8"))
    md.setText(key)
    return md


def leer_arrastre(md: QMimeData) -> dict | None:
    if not md.hasFormat(MIME):
        return None
    try:
        return json.loads(bytes(md.data(MIME)).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


class BotonComando(QToolButton):
    """Botón de icono: clic ejecuta, arrastrar lo lleva a una barra
    personalizada."""

    def __init__(self, maestro, key: str, origen: str, indice: int, px: int, parent=None) -> None:
        super().__init__(parent)
        self.m, self.key, self.origen, self.indice = maestro, key, origen, indice
        self._inicio = None
        self.setAutoRaise(True)
        self.setIconSize(QSize(px, px))
        self.setFixedSize(px + 8, px + 8)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setCursor(Qt.PointingHandCursor)
        # Fondo del color de los botones del tema: los iconos de IngeTrazo se dibujan
        # para ese fondo (claros en el tema oscuro).
        self.setStyleSheet("QToolButton { background: palette(button); border: 1px solid palette(mid); "
                           "border-radius: 3px; } QToolButton:hover { border: 2px solid #f37329; }"
                           "QToolButton:checked { border: 2px solid #f37329; background: palette(highlight); }")
        self.refrescar()

    def refrescar(self) -> None:
        c = self.m.comando(self.key)
        self.setIcon(self.m.icono(self.key))
        self.setToolTip(c.tooltip() if c is not None else _t("{name}\n(not available)",
                                                              name=self.m.nombre(self.key)))
        self.setEnabled(c is not None and c.disponible())
        act = c.accion if c is not None and c.run is None else None
        self.setCheckable(bool(act is not None and vivo(act) and act.isCheckable()))
        if self.isCheckable():
            self.setChecked(act.isChecked())

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton:
            self._inicio = ev.position().toPoint()
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev) -> None:
        if self._inicio is not None and (ev.buttons() & Qt.LeftButton) and \
                (ev.position().toPoint() - self._inicio).manhattanLength() >= QApplication.startDragDistance():
            self._inicio = None
            self.setDown(False)
            drag = QDrag(self)
            drag.setMimeData(datos_arrastre(self.key, self.origen, self.indice))
            drag.setPixmap(self.icon().pixmap(self.iconSize()))
            drag.setHotSpot(QPoint(self.iconSize().width() // 2, self.iconSize().height() // 2))
            drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
            return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev) -> None:
        if self._inicio is not None and ev.button() == Qt.LeftButton and self.rect().contains(
                ev.position().toPoint()):
            self._inicio = None
            self.setDown(False)
            self.m.ejecutar(self.key, origen=self.origen)
            return
        self._inicio = None
        super().mouseReleaseEvent(ev)


def instalar_drop_en_barra(maestro, tb: QToolBar, bid: str) -> None:
    """Las barras personalizadas aceptan iconos arrastrados."""

    class Filtro(QObject):
        def eventFilter(self, obj, ev) -> bool:
            if ev.type() in (QEvent.DragEnter, QEvent.DragMove):
                if leer_arrastre(ev.mimeData()) is not None:
                    ev.acceptProposedAction()
                    return True
            elif ev.type() == QEvent.Drop:
                info = leer_arrastre(ev.mimeData())
                if info is None:
                    return False
                pos = ev.position().toPoint()
                indice = None
                b = maestro.almacen.barra(bid)
                if b is not None:
                    acciones = [a for a in tb.actions() if not a.isSeparator() and tb.widgetForAction(a)]
                    for n, a in enumerate(acciones):
                        w = tb.widgetForAction(a)
                        if w.geometry().center().x() > pos.x():
                            indice = n
                            break
                maestro.barras.anadir_item(bid, info["key"], indice)
                ev.acceptProposedAction()
                return True
            return False

    f = Filtro(tb)
    tb.installEventFilter(f)
    tb._maestro_filtro = f
