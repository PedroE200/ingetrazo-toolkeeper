# SPDX-License-Identifier: GPL-3.0-or-later
"""Comandos personales: una carpeta, un enlace web, una entrada de menú de
IngeTrazo, un script de Python o un acceso directo a un archivo, con nombre,
descripción, atajo, color e icono propios. Se ponen en barras
personalizadas como cualquier otro comando (clave ``personal:<id>``)."""
from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox, QColorDialog, QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout,
    QKeySequenceEdit, QLabel, QLineEdit, QMessageBox, QPushButton, QToolButton, QWidget,
)

from . import _iconos
from ._catalogo import PREFIJO, Comando
from ._datos import PERSONAL, nuevo_personal
from ._i18n import _t

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

# En el orden del menú «Nuevo…» y del lateral. «documento» es el acceso
# directo (la clave se queda así para que los ya creados sigan valiendo).
TIPOS = ("carpeta", "web", "menu", "script", "documento")


def etiqueta_tipo(tipo: str) -> str:
    return {"documento": _t("File shortcut"), "carpeta": _t("Folder"), "web": _t("Web Link"),
            "menu": _t("Menu"), "script": _t("Python script")}.get(tipo, tipo)


class Personales:
    def __init__(self, maestro) -> None:
        self.m = maestro
        self._iconos: dict = {}

    def key(self, c: dict) -> str:
        return PERSONAL + c["id"]

    def de_key(self, key: str) -> dict | None:
        if not key.startswith(PERSONAL):
            return None
        return self.m.almacen.personal(key[len(PERSONAL):])

    def comando(self, key: str) -> Comando | None:
        c = self.de_key(key)
        if c is None:
            return None
        return Comando(key, c["nombre"], etiqueta_tipo(c["tipo"]), None, c.get("atajo", ""),
                       _t("Personal"), c.get("descripcion") or c.get("destino", ""),
                       run=lambda c=c: self.ejecutar(c))

    def icono(self, c: dict) -> QIcon:
        firma = (c["id"], c.get("icono", ""), c.get("color", ""), c["tipo"])
        icono = self._iconos.get(firma)
        if icono is None:
            ruta = c.get("icono") or ""
            icono = QIcon(ruta) if ruta and Path(ruta).is_file() else QIcon()
            if icono.isNull():
                icono = _iconos.tipo_personal(c["tipo"], self.m.tinta())
            icono = _iconos.con_color(icono, c.get("color") or "")
            self._iconos[firma] = icono
        return icono

    def ejecutar(self, c: dict) -> None:
        tipo, destino = c["tipo"], (c.get("destino") or "").strip()
        try:
            if tipo == "documento":
                if not Path(destino).exists():
                    raise FileNotFoundError(destino)
                QDesktopServices.openUrl(QUrl.fromLocalFile(destino))
            elif tipo == "carpeta":
                if not Path(destino).is_dir():
                    raise FileNotFoundError(destino)
                if sys.platform == "win32":
                    subprocess.Popen(["explorer", destino])
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(destino))
            elif tipo == "web":
                url = destino if "://" in destino or destino.startswith("mailto:") else "https://" + destino
                QDesktopServices.openUrl(QUrl(url))
            elif tipo == "menu":
                cmd = self.m.catalogo.comando(destino)
                if cmd is None or not cmd.disponible():
                    raise RuntimeError(_t("«{name}» is not available now.", name=destino))
                cmd.accion.trigger()
            elif tipo == "script":
                self._script(destino)
        except Exception as err:  # noqa: BLE001
            log.exception("comando personal %r", c.get("nombre"))
            self.m.app.viewport.flash_status(_t("{name}: {err}", name=c["nombre"], err=err), 6000)

    def _script(self, ruta: str) -> None:
        p = Path(ruta)
        if not p.is_file():
            raise FileNotFoundError(ruta)
        codigo = p.read_text(encoding="utf-8")
        app = self.m.app
        espacio = {"__name__": "__igz_toolkeeper_script__", "__file__": str(p), "app": app,
                   "window": app.window, "viewport": app.viewport, "scene": app.scene}
        exec(compile(codigo, str(p), "exec"), espacio)  # noqa: S102 — el script es del usuario

    # -- atajos
    def instalar_atajos(self) -> None:
        for c in self.m.almacen.personales:
            self._atajo(c)

    def _atajo(self, c: dict) -> None:
        from PySide6.QtGui import QAction
        win = self.m.app.window
        nombre = f"{PREFIJO}.personal.{c['id']}"
        act = win.findChild(QAction, nombre)
        atajo = (c.get("atajo") or "").strip()
        if act is None:
            if not atajo:
                return
            act = QAction(self.icono(c), c["nombre"], win)
            act.setObjectName(nombre)
            act.triggered.connect(lambda _ch=False, c=c: self.ejecutar(c))
            win.addAction(act)
        act.setText(c["nombre"])
        act.setIcon(self.icono(c))
        act.setShortcut(QKeySequence(atajo) if atajo and not self.m.atajo_ocupado(atajo, act) else QKeySequence())

    # -- altas / bajas
    def nuevo(self, c: dict) -> dict:
        self.m.almacen.personales.append(c)
        self.m.almacen.guardar()
        self._atajo(c)
        return c

    def guardar(self, c: dict) -> None:
        self._iconos = {k: v for k, v in self._iconos.items() if k[0] != c["id"]}
        self.m.almacen.guardar()
        self._atajo(c)
        self.m.todo_cambiado()

    def borrar(self, cid: str) -> None:
        from PySide6.QtGui import QAction
        self.m.almacen.datos["personales"] = [c for c in self.m.almacen.personales if c["id"] != cid]
        act = self.m.app.window.findChild(QAction, f"{PREFIJO}.personal.{cid}")
        if act is not None:
            act.deleteLater()
        self.m.almacen.guardar()
        self.m.todo_cambiado()


