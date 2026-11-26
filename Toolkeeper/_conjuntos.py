# SPDX-License-Identifier: GPL-3.0-or-later
"""Conjuntos de extensiones: qué extensiones están activas y cuáles
desactivadas, guardado con un nombre para volver a ello con un clic.

IngeTrazo solo carga extensiones al arrancar y salta las carpetas que tienen
dentro un archivo ``.disabled`` (lo mismo que hace su propio gestor de
extensiones). Toolkeeper usa esa misma marca, así que vale también para las
extensiones instaladas a mano. Un archivo suelto ``x.py`` se aparta
renombrándolo a ``.x.py.desactivada`` (IngeTrazo no carga nombres con punto
delante) y se recupera al activarlo. Nunca se borra ni se mueve nada más.

Un conjunto puede recordar también dónde están las barras y los paneles; esa
colocación se aplica en el siguiente arranque, cuando ya existen las barras
de las extensiones que se activan.

Los conjuntos van en el JSON de datos (``conjuntos``), con el estado anterior
a la última aplicación (``conjunto_anterior``) para poder volver a él.
"""
from __future__ import annotations

import base64
import binascii
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt, QTimer, QUrl
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QDialog, QFileDialog, QGridLayout,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                               QMainWindow, QMenu, QMessageBox, QPushButton, QToolButton, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from ._catalogo import PREFIJO
from ._datos import carpeta_datos, carpeta_usuario_plugins
from ._i18n import _t
from ._voz import con_microfono

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

MARCA = ".disabled"             # la marca que IngeTrazo mira al arrancar
APARTADA = ".desactivada"       # archivo suelto apartado: «.nombre.py.desactivada»
EXT_CONJUNTOS = ".conjuntos.json"
MODULO = "ingetrazo_plugin_"    # nombre con que IngeTrazo importa cada extensión
PROPIA = Path(__file__).resolve().parent.name
VERSION_QT = 1                  # la de saveState / restoreState (la misma que los estados)

# Colores (tema oscuro del gestor de barras).
VERDE, ROJO, NARANJA, SUAVE = "#97C459", "#f0a19c", "#ffbf86", "#888780"


# ---- las extensiones en disco ---------------------------------------------------

@dataclass
class Ext:
    id: str
    ruta: Path
    tipo: str                   # "paquete" o "archivo"
    activa: bool                # en disco: se cargará al arrancar
    catalogo: bool = False      # instalada por el gestor de IngeTrazo

    @property
    def bloqueada(self) -> bool:
        return self.id == PROPIA

    @property
    def cargada(self) -> bool:
        return (MODULO + self.id) in sys.modules


def listar() -> list[Ext]:
    """Las extensiones de la carpeta del usuario, activas o no. Las que trae
    IngeTrazo de serie no salen: están en una carpeta de solo lectura."""
    raiz = carpeta_usuario_plugins()
    try:
        entradas = sorted(raiz.iterdir(), key=lambda p: p.name.casefold())
    except OSError:
        return []
    exts: dict[str, Ext] = {}
    apartadas: list[Ext] = []
    for e in entradas:
        n = e.name
        try:
            if n.startswith("."):
                if n.endswith(".py" + APARTADA) and os.path.isfile(e):
                    ident = n[1:-len(".py" + APARTADA)]
                    if ident and not ident.startswith(("_", ".")):
                        apartadas.append(Ext(ident, e, "archivo", False))
                continue
            if n.startswith("_"):
                continue
            if os.path.isdir(e):
                if os.path.isfile(e / "__init__.py"):
                    exts[n] = Ext(n, e, "paquete", not os.path.isfile(e / MARCA),
                                  os.path.isfile(e / "extension.json"))
            elif e.suffix == ".py" and os.path.isfile(e):
                exts[e.stem] = Ext(e.stem, e, "archivo", True)
        except OSError:
            continue
    for a in apartadas:                     # si hay una activa con el mismo nombre, gana esa
        exts.setdefault(a.id, a)
    return sorted(exts.values(), key=lambda x: x.id.casefold())


def estado_en_disco(exts: list[Ext] | None = None) -> dict[str, bool]:
    return {x.id: x.activa for x in (listar() if exts is None else exts)}


def poner_activa(ext: Ext, activa: bool) -> None:
    """Escribe en disco si ``ext`` se carga al arrancar. Lanza OSError si no puede."""
    if ext.bloqueada or ext.activa == activa:
        return
    if ext.tipo == "paquete":
        marca = ext.ruta / MARCA
        if activa:
            marca.unlink(missing_ok=True)
        else:
            marca.write_text("", encoding="utf-8")
    else:
        destino = ext.ruta.with_name(f"{ext.id}.py" if activa else f".{ext.id}.py{APARTADA}")
        if destino.exists():
            raise OSError(_t("«{name}» already exists.", name=destino.name))
        ext.ruta.rename(destino)
        ext.ruta = destino
    ext.activa = activa


# ---- imágenes de ayuda (globos de los campos) ----------------------------------

_imagenes: dict[str, str] = {}


def _lapiz(p: QPainter, color: str, ancho: float = 2.0) -> None:
    p.setPen(QPen(QColor(color), ancho, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))


def _casilla(p: QPainter, x: float, y: float, marcada: bool) -> None:
    _lapiz(p, "#f37329" if marcada else "#9a9a9a", 2)
    p.setBrush(QColor("#f37329") if marcada else Qt.NoBrush)
    p.drawRoundedRect(QRectF(x, y, 20, 20), 3, 3)
    if marcada:
        _lapiz(p, "#ffffff", 3)
        p.drawPolyline([QPointF(x + 4, y + 10), QPointF(x + 8.5, y + 15), QPointF(x + 16, y + 5)])


def _pieza(p: QPainter, x: float, y: float, color: str, tachada: bool = False) -> None:
    """Una pieza de puzle: una extensión."""
    _lapiz(p, color, 2)
    p.setBrush(QColor(color).darker(260))
    p.drawRoundedRect(QRectF(x, y + 6, 26, 22), 3, 3)
    p.drawEllipse(QRectF(x + 8, y, 10, 10))
    p.drawEllipse(QRectF(x + 21, y + 12, 10, 10))
    if tachada:
        _lapiz(p, "#e0605a", 3)
        p.drawLine(QPointF(x - 4, y + 32), QPointF(x + 34, y - 2))


