# SPDX-License-Identifier: GPL-3.0-or-later
"""Estados de las barras: la colocación de todas las barras y paneles de la
ventana (dónde está cada uno y si está visible), guardada con un nombre para
recuperarla después. Va en el JSON de datos, con ``QMainWindow.saveState``:
Qt reconoce cada barra y panel por su objectName, y los que falten al
recuperar (una extensión desinstalada) simplemente se ignoran."""
from __future__ import annotations

import base64
import binascii
import logging

from PySide6.QtCore import QByteArray, QTimer
from PySide6.QtWidgets import QDockWidget, QMenu, QMessageBox, QToolBar

from ._i18n import _t
from ._voz import pedir_texto

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

VERSION = 1                 # la de saveState / restoreState


class Estados:
    def __init__(self, maestro) -> None:
        self.m = maestro

    @property
    def _win(self):
        return self.m.app.window

    def menu(self, menu: QMenu) -> None:
        """Guardar, la lista de estados guardados, Sobrescribir y Borrar."""
        menu.clear()
        menu.addAction(_t("Save the current state…"), self.guardar_actual)
        estados = self.m.almacen.estados
        if not estados:
            menu.addAction(_t("(no saved states yet)")).setEnabled(False)
            return
        menu.addSeparator()
        for e in estados:
            menu.addAction(self._rotulo(e), lambda *_a, n=e["nombre"]: self.aplicar(n))
        menu.addSeparator()
        for titulo, accion in ((_t("Overwrite"), self.sobrescribir), (_t("Delete"), self.borrar)):
            sub = menu.addMenu(titulo)
            for e in estados:
                sub.addAction(self._rotulo(e), lambda *_a, n=e["nombre"], f=accion: f(n))

    @staticmethod
    def _rotulo(estado: dict) -> str:
        return estado["nombre"].replace("&", "&&")   # que no se lea como tecla de acceso

    def _si(self, texto: str) -> bool:
        return QMessageBox.question(self._win, _t("Toolbar states"), texto) == QMessageBox.Yes

    # -- guardar
    def guardar_actual(self) -> None:
        almacen = self.m.almacen
        nombre, ok = pedir_texto(self._win, _t("Toolbar states"), _t("Name of the state"),
                                 _t("State {n}", n=len(almacen.estados) + 1))
        if not ok or not nombre:
            return
        previo = almacen.estado(nombre)
        if previo is not None and not self._si(_t("A state named «{name}» already exists. Overwrite it?",
                                                  name=previo["nombre"])):
            return
        self._guardar(nombre)

    def sobrescribir(self, nombre: str) -> None:
        if self._si(_t("A state named «{name}» already exists. Overwrite it?", name=nombre)):
            self._guardar(nombre)

    def _sin_nombre(self) -> list:
        """Barras y paneles que Qt no puede recordar: no tienen objectName."""
        win = self._win
        return [w.windowTitle() or "?" for w in (*win.findChildren(QDockWidget), *win.findChildren(QToolBar))
                if w.parent() is win and not w.objectName()]

    def _guardar(self, nombre: str) -> None:
        datos = base64.b64encode(bytes(self._win.saveState(VERSION))).decode("ascii")
        self.m.almacen.poner_estado(nombre, datos)
        aviso = _t("State «{name}» saved.", name=nombre)
        sueltos = self._sin_nombre()
        if sueltos:
            aviso += " " + _t("Not included: {names}", names=", ".join(sueltos))
        self.m.app.viewport.flash_status(aviso, 6000 if sueltos else 3000)

    # -- recuperar y borrar
    def aplicar(self, nombre: str) -> None:
        # Después, para no recolocar la ventana mientras se cierra el menú.
        QTimer.singleShot(0, lambda: self._aplicar(nombre))

    def _aplicar(self, nombre: str) -> None:
        estado = self.m.almacen.estado(nombre)
        if estado is None:
            return
        try:
            crudo = base64.b64decode(estado["qt"], validate=True)
            hecho = bool(self._win.restoreState(QByteArray(crudo), VERSION))
        except (binascii.Error, ValueError):
            log.exception("estado de las barras ilegible: %s", nombre)
            hecho = False
        if hecho:
            self.m.barras_cambiadas()           # las casillas del lateral
            aviso = _t("State «{name}» restored.", name=nombre)
        else:
            aviso = _t("The state «{name}» could not be restored.", name=nombre)
        self.m.app.viewport.flash_status(aviso, 3000)

    def borrar(self, nombre: str) -> None:
        if self._si(_t("Delete the state «{name}»?", name=nombre)):
            self.m.almacen.borrar_estado(nombre)