class DialogoPersonal(QDialog):
    """«New Personal Command [tipo]» / edición."""

    def __init__(self, maestro, tipo: str, datos: dict | None = None) -> None:
        super().__init__(maestro.app.window)
        self.m = maestro
        self.setObjectName(PREFIJO + "_dlg_personal")
        self.datos = datos or nuevo_personal(tipo, _t("{type} {n}", type=etiqueta_tipo(tipo),
                                                        n=len(maestro.almacen.personales) + 1))
        self.setWindowTitle(_t("New Personal Command [{type}]", type=etiqueta_tipo(tipo))
                            if datos is None else _t("Personal Command [{type}]", type=etiqueta_tipo(tipo)))
        f = QFormLayout(self)
        self.nombre = QLineEdit(self.datos["nombre"])
        f.addRow(_t("Name"), self.nombre)
        self.descripcion = QLineEdit(self.datos.get("descripcion", ""))
        f.addRow(_t("Description"), self.descripcion)
        self.atajo = QKeySequenceEdit(QKeySequence(self.datos.get("atajo", "")))
        fila = QHBoxLayout()
        fila.addWidget(self.atajo)
        enlace = QLabel(f"<a href='#'>{_t('List of Shortcuts')}</a>")
        enlace.linkActivated.connect(lambda _l: maestro.abrir_atajos())
        fila.addWidget(enlace)
        fila.addStretch(1)
        f.addRow(_t("Shortcut"), fila)
        self.usar_color = QCheckBox()
        self.usar_color.setChecked(bool(self.datos.get("color")))
        self.color = QPushButton(self.datos.get("color") or _t("Choose…"))
        self.color.clicked.connect(self._elegir_color)
        self.color.setEnabled(self.usar_color.isChecked())
        self.usar_color.toggled.connect(self.color.setEnabled)
        fila = QHBoxLayout()
        fila.addWidget(self.usar_color)
        fila.addWidget(self.color)
        fila.addStretch(1)
        f.addRow(_t("Use Color"), fila)
        self.icono = QToolButton()
        self._ruta_icono = self.datos.get("icono", "")
        self._pinta_icono()
        self.icono.setToolTip(_t("Click to choose an image file (PNG/SVG); right-click to use the default icon"))
        self.icono.clicked.connect(self._elegir_icono)
        self.icono.setContextMenuPolicy(Qt.CustomContextMenu)
        self.icono.customContextMenuRequested.connect(lambda _p: self._icono_defecto())
        f.addRow(_t("Icon"), self.icono)
        self.destino: QWidget
        if tipo == "menu":
            self.destino = QComboBox()
            self.destino.setEditable(False)
            actual = self.datos.get("destino", "")
            for c in maestro.catalogo.todos():
                self.destino.addItem(maestro.icono(c.key), f"{c.nombre}   — {c.ruta}" if c.ruta else c.nombre, c.key)
            i = self.destino.findData(actual)
            self.destino.setCurrentIndex(max(0, i))
            f.addRow(etiqueta_tipo(tipo), self.destino)
        else:
            self.destino = QLineEdit(self.datos.get("destino", ""))
            fila = QHBoxLayout()
            fila.addWidget(self.destino, 1)
            if tipo != "web":
                examinar = QToolButton()
                examinar.setText("…")
                examinar.clicked.connect(lambda _c=False, t=tipo: self._examinar(t))
                fila.addWidget(examinar)
            f.addRow(etiqueta_tipo(tipo), fila)
        botones = QHBoxLayout()
        botones.addStretch(1)
        cancelar = QPushButton(_t("Cancel"))
        cancelar.clicked.connect(self.reject)
        botones.addWidget(cancelar)
        crear = QPushButton(_t("Create Personal Command") if datos is None else _t("Save"))
        crear.setDefault(True)
        crear.clicked.connect(self._aceptar)
        botones.addWidget(crear)
        f.addRow(botones)
        self.resize(520, self.sizeHint().height())

    def _pinta_icono(self) -> None:
        tmp = dict(self.datos)
        tmp["icono"] = self._ruta_icono
        tmp["color"] = self.datos.get("color") if self.usar_color.isChecked() else ""
        self.m.personales._iconos.pop((tmp["id"], tmp["icono"], tmp["color"] or "", tmp["tipo"]), None)
        self.icono.setIcon(self.m.personales.icono(tmp))
        self.icono.setIconSize(self.icono.iconSize() * 1)

    def _elegir_color(self) -> None:
        c = QColorDialog.getColor(QColor(self.datos.get("color") or "#ffe4b5"), self, _t("Use Color"))
        if c.isValid():
            self.datos["color"] = c.name()
            self.color.setText(c.name())
            self._pinta_icono()

    def _elegir_icono(self) -> None:
        ruta, _f = QFileDialog.getOpenFileName(self, _t("Icon"), "", "Images (*.png *.svg *.jpg *.ico)")
        if ruta:
            self._ruta_icono = ruta
            self._pinta_icono()

    def _icono_defecto(self) -> None:
        self._ruta_icono = ""
        self._pinta_icono()

    def _examinar(self, tipo: str) -> None:
        if tipo == "carpeta":
            ruta = QFileDialog.getExistingDirectory(self, etiqueta_tipo(tipo), self.destino.text())
        elif tipo == "script":
            ruta, _f = QFileDialog.getOpenFileName(self, etiqueta_tipo(tipo), self.destino.text(), "Python (*.py)")
        else:
            ruta, _f = QFileDialog.getOpenFileName(self, etiqueta_tipo(tipo), self.destino.text())
        if ruta:
            self.destino.setText(ruta)

    def _aceptar(self) -> None:
        nombre = self.nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, self.windowTitle(), _t("You must give a valid name"))
            return
        destino = self.destino.currentData() if isinstance(self.destino, QComboBox) else self.destino.text().strip()
        if not destino:
            QMessageBox.warning(self, self.windowTitle(), _t("You must give a target"))
            return
        self.datos.update(nombre=nombre, descripcion=self.descripcion.text().strip(),
                          atajo=self.atajo.keySequence().toString(),
                          color=self.datos.get("color") if self.usar_color.isChecked() else "",
                          icono=self._ruta_icono, destino=destino)
        self.accept()