def _flecha(p: QPainter, x: float, y: float) -> None:
    _lapiz(p, "#cfcfcf", 2)
    p.drawLine(QPointF(x, y), QPointF(x + 28, y))
    p.drawPolyline([QPointF(x + 21, y - 6), QPointF(x + 28, y), QPointF(x + 21, y + 6)])


def _texto(p: QPainter, x: float, y: float, texto: str, color: str = "#e8e6df", negrita: bool = False) -> None:
    f = QFont(p.font())
    f.setPointSizeF(8.5)
    f.setBold(negrita)
    p.setFont(f)
    p.setPen(QColor(color))
    p.drawText(QPointF(x, y), texto)


def _dibujar(nombre: str) -> QPixmap:
    pm = QPixmap(300, 112)
    pm.fill(QColor("#232323"))
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    if nombre == "casilla":
        for fila, marcada in ((0, True), (1, False)):
            y = 14 + fila * 50
            _casilla(p, 12, y + 4, marcada)
            _flecha(p, 44, y + 14)
            _lapiz(p, "#5a5a5a", 1.5)
            p.setBrush(QColor("#1b1b1b"))
            p.drawRoundedRect(QRectF(82, y - 6, 62, 40), 4, 4)
            _pieza(p, 98, y - 1, VERDE if marcada else "#777777", tachada=not marcada)
            _texto(p, 156, y + 10, _t("Loaded at startup") if marcada else _t("Skipped at startup"),
                   VERDE if marcada else ROJO, True)
            _texto(p, 156, y + 26, "IngeTrazo", SUAVE)
    elif nombre == "nombre":
        _lapiz(p, "#f37329", 1.5)
        p.setBrush(QColor("#1b1b1b"))
        p.drawRoundedRect(QRectF(10, 10, 280, 26), 4, 4)
        _texto(p, 18, 28, _t("Modelling"), "#e8e6df")
        _flecha(p, 136, 54)
        _lapiz(p, "#3a3a3a", 1)
        p.setBrush(QColor("#1e1e1e"))
        p.drawRect(QRectF(176, 44, 114, 62))
        for i, (t, sel) in enumerate(((_t("Modelling"), True), (_t("Documentation"), False), ("…", False))):
            if sel:
                p.fillRect(QRectF(177, 46 + i * 20, 112, 19), QColor("#3a2a1c"))
            _texto(p, 184, 60 + i * 20, t, "#e8e6df" if sel else SUAVE, sel)
    elif nombre == "colocacion":
        _lapiz(p, "#5a5a5a", 1.5)
        p.setBrush(QColor("#1b1b1b"))
        p.drawRoundedRect(QRectF(10, 8, 280, 96), 4, 4)
        p.fillRect(QRectF(16, 14, 140, 12), QColor("#0C447C"))
        p.fillRect(QRectF(160, 14, 80, 12), QColor("#27500A"))
        p.fillRect(QRectF(16, 30, 14, 68), QColor("#633806"))
        p.fillRect(QRectF(224, 30, 60, 68), QColor("#3C3489"))
        _lapiz(p, "#f37329", 2)
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(14, 12, 228, 16))
        p.drawRect(QRectF(222, 28, 64, 72))
        _texto(p, 40, 62, _t("Toolbars and panels"), "#e8e6df", True)
        _texto(p, 40, 80, _t("in the same place"), SUAVE)
    elif nombre == "filtro":
        _lapiz(p, "#4a4a48", 1.5)
        p.setBrush(QColor("#1b1b1b"))
        p.drawRoundedRect(QRectF(10, 10, 150, 24), 4, 4)
        _texto(p, 18, 27, "ros", "#e8e6df")
        for i, (t, ok) in enumerate((("Rosco", True), ("Roscoclon", True), ("docpry", False), ("Texturas", False))):
            y = 44 + i * 16
            if ok:
                p.fillRect(QRectF(10, y, 280, 15), QColor("#2b241c"))
            _texto(p, 18, y + 12, t, "#e8e6df" if ok else "#555555", ok)
    p.end()
    return pm


def imagen(nombre: str) -> str:
    """URL de la imagen de ayuda ``nombre`` (se dibuja una vez por sesión)."""
    if nombre not in _imagenes:
        ruta = carpeta_datos() / "ayuda" / f"conjuntos_{nombre}.png"
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            _dibujar(nombre).save(str(ruta), "PNG")
            _imagenes[nombre] = QUrl.fromLocalFile(str(ruta)).toString()
        except Exception:  # noqa: BLE001 — sin imagen, el globo lleva solo el texto
            log.exception("imagen de ayuda %s", nombre)
            _imagenes[nombre] = ""
    return _imagenes[nombre]


def globo(nombre: str, titulo: str, texto: str) -> str:
    url = imagen(nombre)
    img = f"<p><img src='{url}'></p>" if url else ""
    return f"<p><b>{titulo}</b></p>{img}<p>{texto}</p>"


# ---- reiniciar IngeTrazo ----------------------------------------------------------

def reiniciar_ingetrazo() -> bool:
    """Cierra IngeTrazo como al pulsar ✕ (pregunta si se guarda el modelo) y lo
    vuelve a abrir cuando ya se ha cerrado. Devuelve False si no se cerró."""
    app = QApplication.instance()
    ventanas = [w for w in QApplication.topLevelWidgets() if isinstance(w, QMainWindow) and w.isVisible()]
    for w in ventanas:
        if not w.close():
            return False
    if getattr(sys, "frozen", False):
        programa, argumentos = sys.executable, []
    else:
        programa, argumentos = sys.executable, [os.path.abspath(sys.argv[0])] if sys.argv and sys.argv[0] else []

    def comillas(s: str) -> str:
        return "'" + s.replace("'", "''") + "'"

    orden = f"Wait-Process -Id {os.getpid()} -Timeout 120 -ErrorAction SilentlyContinue; " \
            f"Start-Process -FilePath {comillas(programa)} -WorkingDirectory {comillas(os.path.dirname(programa))}"
    if argumentos:
        orden += " -ArgumentList " + ",".join(comillas('"' + a + '"') for a in argumentos)
    try:
        subprocess.Popen(["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", orden],
                         creationflags=0x08000000 | 0x00000200, close_fds=True)
    except OSError:
        log.exception("no se pudo preparar el nuevo arranque")
    QTimer.singleShot(0, app.quit)
    return True


