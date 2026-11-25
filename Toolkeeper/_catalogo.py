# SPDX-License-Identifier: GPL-3.0-or-later
"""El catálogo de comandos: todas las acciones de la ventana que se pueden
pulsar (menús, barras, herramientas, extensiones), cada una con una clave
estable entre sesiones e idiomas, y agrupadas como las presenta el gestor
maestro: comandos nativos de IngeTrazo por barra, y una sección por
extensión.

La clave es la misma que usa IngeTrazo para sus atajos y para los recientes
de F3 (``views.shortcuts.action_key``): el objectName de la acción o, si no
tiene, ``"text:"`` + su texto original en inglés.
"""
from __future__ import annotations

import logging
import time
import unicodedata

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMainWindow, QMenu, QToolBar

from . import _iconos
from ._datos import PERSONAL

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

PREFIJO = "igz_toolkeeper"              # objectName de lo propio (IngeTrazo recuerda por él la posición de las barras)
SEP_RUTA = " ▸ "
# Barras nativas de IngeTrazo 0.5.8, en el orden del gestor de barras.
NATIVAS = ("main", "draw", "modify", "annotate", "sections", "solids", "walkthrough",
           "view", "views", "panels_toolbar")

try:
    from shiboken6 import isValid as _vivo
except Exception:  # noqa: BLE001
    def _vivo(_obj) -> bool:
        return True


def vivo(obj) -> bool:
    try:
        return obj is not None and _vivo(obj)
    except Exception:  # noqa: BLE001
        return False


def plano(texto: str) -> str:
    """El texto de una acción sin «&», puntos suspensivos ni atajo final."""
    texto = (texto or "").replace("&&", "\0").replace("&", "").replace("\0", "&")
    texto = texto.split("\t")[0]
    return texto.rstrip("…").rstrip(".").strip()


def origen_ingles(texto: str) -> str:
    try:
        from core.i18n import source_of
        return source_of(texto)
    except Exception:  # noqa: BLE001
        return texto


def tr_app(texto: str) -> str:
    try:
        from core.i18n import tr
        return tr(texto)
    except Exception:  # noqa: BLE001
        return texto


def clave(accion: QAction) -> str:
    try:
        from views.shortcuts import action_key
        return action_key(accion)
    except Exception:  # noqa: BLE001
        nombre = accion.objectName()
        return nombre if nombre else "text:" + plano(origen_ingles(accion.text()))


def normalizar(texto: str) -> str:
    """Para buscar: minúsculas y sin tildes."""
    t = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in t if not unicodedata.combining(c)).casefold()


def coincide(patron: str, texto: str) -> bool:
    """Búsqueda con comodín «*»: sin asterisco busca la subcadena; con él,
    cada trozo en orden."""
    patron, texto = normalizar(patron.strip()), normalizar(texto)
    if not patron:
        return True
    if "*" not in patron:
        return patron in texto
    pos = 0
    for trozo in patron.split("*"):
        if not trozo:
            continue
        i = texto.find(trozo, pos)
        if i < 0:
            return False
        pos = i + len(trozo)
    return True


def pertenece(accion: QAction, ventana) -> bool:
    obj = accion.parent()
    while obj is not None:
        if isinstance(obj, QMainWindow):
            return obj is ventana
        obj = obj.parent()
    return False


def de_maestro(obj) -> bool:
    """El objeto vive dentro de algo de Toolkeeper (sus menús, barras,
    diálogos): no es un comando de IngeTrazo."""
    while obj is not None:
        if obj.objectName().startswith(PREFIJO):
            return True
        obj = obj.parent()
    return False


class Comando:
    __slots__ = ("key", "nombre", "ruta", "accion", "atajo", "origen", "descripcion", "run")

    def __init__(self, key, nombre, ruta, accion, atajo="", origen="", descripcion="", run=None):
        self.key, self.nombre, self.ruta = key, nombre, ruta
        self.accion, self.atajo, self.origen = accion, atajo, origen
        self.descripcion, self.run = descripcion, run

    def texto_busqueda(self) -> str:
        return f"{self.nombre} {origen_ingles(self.nombre)} {self.ruta} {self.origen}"

    def disponible(self) -> bool:
        return self.run is not None or (vivo(self.accion) and self.accion.isEnabled())

    def tooltip(self) -> str:
        partes = [f"[{self.origen}]" if self.origen else "", self.nombre, self.descripcion]
        return "\n".join(p for p in partes if p)


def _descripcion(act: QAction) -> str:
    for texto in (act.statusTip(), act.toolTip()):
        texto = plano(texto)
        if texto and texto != plano(act.text()):
            return texto.split("\n")[0]
    return ""


