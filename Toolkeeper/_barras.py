# SPDX-License-Identifier: GPL-3.0-or-later
"""Barras de herramientas reales (QToolBar): la barra «Toolkeeper»
y las barras personalizadas del gestor maestro, hechas con cualquier comando."""
from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QToolBar

from ._catalogo import PREFIJO, vivo
from ._datos import SEPARADOR
from ._i18n import AJUSTES, _t

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

ESPERA_MS = 1500        # tras el arranque (IngeTrazo restaura entonces las barras)
PREFIJO_BARRA = PREFIJO + "_tb_"

_dueno: QObject | None = None


def dueno() -> QObject:
    """Las acciones «espejo» cuelgan de este objeto, que no es hijo de la
    ventana: así no salen en F3 ni en el editor de atajos de IngeTrazo."""
    global _dueno
    if _dueno is None:
        _dueno = QObject()
        _dueno.setObjectName(PREFIJO + "_espejos")
    return _dueno


def tamano_icono() -> int:
    try:
        from views.icons import toolbar_icon_px
        return int(toolbar_icon_px())
    except Exception:  # noqa: BLE001
        return 24


def _colocar_primera_vez(win, tb, al_crear: bool) -> None:
    """La primera vez, IngeTrazo restaura sus barras después de los plugins y
    deja oculta la que no conoce: se coloca arriba y se muestra."""
    ajustes = QSettings("IngeTrazo", AJUSTES)
    clave = f"colocada/{tb.objectName()}"
    if str(ajustes.value(clave, "")).lower() in ("1", "true"):
        return

    def colocar() -> None:
        if not vivo(tb):
            return
        try:
            if not al_crear:
                win.removeToolBar(tb)
                win.addToolBar(Qt.TopToolBarArea, tb)
            tb.show()
            ajustes.setValue(clave, True)
        except Exception:  # noqa: BLE001
            log.exception("no se pudo colocar la barra %s", tb.objectName())

    if al_crear:
        colocar()
    else:
        QTimer.singleShot(ESPERA_MS, colocar)


def crear_barra(app, nombre_obj: str, titulo: str, al_crear: bool = False) -> QToolBar:
    win = app.window
    tb = win.findChild(QToolBar, nombre_obj)
    if tb is not None:
        tb.setWindowTitle(titulo)
        return tb
    nueva = getattr(win, "_new_toolbar", None)            # interno de 0.5.8
    if callable(nueva):
        try:
            tb = nueva(titulo, nombre_obj)
        except Exception:  # noqa: BLE001
            log.exception("_new_toolbar falló; barra propia")
            tb = None
    if tb is None:
        tb = QToolBar(titulo, win)
        tb.setObjectName(nombre_obj)
        tb.setMovable(True)
        tb.setFloatable(True)
        tb.setAllowedAreas(Qt.AllToolBarAreas)
        px = tamano_icono()
        tb.setIconSize(QSize(px, px))
        tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        win.addToolBar(Qt.TopToolBarArea, tb)
    _colocar_primera_vez(win, tb, al_crear)
    return tb


def quitar_barra(app, tb: QToolBar) -> None:
    if not vivo(tb):
        return
    vaciar(tb)
    app.window.removeToolBar(tb)
    tb.deleteLater()
    QSettings("IngeTrazo", AJUSTES).remove(f"colocada/{tb.objectName()}")


def espejo(icono, texto: str, consejo: str, al_pulsar) -> QAction:
    act = QAction(icono, texto, dueno())
    act.setObjectName(PREFIJO + "_espejo")
    act.setToolTip(consejo or texto)
    act.triggered.connect(lambda _c=False: QTimer.singleShot(0, al_pulsar))
    return act