# ---- la lógica -------------------------------------------------------------------

class Conjuntos:
    def __init__(self, maestro) -> None:
        self.m = maestro
        # Lo que había en disco al arrancar = lo que está cargado en esta sesión.
        self.arranque = estado_en_disco()
        self._dlg = None

    @property
    def _win(self):
        return self.m.app.window

    @property
    def almacen(self):
        return self.m.almacen

    # -- comparar
    def coincide(self, conjunto: dict, disco: dict[str, bool]) -> bool:
        ids = [(i, True) for i in conjunto["activas"]] + [(i, False) for i in conjunto["inactivas"]]
        vistos = [(i, v) for i, v in ids if i in disco and i != PROPIA]
        return bool(vistos) and all(disco[i] == v for i, v in vistos)

    def cambios(self, destino: dict[str, bool]) -> tuple[list[str], list[str]]:
        """Qué se activará y qué se desactivará al reiniciar, frente a lo cargado ahora."""
        act = [i for i, v in destino.items() if v and not self.arranque.get(i, v)]
        des = [i for i, v in destino.items() if not v and self.arranque.get(i, v)]
        return sorted(act, key=str.casefold), sorted(des, key=str.casefold)

    def destino_de(self, conjunto: dict, disco: dict[str, bool]) -> dict[str, bool]:
        """El disco tal como quedaría con ``conjunto``: las extensiones que el
        conjunto no conoce (instaladas después) se quedan como estén."""
        destino = dict(disco)
        for i in conjunto["activas"]:
            if i in destino:
                destino[i] = True
        for i in conjunto["inactivas"]:
            if i in destino and i != PROPIA:
                destino[i] = False
        return destino

    def faltan(self, conjunto: dict, disco: dict[str, bool]) -> list[str]:
        return [i for i in (*conjunto["activas"], *conjunto["inactivas"]) if i not in disco]

    # -- menú
    def menu(self, menu: QMenu, con_gestor: bool = False) -> None:
        """Gestionar, guardar, la lista de conjuntos y volver al anterior. Con
        ``con_gestor`` (botón Extensiones del gestor de barras) empieza por la
        orden que abre el gestor de extensiones de IngeTrazo."""
        menu.clear()
        if con_gestor:
            menu.addAction("🧩 " + _t("Manage extensions…"), self.m.abrir_gestor_extensiones)
            menu.addSeparator()
            titulo = menu.addAction(_t("Extension sets").upper())
            titulo.setEnabled(False)
        menu.addAction(_t("Manage sets…"), self.abrir)
        menu.addAction(_t("Save the current set…"), self.guardar_actual)
        conjuntos = self.almacen.conjuntos
        if not conjuntos:
            menu.addAction(_t("(no saved sets yet)")).setEnabled(False)
        else:
            menu.addSeparator()
            disco = estado_en_disco()
            for c in conjuntos:
                marca = "● " if self.coincide(c, disco) else "    "
                menu.addAction(marca + c["nombre"].replace("&", "&&"),
                               lambda *_a, n=c["nombre"]: QTimer.singleShot(0, lambda: self.aplicar(n)))
        menu.addSeparator()
        volver = menu.addAction("↶ " + _t("Back to the previous one"), lambda: QTimer.singleShot(0, self.volver))
        volver.setEnabled(bool(self.almacen.conjunto_anterior.get("activas") or
                               self.almacen.conjunto_anterior.get("inactivas")))

    def abrir(self) -> None:
        try:
            if self._dlg is None:
                self._dlg = DialogoConjuntos(self)
            self._dlg.abrir()
        except Exception as err:  # noqa: BLE001 — que el fallo se vea en vez de no abrir nada
            log.exception("la ventana de conjuntos no se pudo abrir")
            self.m.app.viewport.flash_status(_t("The extension sets window could not open: {err}", err=err), 8000)

    def idioma_cambiado(self) -> None:
        if self._dlg is not None:
            visible = self._dlg.isVisible()
            self._dlg.close()
            self._dlg.deleteLater()
            self._dlg = None
            if visible:
                QTimer.singleShot(0, self.abrir)

    # -- guardar
    def colocacion_actual(self) -> str:
        return base64.b64encode(bytes(self._win.saveState(VERSION_QT))).decode("ascii")

    def guardar(self, nombre: str, estado: dict[str, bool], con_colocacion: bool, padre=None) -> bool:
        previo = self.almacen.conjunto(nombre)
        if previo is not None and QMessageBox.question(
                padre or self._win, _t("Extension sets"),
                _t("A set named «{name}» already exists. Overwrite it?", name=previo["nombre"])) != QMessageBox.Yes:
            return False
        self.almacen.poner_conjunto(nombre, estado, self.colocacion_actual() if con_colocacion else "")
        self.m.app.viewport.flash_status(_t("Set «{name}» saved.", name=nombre), 3000)
        return True

    def guardar_actual(self, padre=None, estado: dict[str, bool] | None = None) -> str | None:
        nombre, colocacion, ok = pedir_nombre(padre or self._win, _t("Save the current set"),
                                              _t("Set {n}", n=len(self.almacen.conjuntos) + 1))
        if not ok or not nombre:
            return None
        if self.guardar(nombre, estado_en_disco() if estado is None else estado, colocacion, padre):
            return nombre
        return None

    # -- aplicar
    def aplicar(self, nombre: str, padre=None) -> bool:
        c = self.almacen.conjunto(nombre)
        if c is None:
            return False
        exts = listar()
        disco = estado_en_disco(exts)
        aviso = ""
        faltan = self.faltan(c, disco)
        if faltan:
            aviso = _t("Not installed now (ignored): {names}", names=", ".join(faltan))
        return self.aplicar_estado(self.destino_de(c, disco), _t("Apply the set «{name}»?", name=c["nombre"]),
                                   exts=exts, colocacion=c.get("qt") or "", aviso=aviso, padre=padre)

    def volver(self, padre=None) -> bool:
        anterior = self.almacen.conjunto_anterior
        if not (anterior.get("activas") or anterior.get("inactivas")):
            QMessageBox.information(padre or self._win, _t("Extension sets"), _t("There is no previous set."))
            return False
        exts = listar()
        disco = estado_en_disco(exts)
        return self.aplicar_estado(self.destino_de(anterior, disco), _t("Go back to the previous set?"),
                                   exts=exts, colocacion=anterior.get("qt") or "", padre=padre)

    def aplicar_estado(self, destino: dict[str, bool], pregunta: str, exts: list[Ext] | None = None,
                       colocacion: str = "", aviso: str = "", padre=None) -> bool:
        """Pide confirmación con el resumen de cambios, escribe el disco,
        guarda el estado anterior y, si se pide, reinicia IngeTrazo."""
        padre = padre or self._win
        exts = listar() if exts is None else exts
        disco = estado_en_disco(exts)
        destino = {i: v for i, v in destino.items() if i in disco}
        if PROPIA in destino:
            destino[PROPIA] = True
        act, des = self.cambios(destino)
        hay_disco = any(disco[i] != v for i, v in destino.items())
        texto = [f"<b>{pregunta}</b>"]
        if act:
            texto.append(_t("It will turn on <b>{n}</b>: {names}", n=len(act), names=", ".join(act)))
        if des:
            texto.append(_t("It will turn off <b>{n}</b>: {names}", n=len(des), names=", ".join(des)))
        if not act and not des:
            texto.append(_t("No extension changes: everything is already like this."))
        if colocacion:
            texto.append(_t("The layout of toolbars and panels is also restored")
                         + (" " + _t("(at the next start).") if act or des else "."))
        if aviso:
            texto.append(f"<i>{aviso}</i>")
        if act or des:
            texto.append(f"<span style='color:{SUAVE}'>"
                         + _t("The changes take effect when IngeTrazo restarts. The current set is kept so you can "
                              "go «Back to the previous one».") + "</span>")
        caja = QMessageBox(QMessageBox.Question, _t("Extension sets"), "<br><br>".join(texto), parent=padre)
        caja.setTextFormat(Qt.RichText)
        caja.addButton(QMessageBox.Cancel)
        if act or des:
            luego = caja.addButton(_t("Apply (I will restart later)"), QMessageBox.AcceptRole)
            ahora_b = caja.addButton(_t("Apply and restart now"), QMessageBox.YesRole)
            caja.setDefaultButton(ahora_b)
        else:
            luego = caja.addButton(_t("Apply"), QMessageBox.AcceptRole)
            ahora_b = None
            caja.setDefaultButton(luego)
        caja.exec()
        pulsado = caja.clickedButton()
        if pulsado not in (luego, ahora_b) or pulsado is None:
            return False

        if hay_disco:
            anterior = {"activas": [i for i, v in disco.items() if v], "inactivas": [i for i, v in disco.items() if not v]}
            pendiente = self.almacen.colocacion_pendiente
            if pendiente:
                anterior["qt"] = pendiente
            self.almacen.poner_anterior(anterior)
        errores = []
        for x in exts:
            if x.id in destino and not x.bloqueada:
                try:
                    poner_activa(x, destino[x.id])
                except OSError as err:
                    errores.append(f"{x.id}: {err}")
        if colocacion:
            if act or des:
                self.almacen.poner_colocacion_pendiente(colocacion)
            else:
                self.restaurar_colocacion(colocacion)
        elif act or des:
            self.almacen.poner_colocacion_pendiente("")
        if errores:
            QMessageBox.warning(padre, _t("Extension sets"),
                                _t("These extensions could not be changed:") + "\n\n" + "\n".join(errores))
        if self._dlg is not None and self._dlg.isVisible():
            self._dlg.recargar()
        if pulsado is ahora_b:
            if not reiniciar_ingetrazo():
                self.m.app.viewport.flash_status(
                    _t("IngeTrazo was not closed: the changes will apply at the next start."), 6000)
        elif act or des:
            self.m.app.viewport.flash_status(_t("Changes saved: restart IngeTrazo to apply them."), 5000)
        return True

    def descartar(self, padre=None) -> None:
        """Deja el disco como estaba al arrancar (lo cargado ahora)."""
        errores = []
        for x in listar():
            if x.id in self.arranque and not x.bloqueada:
                try:
                    poner_activa(x, self.arranque[x.id])
                except OSError as err:
                    errores.append(f"{x.id}: {err}")
        self.almacen.poner_colocacion_pendiente("")
        if errores:
            QMessageBox.warning(padre or self._win, _t("Extension sets"),
                                _t("These extensions could not be changed:") + "\n\n" + "\n".join(errores))

    # -- colocación de barras
    def restaurar_colocacion(self, qt: str) -> bool:
        try:
            crudo = base64.b64decode(qt, validate=True)
            hecho = bool(self._win.restoreState(QByteArray(crudo), VERSION_QT))
        except (binascii.Error, ValueError):
            log.exception("colocación de barras ilegible")
            hecho = False
        if hecho:
            self.m.barras_cambiadas()
        return hecho

    def tras_arranque(self) -> None:
        """Si un conjunto dejó pendiente la colocación de barras, ahora que ya
        están cargadas todas las extensiones, se aplica."""
        qt = self.almacen.colocacion_pendiente
        if not qt:
            return
        self.almacen.poner_colocacion_pendiente("")
        if self.restaurar_colocacion(qt):
            self.m.app.viewport.flash_status(_t("Layout of toolbars and panels of the set restored."), 4000)

    # -- exportar / importar
    def exportar(self, nombres: list[str], padre=None) -> None:
        padre = padre or self._win
        lista = [c for c in self.almacen.conjuntos if c["nombre"] in nombres]
        if not lista:
            return
        base = lista[0]["nombre"] if len(lista) == 1 else "conjuntos"
        base = "".join(ch for ch in base if ch not in '\\/:*?"<>|').strip() or "conjuntos"
        ruta, _f = QFileDialog.getSaveFileName(padre, _t("Export extension sets"), base + EXT_CONJUNTOS,
                                               f"{_t('Extension sets')} (*{EXT_CONJUNTOS})")
        if not ruta:
            return
        if not ruta.endswith(EXT_CONJUNTOS):
            ruta += EXT_CONJUNTOS
        try:
            Path(ruta).write_text(json.dumps({"conjuntos": lista}, ensure_ascii=False, indent=1), encoding="utf-8")
            self.m.app.viewport.flash_status(_t("Exported to {path}", path=ruta), 4000)
        except OSError as err:
            QMessageBox.critical(padre, _t("Extension sets"), str(err))

    def importar(self, padre=None) -> list[str]:
        padre = padre or self._win
        ruta, _f = QFileDialog.getOpenFileName(padre, _t("Import extension sets"), "",
                                               f"{_t('Extension sets')} (*{EXT_CONJUNTOS} *.json)")
        if not ruta:
            return []
        try:
            crudo = json.loads(Path(ruta).read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            QMessageBox.critical(padre, _t("Extension sets"), str(err))
            return []
        nuevos = self.almacen.importar_conjuntos(crudo)
        if not nuevos:
            QMessageBox.information(padre, _t("Extension sets"), _t("The file has no new extension sets."))
        else:
            self.m.app.viewport.flash_status(_t("Imported: {names}", names=", ".join(nuevos)), 4000)
        return nuevos


# ---- ventanita para el nombre ----------------------------------------------------

def pedir_nombre(padre, titulo: str, texto: str = "", colocacion: bool = False,
                 con_casilla: bool = True) -> tuple[str, bool, bool]:
    """Nombre del conjunto (con micrófono) y la casilla de la colocación de
    barras. Devuelve (nombre, recordar_colocación, aceptado)."""
    from ._maestro_dlg import ESTILO
    dlg = QDialog(padre)
    dlg.setObjectName(PREFIJO + "_dlg_nombre_conjunto")
    dlg.setWindowTitle(titulo)
    dlg.setStyleSheet(ESTILO)
    dlg.setMinimumWidth(380)
    lay = QVBoxLayout(dlg)
    etiqueta = QLabel(_t("Name of the set"))
    lay.addWidget(etiqueta)
    campo = con_microfono(QLineEdit(texto))
    campo.selectAll()
    ayuda = globo("nombre", _t("Name of the set"),
                  _t("The name you will choose in the menu or in the list of sets to bring this set back."))
    campo.setToolTip(ayuda)
    etiqueta.setToolTip(ayuda)
    lay.addWidget(campo)
    casilla = QCheckBox(_t("Also remember where the toolbars and panels are"))
    casilla.setChecked(colocacion)
    casilla.setToolTip(globo("colocacion", _t("Also remember where the toolbars and panels are"),
                             _t("When the set is applied, the toolbars and panels go back to where they are now. "
                                "If extensions change, it is done at the next start, when their toolbars exist.")))
    casilla.setVisible(con_casilla)
    lay.addWidget(casilla)
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
    resultado = (campo.text().strip(), casilla.isChecked(), aceptado)
    dlg.deleteLater()
    return resultado


# ---- la ventana «Conjuntos de extensiones» ---------------------------------------

ESTILO_EXTRA = f"""
QWidget#{PREFIJO}_cj_izq {{ background: #1e1e1e; border-right: 3px solid #3a3a3a; }}
QLabel#{PREFIJO}_cj_tit_izq {{ background: #3C3489; color: #CECBF6; font-weight: bold; padding: 6px 10px; }}
QWidget#{PREFIJO}_cj_tit_der {{ background: #0C447C; }}
QLabel#{PREFIJO}_cj_tit_der_t {{ color: #B5D4F4; font-weight: bold; }}
QListWidget {{ background: #1e1e1e; color: #D3D1C7; border: none; outline: 0; }}
QListWidget::item {{ padding: 6px 8px; border-bottom: 1px solid #2e2e2e; }}
QListWidget::item:selected {{ background: #3a2a1c; color: #ffffff; border-left: 3px solid #f37329; }}
QTreeWidget {{ background: #232323; color: #D3D1C7; border: none; alternate-background-color: #262626; outline: 0; }}
QTreeWidget::item {{ padding: 3px 2px; border-bottom: 1px solid #2e2e2e; }}
QTreeWidget::item:selected {{ background: #333333; color: #ffffff; }}
QTreeWidget::indicator {{ width: 15px; height: 15px; }}
QHeaderView::section {{ background: #2a2a2a; color: #888780; border: none; border-bottom: 1px solid #3a3a3a;
            padding: 4px 6px; font-weight: bold; }}
QWidget#{PREFIJO}_cj_pie {{ background: #2b241c; border-top: 1px solid #4a3a28; }}
QLabel#{PREFIJO}_cj_pie_t {{ color: #ffd9bf; }}
QPushButton#{PREFIJO}_cj_prim {{ background: #4a2a12; border-color: #f37329; color: #ffd9bf; }}
QPushButton:disabled, QPushButton#{PREFIJO}_cj_prim:disabled, QToolButton#{PREFIJO}_boton:disabled {{
            background: #2a2a2a; color: #5f5f5c; border-color: #3a3a3a; }}
"""


class DialogoConjuntos(QDialog):
    COL_CASILLA, COL_NOMBRE, COL_AHORA, COL_LUEGO, COL_ORIGEN = range(5)

    def __init__(self, conjuntos: Conjuntos) -> None:
        super().__init__(conjuntos.m.app.window)
        from ._maestro_dlg import ESTILO
        self.c = conjuntos
        self.exts: list[Ext] = []
        self.marcadas: dict[str, bool] = {}
        self._rellenando = False
        self.setObjectName(PREFIJO + "_dlg_conjuntos")
        self.setWindowTitle("🧩 " + _t("Extension sets") + " — Toolkeeper")
        self.setWindowIcon(conjuntos.m.iconos["dragon"])
        self.setStyleSheet(ESTILO + ESTILO_EXTRA)
        self.resize(980, 600)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)
        lay.addLayout(cuerpo, 1)

        # -- izquierda: los conjuntos
        izq = QWidget()
        izq.setObjectName(PREFIJO + "_cj_izq")
        izq.setAttribute(Qt.WA_StyledBackground, True)
        izq.setFixedWidth(270)
        il = QVBoxLayout(izq)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(0)
        t = QLabel(_t("Saved sets"))
        t.setObjectName(PREFIJO + "_cj_tit_izq")
        il.addWidget(t)
        self.lista = QListWidget()
        self.lista.itemSelectionChanged.connect(self._botones_lista)
        self.lista.itemDoubleClicked.connect(lambda _i: self._aplicar_sel())
        il.addWidget(self.lista, 1)
        rejilla = QGridLayout()
        rejilla.setContentsMargins(8, 8, 8, 8)
        rejilla.setSpacing(5)
        self.b_nuevo = self._boton("＋ " + _t("New…"), _t("Save the ticked extensions as a new set"), self._nuevo)
        self.b_aplicar = self._boton(_t("Apply"), _t("Apply the selected set"), self._aplicar_sel, primario=True)
        self.b_volver = self._boton("↶ " + _t("Previous"), _t("Back to the previous one"), self._volver)
        self.b_actualizar = self._boton(_t("Update"), _t("Overwrite the selected set with the ticked extensions"),
                                        self._actualizar)
        self.b_renombrar = self._boton(_t("Rename…"), _t("Rename the selected set"), self._renombrar)
        self.b_borrar = self._boton("🗑 " + _t("Delete"), _t("Delete the selected set"), self._borrar)
        self.b_exportar = QToolButton()
        self.b_exportar.setObjectName(PREFIJO + "_boton")
        self.b_exportar.setText("⤒ " + _t("Export") + " ▾")
        self.b_exportar.setToolTip(_t("Export the selected set or all of them to a file"))
        self.b_exportar.setPopupMode(QToolButton.InstantPopup)
        menu_exp = QMenu(self.b_exportar)
        menu_exp.addAction(_t("The selected set…"), self._exportar_sel)
        menu_exp.addAction(_t("All the sets…"), lambda: self.c.exportar([x["nombre"] for x in self.c.almacen.conjuntos], self))
        self.b_exportar.setMenu(menu_exp)
        self.b_importar = self._boton("⤓ " + _t("Import…"), _t("Import extension sets from a file"), self._importar)
        for i, b in enumerate((self.b_nuevo, self.b_aplicar, self.b_volver, self.b_actualizar, self.b_renombrar,
                               self.b_borrar, self.b_exportar, self.b_importar)):
            b.setSizePolicy(b.sizePolicy().horizontalPolicy(), b.sizePolicy().verticalPolicy())
            b.setMinimumWidth(110)
            rejilla.addWidget(b, i // 2, i % 2)
        il.addLayout(rejilla)
        cuerpo.addWidget(izq)

        # -- derecha: las extensiones
        der = QVBoxLayout()
        der.setContentsMargins(0, 0, 0, 0)
        der.setSpacing(0)
        cab = QWidget()
        cab.setObjectName(PREFIJO + "_cj_tit_der")
        cab.setAttribute(Qt.WA_StyledBackground, True)
        cl = QHBoxLayout(cab)
        cl.setContentsMargins(10, 5, 8, 5)
        cl.setSpacing(6)
        self.titulo_ext = QLabel()
        self.titulo_ext.setObjectName(PREFIJO + "_cj_tit_der_t")
        cl.addWidget(self.titulo_ext)
        cl.addSpacing(8)
        self.filtro = con_microfono(QLineEdit())
        self.filtro.setPlaceholderText(_t("Filter…"))
        self.filtro.setClearButtonEnabled(True)
        self.filtro.setToolTip(globo("filtro", _t("Filter"), _t("Shows only the extensions whose name contains "
                                                                 "what you type.")))
        self.filtro.textChanged.connect(lambda _s: self._filtrar())
        cl.addWidget(self.filtro, 1)
        cl.addWidget(self._boton(_t("Turn all on"), _t("Tick every extension"), lambda: self._todas(True)))
        cl.addWidget(self._boton(_t("Turn all off"), _t("Untick every extension (except Toolkeeper)"),
                                 lambda: self._todas(False)))
        der.addWidget(cab)
        self.arbol = QTreeWidget()
        self.arbol.setRootIsDecorated(False)
        self.arbol.setAlternatingRowColors(True)
        self.arbol.setUniformRowHeights(True)
        self.arbol.setSelectionMode(QAbstractItemView.SingleSelection)
        self.arbol.setHeaderLabels(["", _t("Extension"), _t("Now"), _t("After restart"), _t("Installed")])
        cabecera = self.arbol.header()
        cabecera.setStretchLastSection(False)
        cabecera.setSectionResizeMode(self.COL_CASILLA, QHeaderView.Fixed)
        cabecera.resizeSection(self.COL_CASILLA, 34)
        cabecera.setSectionResizeMode(self.COL_NOMBRE, QHeaderView.Stretch)
        for col in (self.COL_AHORA, self.COL_LUEGO, self.COL_ORIGEN):
            cabecera.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.arbol.itemChanged.connect(self._casilla_cambiada)
        der.addWidget(self.arbol, 1)
        cuerpo.addLayout(der, 1)

        # -- pie: cambios pendientes
        self.pie = QWidget()
        self.pie.setObjectName(PREFIJO + "_cj_pie")
        self.pie.setAttribute(Qt.WA_StyledBackground, True)
        pl = QHBoxLayout(self.pie)
        pl.setContentsMargins(10, 6, 10, 6)
        self.pie_texto = QLabel()
        self.pie_texto.setObjectName(PREFIJO + "_cj_pie_t")
        pl.addWidget(self.pie_texto, 1)
        self.b_descartar = QPushButton(_t("Discard changes"))
        self.b_descartar.setToolTip(_t("Leave the extensions as they were when IngeTrazo started"))
        self.b_descartar.clicked.connect(self._descartar)
        pl.addWidget(self.b_descartar)
        self.b_aplicar_pie = QPushButton(_t("Apply and restart…"))
        self.b_aplicar_pie.setObjectName(PREFIJO + "_cj_prim")
        self.b_aplicar_pie.clicked.connect(self._aplicar_marcadas)
        pl.addWidget(self.b_aplicar_pie)
        lay.addWidget(self.pie)

        self.estado = QLabel(_t("The extensions included with IngeTrazo (Python console, Solid inspector…) are not "
                                "listed: they cannot be turned off."))
        self.estado.setObjectName(PREFIJO + "_estado")
        lay.addWidget(self.estado)

    def _boton(self, texto: str, consejo: str, fn, primario: bool = False) -> QPushButton:
        b = QPushButton(texto)
        b.setToolTip(consejo)
        b.setAutoDefault(False)
        if primario:
            b.setObjectName(PREFIJO + "_cj_prim")
        b.clicked.connect(lambda _c=False, f=fn: f())
        return b

    # -- abrir y rellenar
    def abrir(self) -> None:
        self.recargar()
        self.show()
        self.raise_()
        self.activateWindow()

    def recargar(self) -> None:
        """Vuelve a leer el disco (las casillas pasan a ser lo que hay en él)."""
        self.exts = listar()
        self.marcadas = {x.id: x.activa for x in self.exts}
        self._rellenar_extensiones()
        self._rellenar_lista()

    def _rellenar_lista(self, seleccionar: str | None = None) -> None:
        actual = seleccionar or (self.lista.currentItem().data(Qt.UserRole) if self.lista.currentItem() else None)
        self.lista.blockSignals(True)
        self.lista.clear()
        disco = estado_en_disco(self.exts)
        for cj in self.c.almacen.conjuntos:
            marca = "● " if self.c.coincide(cj, disco) else ""
            extra = "  ▦" if cj.get("qt") else ""
            it = QListWidgetItem(f"{marca}{cj['nombre']}{extra}")
            it.setData(Qt.UserRole, cj["nombre"])
            fecha = cj.get("fecha", "")[:16].replace("T", " ")
            consejo = _t("Saved: {date}", date=fecha) + "\n" + \
                _t("On: {n} · Off: {m}", n=len(cj["activas"]), m=len(cj["inactivas"]))
            if cj.get("qt"):
                consejo += "\n▦ " + _t("Also remembers where the toolbars and panels are")
            if marca:
                consejo += "\n● " + _t("It is the current set")
            it.setToolTip(consejo)
            self.lista.addItem(it)
            if cj["nombre"] == actual:
                it.setSelected(True)
                self.lista.setCurrentItem(it)
        self.lista.blockSignals(False)
        self._botones_lista()

    def _rellenar_extensiones(self) -> None:
        self._rellenando = True
        self.arbol.clear()
        ayuda = globo("casilla", _t("On at startup"),
                      _t("Ticked: IngeTrazo loads this extension when it starts. Unticked: IngeTrazo skips it. "
                         "Nothing changes until you press Apply."))
        for x in self.exts:
            it = QTreeWidgetItem()
            it.setData(self.COL_CASILLA, Qt.UserRole, x.id)
            it.setText(self.COL_NOMBRE, x.id)
            if x.bloqueada:
                it.setText(self.COL_CASILLA, "🔒")
                it.setFlags(Qt.ItemIsEnabled)
                it.setToolTip(self.COL_CASILLA, _t("Toolkeeper cannot be turned off (you would lose this window)."))
                f = it.font(self.COL_NOMBRE)
                f.setBold(True)
                it.setFont(self.COL_NOMBRE, f)
            else:
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
                it.setCheckState(self.COL_CASILLA, Qt.Checked if self.marcadas[x.id] else Qt.Unchecked)
                it.setToolTip(self.COL_CASILLA, ayuda)
                it.setToolTip(self.COL_NOMBRE, ayuda)
            origen = _t("catalogue") if x.catalogo else (_t("loose file") if x.tipo == "archivo" else _t("by hand"))
            if x.bloqueada:
                origen += " · " + _t("always on")
            it.setText(self.COL_ORIGEN, origen)
            it.setForeground(self.COL_ORIGEN, QBrush(QColor(SUAVE)))
            self.arbol.addTopLevelItem(it)
            self._pintar_fila(it, x)
        self._rellenando = False
        self._filtrar()
        self._pie()

    def _pintar_fila(self, it: QTreeWidgetItem, x: Ext) -> None:
        al_arrancar = self.c.arranque.get(x.id, x.activa)
        if x.cargada:
            ahora_t, color = _t("Loaded"), VERDE
        elif al_arrancar:
            ahora_t, color = _t("Not loaded (error?)"), NARANJA
        else:
            ahora_t, color = _t("Off"), ROJO
        it.setText(self.COL_AHORA, ahora_t)
        it.setForeground(self.COL_AHORA, QBrush(QColor(color)))
        quiere = self.marcadas.get(x.id, x.activa)
        if x.bloqueada or quiere == al_arrancar:
            it.setText(self.COL_LUEGO, "—")
            it.setForeground(self.COL_LUEGO, QBrush(QColor(SUAVE)))
            fondo = QBrush()
        else:
            it.setText(self.COL_LUEGO, _t("Will turn on") if quiere else _t("Will turn off"))
            it.setForeground(self.COL_LUEGO, QBrush(QColor("#9fe0a8" if quiere else NARANJA)))
            fondo = QBrush(QColor("#2b241c"))
        for col in range(5):
            it.setBackground(col, fondo)

    def _fila_de(self, ident: str) -> QTreeWidgetItem | None:
        for i in range(self.arbol.topLevelItemCount()):
            it = self.arbol.topLevelItem(i)
            if it.data(self.COL_CASILLA, Qt.UserRole) == ident:
                return it
        return None

    def _ext(self, ident: str) -> Ext | None:
        return next((x for x in self.exts if x.id == ident), None)

    # -- casillas
    def _casilla_cambiada(self, it: QTreeWidgetItem, col: int) -> None:
        if self._rellenando or col != self.COL_CASILLA:
            return
        ident = it.data(self.COL_CASILLA, Qt.UserRole)
        x = self._ext(ident)
        if x is None or x.bloqueada:
            return
        self.marcadas[ident] = it.checkState(self.COL_CASILLA) == Qt.Checked
        self._rellenando = True
        self._pintar_fila(it, x)
        self._rellenando = False
        self._pie()

    def _todas(self, activa: bool) -> None:
        self._rellenando = True
        for x in self.exts:
            if x.bloqueada:
                continue
            it = self._fila_de(x.id)
            if it is not None and it.isHidden():
                continue                    # con filtro, solo las que se ven
            self.marcadas[x.id] = activa
            if it is not None:
                it.setCheckState(self.COL_CASILLA, Qt.Checked if activa else Qt.Unchecked)
                self._pintar_fila(it, x)
        self._rellenando = False
        self._pie()

    def _filtrar(self) -> None:
        texto = self.filtro.text().strip().casefold()
        vistas = 0
        for i in range(self.arbol.topLevelItemCount()):
            it = self.arbol.topLevelItem(i)
            oculta = bool(texto) and texto not in it.text(self.COL_NOMBRE).casefold()
            it.setHidden(oculta)
            vistas += not oculta
        total = len(self.exts)
        self.titulo_ext.setText(_t("Extensions ({n})", n=total) if vistas == total
                                else _t("Extensions ({n} of {m})", n=vistas, m=total))

    def _pie(self) -> None:
        act, des = self.c.cambios(self.marcadas)
        sin_escribir = any(x.activa != self.marcadas.get(x.id, x.activa) for x in self.exts)
        n = len(act) + len(des)
        if n:
            self.pie_texto.setText("⚠ " + _t("{n} pending changes: they apply when IngeTrazo restarts.", n=n))
        elif sin_escribir:
            self.pie_texto.setText(_t("Unsaved changes."))
        self.pie.setVisible(bool(n) or sin_escribir)
        self.b_aplicar_pie.setText(_t("Apply and restart…") if n else _t("Apply"))

    # -- botones de la lista
    def _sel(self) -> str | None:
        it = self.lista.currentItem()
        return it.data(Qt.UserRole) if it is not None and it.isSelected() else None

    def _botones_lista(self) -> None:
        hay = self._sel() is not None
        for b in (self.b_aplicar, self.b_actualizar, self.b_renombrar, self.b_borrar):
            b.setEnabled(hay)
        self.b_exportar.setEnabled(bool(self.c.almacen.conjuntos))
        anterior = self.c.almacen.conjunto_anterior
        self.b_volver.setEnabled(bool(anterior.get("activas") or anterior.get("inactivas")))
        if hay:
            cj = self.c.almacen.conjunto(self._sel())
            if cj is not None:
                self._mostrar_conjunto(cj)

    def _mostrar_conjunto(self, cj: dict) -> None:
        """Marca las casillas como las dejaría el conjunto (sin escribir nada)."""
        destino = self.c.destino_de(cj, {x.id: x.activa for x in self.exts})
        self.marcadas.update(destino)
        self._rellenando = True
        for x in self.exts:
            it = self._fila_de(x.id)
            if it is not None and not x.bloqueada:
                it.setCheckState(self.COL_CASILLA, Qt.Checked if self.marcadas[x.id] else Qt.Unchecked)
                self._pintar_fila(it, x)
        self._rellenando = False
        self._pie()
        faltan = self.c.faltan(cj, estado_en_disco(self.exts))
        self.estado.setText(_t("Set «{name}»: the ticks show how it would leave the extensions.", name=cj["nombre"])
                            + (" " + _t("Not installed now (ignored): {names}", names=", ".join(faltan))
                               if faltan else ""))

    def _nuevo(self) -> None:
        nombre = self.c.guardar_actual(self, dict(self.marcadas))
        if nombre:
            self._rellenar_lista(nombre)

    def _aplicar_sel(self) -> None:
        nombre = self._sel()
        if nombre and self.c.aplicar(nombre, self):
            self.recargar()

    def _aplicar_marcadas(self) -> None:
        if self.c.aplicar_estado(dict(self.marcadas), _t("Apply the ticked extensions?"), padre=self):
            self.recargar()

    def _volver(self) -> None:
        if self.c.volver(self):
            self.recargar()

    def _descartar(self) -> None:
        if QMessageBox.question(self, _t("Extension sets"),
                                _t("Leave the extensions as they were when IngeTrazo started?")) != QMessageBox.Yes:
            return
        self.c.descartar(self)
        self.lista.clearSelection()
        self.recargar()

    def _actualizar(self) -> None:
        nombre = self._sel()
        cj = self.c.almacen.conjunto(nombre) if nombre else None
        if cj is None:
            return
        _n, colocacion, ok = pedir_nombre(self, _t("Update the set «{name}»", name=cj["nombre"]), cj["nombre"],
                                          colocacion=bool(cj.get("qt")))
        if not ok:
            return
        self.c.almacen.poner_conjunto(cj["nombre"], dict(self.marcadas),
                                      self.c.colocacion_actual() if colocacion else "")
        self.c.m.app.viewport.flash_status(_t("Set «{name}» updated.", name=cj["nombre"]), 3000)
        self._rellenar_lista(cj["nombre"])

    def _renombrar(self) -> None:
        nombre = self._sel()
        if not nombre:
            return
        nuevo, _c, ok = pedir_nombre(self, _t("Rename the set"), nombre, con_casilla=False)
        if not ok or not nuevo or nuevo == nombre:
            return
        otro = self.c.almacen.conjunto(nuevo)
        if otro is not None and otro["nombre"].casefold() != nombre.casefold():
            QMessageBox.warning(self, _t("Extension sets"), _t("That name is already used."))
            return
        self.c.almacen.renombrar_conjunto(nombre, nuevo)
        self._rellenar_lista(nuevo)

    def _borrar(self) -> None:
        nombre = self._sel()
        if nombre and QMessageBox.question(self, _t("Extension sets"),
                                           _t("Delete the set «{name}»?", name=nombre)) == QMessageBox.Yes:
            self.c.almacen.borrar_conjunto(nombre)
            self.recargar()

    def _exportar_sel(self) -> None:
        nombre = self._sel()
        if not nombre:
            QMessageBox.information(self, _t("Extension sets"), _t("Select a set in the list first."))
            return
        self.c.exportar([nombre], self)

    def _importar(self) -> None:
        nuevos = self.c.importar(self)
        if nuevos:
            self._rellenar_lista(nuevos[0])

    def closeEvent(self, ev) -> None:
        self.lista.clearSelection()
        super().closeEvent(ev)