class Catalogo:
    """Índice clave → comando y las secciones del gestor de barras,
    reconstruidos cuando hace falta (como mucho una vez cada dos segundos
    al pedir una clave que no está)."""

    def __init__(self, ventana) -> None:
        self.ventana = ventana
        self._indice: dict = {}
        self._lista: list = []
        self._secciones: list = []
        self._hora = 0.0
        self._iconos: dict = {}
        self.extra = None          # callable(key) → Comando | None (comandos personales)

    # -- construcción
    def refrescar(self) -> list:
        win = self.ventana
        self._lista, self._secciones, self._indice = [], [], {}
        rutas = self._rutas_menus()
        en_barra: set = set()

        def anadir(act, origen, grupo) -> Comando | None:
            if act.isSeparator() or act.menu() is not None or not plano(act.text()):
                return None
            if not pertenece(act, win) or de_maestro(act):
                return None
            k = clave(act)
            c = self._indice.get(k)
            if c is None:
                c = Comando(k, plano(act.text()), rutas.get(id(act), grupo), act,
                            act.shortcut().toString(), origen, _descripcion(act))
                self._indice[k] = c
                self._lista.append(c)
            return c

        # 1) IngeTrazo: una fila por barra nativa
        filas_nativas = []
        barras = {tb.objectName(): tb for tb in win.findChildren(QToolBar)
                  if tb.parent() is win and not de_maestro(tb)}
        for obj in NATIVAS:
            tb = barras.pop(obj, None)
            if tb is None:
                continue
            fila = [c for c in (anadir(a, "IngeTrazo", tb.windowTitle()) for a in tb.actions()) if c]
            en_barra.update(c.key for c in fila)
            if fila:
                filas_nativas.append((tb.windowTitle() or obj, fila))
        # 2) menús de IngeTrazo que no están en ninguna barra (sin Extensiones)
        ext_menu = getattr(win, "_ext_menu", None)
        menus_ext: list = []
        otras_menu: dict = {}
        for top in win.menuBar().actions():
            menu = top.menu()
            if menu is None:
                continue
            if ext_menu is not None and menu is ext_menu:
                continue
            titulo = plano(menu.title())
            for act in self._acciones_de(menu):
                c = anadir(act, "IngeTrazo", titulo)
                if c is not None and c.key not in en_barra:
                    otras_menu.setdefault(titulo, []).append(c)
        for titulo, fila in otras_menu.items():
            filas_nativas.append((titulo, fila))
        if filas_nativas:
            self._secciones.append(("IngeTrazo", filas_nativas, True))
        # 3) extensiones: submenús de Extensiones y barras no nativas
        secciones_ext: dict = {}
        if ext_menu is not None:
            for act in ext_menu.actions():
                sub = act.menu()
                if sub is not None:
                    titulo = plano(sub.title())
                    fila = [c for c in (anadir(a, titulo, titulo) for a in self._acciones_de(sub)) if c]
                    if fila:
                        secciones_ext.setdefault(titulo, []).append((titulo, fila))
                elif not act.isSeparator() and plano(act.text()):
                    c = anadir(act, "Extensions", plano(ext_menu.title()))
                    if c is not None:
                        secciones_ext.setdefault(plano(ext_menu.title()), []).append((c.nombre, [c]))
        for obj, tb in barras.items():
            titulo = tb.windowTitle() or obj
            fila = [c for c in (anadir(a, titulo, titulo) for a in tb.actions()) if c]
            if fila:
                secciones_ext.setdefault(titulo, []).append((titulo, fila))
        for titulo in sorted(secciones_ext, key=str.lower):
            self._secciones.append((titulo, secciones_ext[titulo], False))
        # 4) cualquier otra acción con texto (atajos sueltos)
        for act in win.findChildren(QAction):
            anadir(act, "IngeTrazo", "")
        self._lista.sort(key=lambda c: c.nombre.lower())
        self._hora = time.monotonic()
        return self._lista

    def _acciones_de(self, menu: QMenu) -> list:
        salida = []
        for act in menu.actions():
            sub = act.menu()
            if sub is not None:
                salida.extend(self._acciones_de(sub))
            else:
                salida.append(act)
        return salida

    def _rutas_menus(self) -> dict:
        rutas: dict = {}

        def recorrer(menu: QMenu, camino: list) -> None:
            for act in menu.actions():
                if act.isSeparator():
                    continue
                sub = act.menu()
                if sub is not None:
                    recorrer(sub, camino + [plano(sub.title())])
                elif plano(act.text()):
                    rutas.setdefault(id(act), SEP_RUTA.join(camino))

        for act in self.ventana.menuBar().actions():
            if act.menu() is not None:
                recorrer(act.menu(), [plano(act.menu().title())])
        return rutas

    # -- consulta
    def todos(self) -> list:
        if not self._lista:
            self.refrescar()
        return self._lista

    def secciones(self) -> list:
        """[(título, [(fila, [Comando…])…], es_nativa)…]"""
        if not self._secciones:
            self.refrescar()
        return self._secciones

    def comando(self, key: str) -> Comando | None:
        if key.startswith(PERSONAL) and self.extra is not None:
            return self.extra(key)
        c = self._indice.get(key)
        if c is not None and vivo(c.accion):
            return c
        if time.monotonic() - self._hora > 2.0:
            self.refrescar()
            c = self._indice.get(key)
            if c is not None and vivo(c.accion):
                return c
        return None

    def accion(self, key: str) -> QAction | None:
        c = self.comando(key)
        return c.accion if c is not None else None

    def nombre(self, key: str, defecto: str = "") -> str:
        c = self.comando(key)
        return c.nombre if c is not None else (defecto or key.split(":", 1)[-1])

    def icono(self, key: str, nombre: str = "") -> QIcon:
        """El icono de la acción o, si no tiene, uno con sus iniciales."""
        c = self.comando(key)
        if c is not None and vivo(c.accion) and not c.accion.icon().isNull():
            return c.accion.icon()
        nombre = nombre or self.nombre(key)
        guardado = self._iconos.get((key, nombre))
        if guardado is None:
            guardado = self._iconos[(key, nombre)] = _iconos.letras(nombre, key)
        return guardado

    def buscar(self, patron: str, maximo: int = 80) -> list:
        salida = []
        for c in self.todos():
            if coincide(patron, c.texto_busqueda()):
                salida.append(c)
                if len(salida) >= maximo:
                    break
        return salida