def boton_para(maestro, key: str) -> tuple[QAction, bool]:
    """La acción que se pone en una barra para el comando ``key``: la propia
    de IngeTrazo si tiene icono (comparte marcado, activado y atajo), o un
    espejo. Devuelve (acción, es_espejo)."""
    c = maestro.catalogo.comando(key)
    if c is None:
        nombre = maestro.nombre(key)
        falta = espejo(maestro.icono(key), nombre, nombre, lambda: None)
        falta.setEnabled(False)
        return falta, True
    if c.run is None and vivo(c.accion) and not c.accion.icon().isNull():
        return c.accion, False
    e = espejo(maestro.icono(key), c.nombre, c.tooltip(), lambda k=key: maestro.ejecutar(k))
    if c.run is None and vivo(c.accion):
        e.setEnabled(c.accion.isEnabled())
    return e, True


def vaciar(tb, espejos: list | None = None) -> None:
    for act in list(tb.actions()):
        tb.removeAction(act)
        if act.parent() is tb and act.isSeparator():
            act.deleteLater()
    borrar_espejos(espejos)


def borrar_espejos(espejos: list | None) -> None:
    for e in espejos or []:
        if vivo(e):
            e.deleteLater()
    if espejos is not None:
        espejos.clear()


def menu_en_boton(tb: QToolBar, act: QAction, construir) -> None:
    """Menú contextual propio en el botón de ``act`` dentro de ``tb``."""
    w = tb.widgetForAction(act)
    if w is None:
        return
    w.setContextMenuPolicy(Qt.CustomContextMenu)

    def mostrar(pos) -> None:
        menu = QMenu(w)
        menu.setObjectName(PREFIJO + "_menu_boton")
        construir(menu)
        if not menu.isEmpty():
            menu.exec(w.mapToGlobal(pos))

    w.customContextMenuRequested.connect(mostrar)


class BarrasPersonalizadas:
    """Las «Custom toolbars» del gestor maestro: QToolBar reales."""

    def __init__(self, maestro) -> None:
        self.m = maestro
        self._espejos: dict = {}

    def nombre_obj(self, bid: str) -> str:
        return PREFIJO_BARRA + bid

    def construir_todas(self) -> None:
        ids = {b["id"] for b in self.m.almacen.barras}
        for tb in list(self.m.app.window.findChildren(QToolBar)):
            obj = tb.objectName()
            if obj.startswith(PREFIJO_BARRA) and obj[len(PREFIJO_BARRA):] not in ids:
                quitar_barra(self.m.app, tb)
        for b in self.m.almacen.barras:
            try:
                self.construir(b, al_crear=False)
            except Exception:  # noqa: BLE001
                log.exception("barra personalizada %r no construida", b.get("nombre"))

    def construir(self, b: dict, al_crear: bool = True) -> QToolBar:
        bid, m = b["id"], self.m
        tb = crear_barra(m.app, self.nombre_obj(bid), b["nombre"], al_crear)
        espejos = self._espejos.setdefault(bid, [])
        vaciar(tb, espejos)
        for key in b["items"]:
            if key == SEPARADOR:
                tb.addSeparator()
                continue
            act, es_espejo = boton_para(m, key)
            if act in tb.actions():
                continue
            tb.addAction(act)
            if es_espejo:
                espejos.append(act)
            menu_en_boton(tb, act, lambda menu, k=key: self.menu_item(menu, bid, k))
        if not b["items"]:
            vacio = QAction(_t("(empty — drag icons here from the Master Toolbar Manager)"), dueno())
            vacio.setEnabled(False)
            tb.addAction(vacio)
            espejos.append(vacio)
        if not getattr(tb, "_maestro_vis", False):
            tb._maestro_vis = True
            tb.visibilityChanged.connect(lambda v, i=bid: self._visible_cambiada(i, v))
        tb.setAcceptDrops(True)
        if not getattr(tb, "_maestro_drop", False):
            from ._boton import instalar_drop_en_barra
            instalar_drop_en_barra(self.m, tb, bid)
            tb._maestro_drop = True
        if al_crear:
            tb.setVisible(bool(b.get("visible", True)))
        return tb

    def _visible_cambiada(self, bid, visible: bool) -> None:
        b = self.m.almacen.barra(bid)
        if b is not None and b.get("visible") != visible and not self.m.saliendo:
            b["visible"] = visible
            self.m.almacen.guardar_pronto()

    def barra_qt(self, bid: str) -> QToolBar | None:
        tb = self.m.app.window.findChild(QToolBar, self.nombre_obj(bid))
        return tb if vivo(tb) else None

    def visible(self, bid: str) -> bool:
        tb = self.barra_qt(bid)
        return bool(tb is not None and tb.isVisible())

    # -- cambios
    def nueva(self, nombre: str, items=None) -> dict:
        from ._datos import nueva_barra
        b = nueva_barra(nombre)
        b["items"] = list(items or [])
        self.m.almacen.barras.append(b)
        self.m.almacen.guardar()
        self.construir(b)
        return b

    def renombrar(self, bid: str, nombre: str) -> None:
        b = self.m.almacen.barra(bid)
        if b is not None and nombre.strip():
            b["nombre"] = nombre.strip()
            self.m.almacen.guardar()
            self.construir(b)

    def borrar(self, bid: str) -> None:
        tb = self.barra_qt(bid)
        if tb is not None:
            vaciar(tb, self._espejos.pop(bid, []))
            quitar_barra(self.m.app, tb)
        self.m.almacen.datos["barras"] = [b for b in self.m.almacen.barras if b["id"] != bid]
        self.m.almacen.guardar()

    def anadir_item(self, bid: str, key: str, indice: int | None = None) -> None:
        b = self.m.almacen.barra(bid)
        if b is None:
            return
        if key != SEPARADOR and key in b["items"]:
            b["items"].remove(key)
        if indice is None or indice >= len(b["items"]):
            b["items"].append(key)
        else:
            b["items"].insert(max(0, indice), key)
        self.m.almacen.guardar()
        self.construir(b)
        self.m.barras_cambiadas()
        self.m.app.viewport.flash_status(_t("Added to «{name}».", name=b["nombre"]), 2500)

    def quitar_item(self, bid: str, indice: int) -> None:
        b = self.m.almacen.barra(bid)
        if b is not None and 0 <= indice < len(b["items"]):
            del b["items"][indice]
            self.m.almacen.guardar()
            self.construir(b)
            self.m.barras_cambiadas()

    def mostrar(self, bid: str, visible: bool) -> None:
        b = self.m.almacen.barra(bid)
        if b is None:
            return
        b["visible"] = visible
        self.m.almacen.guardar()
        tb = self.barra_qt(bid) or self.construir(b)
        tb.setVisible(visible)

    # -- menú contextual de un botón
    def menu_item(self, menu: QMenu, bid: str, key: str) -> None:
        b = self.m.almacen.barra(bid)
        if b is None:
            return
        nombre = self.m.nombre(key)
        menu.addAction(_t("Run"), lambda: self.m.ejecutar(key))
        menu.addAction(_t("Remove command icon: {name}", name=nombre),
                       lambda: self._quitar_key(bid, key))
        menu.addSeparator()
        menu.addAction(_t("Insert Separator before Command [{name}]", name=nombre),
                       lambda: self._separador(bid, key, 0))
        menu.addAction(_t("Insert Separator after Command [{name}]", name=nombre),
                       lambda: self._separador(bid, key, 1))
        menu.addSeparator()
        menu.addAction(_t("Rename the custom toolbar…"), lambda: self.m.renombrar_barra_dialogo(bid))
        menu.addAction(_t("Delete the custom toolbar"), lambda: self.m.borrar_barra_dialogo(bid))
        menu.addSeparator()
        menu.addAction(_t("Hide the toolbar"), lambda: self.mostrar(bid, False))

    def _quitar_key(self, bid, key) -> None:
        b = self.m.almacen.barra(bid)
        if b is not None and key in b["items"]:
            self.quitar_item(bid, b["items"].index(key))

    def _separador(self, bid, key, despues: int) -> None:
        b = self.m.almacen.barra(bid)
        if b is not None and key in b["items"]:
            b["items"].insert(b["items"].index(key) + despues, SEPARADOR)
            self.m.almacen.guardar()
            self.construir(b)
            self.m.barras_cambiadas()
