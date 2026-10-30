# SPDX-License-Identifier: GPL-3.0-or-later
"""«List of Shortcuts» con editor, en el tema oscuro del gestor maestro:

- a la izquierda, solo los comandos con atajo (Atajo · Comando ·
  Asignado por), ordenables pulsando el encabezado; por tecla siguen
  ``orden_tecla``: letras solas, Ctrl+…, Alt+…, Shift+… y lo demás;
- en el centro, todos los comandos (los de IngeTrazo, los de cada
  extensión y los de Toolkeeper, con los comandos personales) por
  apartados plegables, con su tecla; buscar y «Solo con atajo»;
- a la derecha, un panel para cambiar la tecla de cualquier comando: su
  propio buscador, el atajo actual, la casilla donde se pulsan las teclas
  nuevas y la comprobación de si ya están asignadas y a quién; «Asignar»
  (se las quita al otro comando, para que no queden dos con la misma) y
  «Quitar atajo».

Los atajos se guardan donde IngeTrazo 0.5.8 guarda los suyos (QSettings
«IngeTrazo/IngeTrazo», grupo ``shortcuts``, clave = ``action_key`` con «/»
escrito «%2F»). IngeTrazo los aplica a sus comandos al arrancar; a los de
las extensiones, que llegan después, se los aplica Toolkeeper
(``aplicar_atajos_guardados``). Los de los comandos personales van en sus
propios datos.
"""
from __future__ import annotations

import logging
import re

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QHeaderView, QKeySequenceEdit, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget,
)

from ._catalogo import PREFIJO, clave, normalizar, plano, vivo
from ._i18n import _t
from ._maestro_dlg import (
    BARRAS, BORDE, ESTILO, EXTENSION, FONDO, NATIVOS, PERSONALES, TEXTO, TEXTO_SUAVE,
)

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

GRUPO = "shortcuts"
MAX_RESULTADOS = 12
TECLA = "#FAC775"

ESTILO_ATAJOS = ESTILO + f"""
QTreeWidget {{ background: {FONDO}; color: {TEXTO}; border: none; }}
QTreeWidget::item {{ padding: 1px 0; }}
QTreeWidget::item:selected {{ background: #0C447C; color: #E6F1FB; }}
QHeaderView::section {{ background: #262626; color: {TEXTO_SUAVE}; border: none;
            border-bottom: 1px solid #3a3a3a; padding: 3px 6px; }}
QListWidget {{ background: #2a2a2a; color: {TEXTO}; border: 1px solid {BORDE}; }}
QListWidget::item {{ padding: 2px 4px; }}
QListWidget::item:selected {{ background: #0C447C; color: #E6F1FB; }}
QKeySequenceEdit QLineEdit {{ border-color: #f37329; color: {TECLA}; font-family: Consolas, monospace; }}
QWidget#{PREFIJO}_con_atajo, QWidget#{PREFIJO}_con_atajo QTreeWidget {{ background: #1e1e1e; }}
QPushButton:checked {{ border-color: #f37329; color: {TECLA}; }}
"""

# Orden de los atajos (el que pidió el usuario):
#   1. letras solas: A, B, C…
#   2. Ctrl+…  3. Alt+…  4. Shift+…  (5. Meta+…), cada grupo por dentro:
#      primero los que llevan otra modificadora (Ctrl+Alt+…, Ctrl+Shift+…,
#      con la misma regla), luego números, letras, símbolos, el resto de
#      teclas con nombre y las teclas de función;
#   6. sin modificadoras y sin ser letra: teclas de función, números,
#      símbolos y el resto (Fin, Espacio…).
MODIFICADORAS = ("Ctrl", "Alt", "Shift", "Meta")
CLASE_CON_MOD = {"N": 0, "L": 1, "S": 2, "R": 3, "F": 4}
CLASE_SOLA = {"F": 0, "N": 1, "S": 2, "R": 3}


def _partes(texto: str) -> tuple:
    primera = texto.split(", ")[0]
    if primera.endswith("++"):
        tecla, base = "+", primera[:-2]
    else:
        trozos = primera.split("+")
        tecla, base = trozos[-1], "+".join(trozos[:-1])
    return primera, tecla, frozenset(m for m in base.split("+") if m)


def _clase(tecla: str) -> tuple:
    """(clase, valor): L letra, N número, F función, S símbolo, R el resto."""
    if len(tecla) == 1 and tecla.isalpha():
        return "L", tecla.upper()
    if len(tecla) == 1 and tecla.isdigit():
        return "N", tecla
    if re.fullmatch(r"F\d{1,2}", tecla):
        return "F", f"{int(tecla[1:]):02d}"
    if len(tecla) == 1:
        return "S", tecla
    return "R", tecla.lower()


def _orden(mods: frozenset, tecla: str) -> tuple:
    clase, valor = _clase(tecla)
    if not mods:
        if clase == "L":
            return (0, 0, valor)
        return (len(MODIFICADORAS) + 1, CLASE_SOLA[clase], valor)
    principal = next((i for i, m in enumerate(MODIFICADORAS) if m in mods), None)
    if principal is None:                   # modificadora rara (Num…): al final de todo
        return (len(MODIFICADORAS) + 2, 0, valor)
    resto = mods - {MODIFICADORAS[principal]}
    if resto:
        return (principal + 1, 0, _orden(resto, tecla))
    return (principal + 1, 1, (CLASE_CON_MOD[clase], valor))


def orden_tecla(texto: str) -> tuple:
    """Clave para ordenar atajos según la regla de arriba."""
    primera, tecla, mods = _partes(texto)
    return _orden(mods, tecla), primera


# ---- dónde guarda IngeTrazo los atajos ---------------------------------------------

def _ajustes() -> QSettings:
    return QSettings("IngeTrazo", "IngeTrazo")


def guardar_atajo(key: str, texto: str) -> None:
    s = _ajustes()
    s.beginGroup(GRUPO)
    s.setValue(key.replace("/", "%2F"), texto)
    s.endGroup()
    s.sync()


def atajos_guardados() -> dict:
    s = _ajustes()
    s.beginGroup(GRUPO)
    salida = {k.replace("%2F", "/"): str(s.value(k) or "") for k in s.childKeys()}
    s.endGroup()
    return salida


def aplicar_atajos_guardados(ventana) -> int:
    """Pone a cada acción de la ventana el atajo guardado para su clave
    (las de las extensiones nacen después de que IngeTrazo aplique los
    suyos). Devuelve cuántas cambió."""
    guardados = atajos_guardados()
    if not guardados:
        return 0
    n = 0
    for act in ventana.findChildren(QAction):
        if act.isSeparator() or act.menu() is not None:
            continue
        texto = guardados.get(clave(act))
        if texto is None:
            continue
        seq = QKeySequence(texto)
        if act.shortcut() != seq:
            act.setShortcut(seq)
            n += 1
    return n


# ---- los comandos -------------------------------------------------------------------

class _Entrada:
    """Un comando de la lista: su acción de Qt o, si es un comando personal,
    sus datos (cuya tecla vive en el JSON de Toolkeeper)."""

    __slots__ = ("key", "nombre", "ruta", "seccion", "accion", "personal")

    def __init__(self, key, nombre, ruta, seccion, accion, personal=None) -> None:
        self.key, self.nombre, self.ruta, self.seccion = key, nombre, ruta, seccion
        self.accion, self.personal = accion, personal

    def atajo(self) -> str:
        if self.personal is not None:
            return str(self.personal.get("atajo") or "")
        if self.accion is None or not vivo(self.accion):
            return ""
        return self.accion.shortcut().toString(QKeySequence.PortableText)

    def usa(self, seq: QKeySequence) -> bool:
        if seq.isEmpty():
            return False
        if self.personal is not None:
            return QKeySequence(self.atajo()) == seq
        return self.accion is not None and vivo(self.accion) and seq in self.accion.shortcuts()

    def donde(self) -> str:
        return f"{self.seccion} · {self.ruta}" if self.ruta and self.ruta != self.seccion else self.seccion


class _ItemAtajo(QTreeWidgetItem):
    """Fila del panel «Con atajo»: cada columna ordena con su propia clave
    (la tecla con ``orden_tecla``; comando y origen, desempatando por tecla)."""

    def __init__(self, textos: list, claves: tuple) -> None:
        super().__init__(textos)
        self.claves = claves

    def __lt__(self, otro) -> bool:
        arbol = self.treeWidget()
        col = arbol.sortColumn() if arbol is not None else 0
        try:
            return self.claves[col] < otro.claves[col]
        except (AttributeError, IndexError, TypeError):
            return super().__lt__(otro)


def _colores(seccion: str) -> tuple:
    if seccion == "IngeTrazo":
        return NATIVOS
    if seccion == _t("Toolkeeper"):
        return PERSONALES
    return EXTENSION


class DialogoAtajos(QDialog):
    def __init__(self, maestro) -> None:
        super().__init__(maestro.app.window)
        self.m = maestro
        self.setObjectName(PREFIJO + "_dlg_atajos")
        self.setWindowTitle(_t("List of Shortcuts"))
        self.setStyleSheet(ESTILO_ATAJOS)
        self.resize(1280, 660)
        self._entradas: list = []
        self._actual: _Entrada | None = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        barra = QWidget()
        barra.setObjectName(PREFIJO + "_cabecera")
        barra.setAttribute(Qt.WA_StyledBackground, True)
        fila = QHBoxLayout(barra)
        fila.setContentsMargins(8, 6, 8, 6)
        fila.setSpacing(6)
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText(_t("Search…"))
        self.filtro.setClearButtonEnabled(True)
        self.filtro.textChanged.connect(lambda _t_: self._filtrar_centro())
        fila.addWidget(self.filtro, 1)
        self.solo = QCheckBox(_t("Only with shortcut"))
        self.solo.toggled.connect(lambda _v: self._filtrar_centro())
        fila.addWidget(self.solo)
        imprimir = QPushButton("🖶 " + _t("Print"))
        imprimir.setAutoDefault(False)
        imprimir.clicked.connect(self._imprimir)
        fila.addWidget(imprimir)
        hecho = QPushButton(_t("Done"))
        hecho.setAutoDefault(False)
        hecho.clicked.connect(self.accept)
        fila.addWidget(hecho)
        lay.addWidget(barra)

        division = QSplitter(Qt.Horizontal)
        division.setChildrenCollapsible(False)
        division.setHandleWidth(3)
        division.addWidget(self._panel_con_atajo())
        self.arbol = QTreeWidget()
        self.arbol.setHeaderLabels([_t("Shortcut"), _t("Command"), _t("Menu")])
        self.arbol.setRootIsDecorated(True)
        self.arbol.setUniformRowHeights(True)
        self.arbol.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.arbol.setColumnWidth(0, 130)
        self.arbol.setColumnWidth(2, 200)
        self.arbol.currentItemChanged.connect(self._item_elegido)
        division.addWidget(self.arbol)
        division.addWidget(self._panel())
        division.setStretchFactor(0, 0)
        division.setStretchFactor(1, 1)
        division.setStretchFactor(2, 0)
        division.setSizes([340, 1200 - 340 - 300, 300])
        lay.addWidget(division, 1)

        self.estado = QLabel(_t("Choose a command from the list or the search box to change its shortcut"))
        self.estado.setObjectName(PREFIJO + "_estado")
        lay.addWidget(self.estado)
        self._cargar()
        self.rellenar()
        self._mostrar(None)

    # -- panel izquierdo: solo los comandos con atajo
    def _panel_con_atajo(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName(PREFIJO + "_con_atajo")
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setMinimumWidth(180)
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        self.titulo_izq = QLabel()
        self.titulo_izq.setStyleSheet(f"background: {BARRAS[0]}; color: {BARRAS[1]}; font-weight: bold; padding: 4px 8px;")
        v.addWidget(self.titulo_izq)
        self.izq = QTreeWidget()
        self.izq.setHeaderLabels([_t("Shortcut"), _t("Command"), _t("Assigned by")])
        self.izq.setRootIsDecorated(False)
        self.izq.setUniformRowHeights(True)
        self.izq.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.izq.header().setSectionsClickable(True)
        self.izq.header().setToolTip(_t("Click a column title to sort; click again to reverse"))
        self.izq.setColumnWidth(0, 120)
        self.izq.setColumnWidth(2, 118)
        self.izq.setSortingEnabled(True)
        self.izq.sortByColumn(0, Qt.AscendingOrder)
        self.izq.currentItemChanged.connect(self._item_elegido)
        v.addWidget(self.izq, 1)
        return panel

    def _rellenar_izquierda(self) -> None:
        self.izq.blockSignals(True)
        self.izq.setSortingEnabled(False)   # se ordena una vez, al final
        self.izq.clear()
        n = 0
        for i, e in enumerate(self._entradas):
            tecla = e.atajo()
            if not tecla:
                continue
            n += 1
            orden = orden_tecla(tecla)
            it = _ItemAtajo([tecla, e.nombre, e.seccion],
                            (orden, (e.nombre.lower(), orden), (e.seccion.lower(), orden)))
            it.setData(0, Qt.UserRole, i)
            it.setForeground(0, QColor(TECLA))
            it.setForeground(2, QColor(TEXTO_SUAVE))
            it.setToolTip(1, e.donde())
            it.setToolTip(2, e.donde())
            self.izq.addTopLevelItem(it)
        self.izq.setSortingEnabled(True)    # con la columna y el sentido que eligió el usuario
        self.izq.blockSignals(False)
        self.titulo_izq.setText(_t("With shortcut ({n})", n=n))

    # -- panel derecho
    def _panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName(PREFIJO + "_lateral")
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setMinimumWidth(260)
        v = QVBoxLayout(panel)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(4)
        v.addWidget(self._rotulo(_t("Command")))
        self.busca = QLineEdit()
        self.busca.setPlaceholderText(_t("Search a command…"))
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self._buscar)
        self.busca.returnPressed.connect(self._primer_resultado)
        v.addWidget(self.busca)
        self.resultados = QListWidget()
        self.resultados.setMaximumHeight(230)
        self.resultados.itemClicked.connect(self._resultado_elegido)
        self.resultados.itemActivated.connect(self._resultado_elegido)
        self.resultados.hide()
        v.addWidget(self.resultados)
        v.addSpacing(8)
        cab = QHBoxLayout()
        self.icono = QLabel()
        self.icono.setFixedSize(28, 28)
        cab.addWidget(self.icono)
        datos = QVBoxLayout()
        datos.setSpacing(0)
        self.nombre = QLabel()
        self.nombre.setWordWrap(True)
        datos.addWidget(self.nombre)
        self.ruta = QLabel()
        self.ruta.setWordWrap(True)
        self.ruta.setStyleSheet(f"color: {TEXTO_SUAVE}; font-size: 11px;")
        datos.addWidget(self.ruta)
        cab.addLayout(datos, 1)
        v.addLayout(cab)
        v.addWidget(self._rotulo(_t("Current shortcut")))
        self.actual = QLabel()
        self.actual.setStyleSheet(f"color: {TECLA}; font-family: Consolas, monospace; font-size: 14px;")
        v.addWidget(self.actual)
        v.addWidget(self._rotulo(_t("New shortcut (press the keys)")))
        self.tecla = QKeySequenceEdit()
        for metodo, valor in (("setMaximumSequenceLength", 1), ("setClearButtonEnabled", True)):
            try:
                getattr(self.tecla, metodo)(valor)          # Qt 6.4 / 6.5 en adelante
            except AttributeError:
                pass
        self.tecla.keySequenceChanged.connect(self._tecla_cambiada)
        v.addWidget(self.tecla)
        self.aviso = QLabel()
        self.aviso.setWordWrap(True)
        self.aviso.hide()
        v.addWidget(self.aviso)
        botones = QHBoxLayout()
        self.asignar = QPushButton(_t("Assign"))
        self.asignar.setAutoDefault(False)
        self.asignar.setStyleSheet("border-color: #f37329;")
        self.asignar.clicked.connect(self._asignar)
        botones.addWidget(self.asignar)
        self.quitar = QPushButton(_t("Remove shortcut"))
        self.quitar.setAutoDefault(False)
        self.quitar.clicked.connect(self._quitar)
        botones.addWidget(self.quitar)
        v.addSpacing(6)
        v.addLayout(botones)
        nota = QLabel(_t("Saved where IngeTrazo keeps its shortcuts; applied at once, also to extension commands."))
        nota.setWordWrap(True)
        nota.setStyleSheet(f"color: {TEXTO_SUAVE}; font-size: 11px; padding-top: 10px;")
        v.addWidget(nota)
        v.addStretch(1)
        return panel

    @staticmethod
    def _rotulo(texto: str) -> QLabel:
        e = QLabel(texto)
        e.setStyleSheet(f"color: {TEXTO_SUAVE}; font-size: 11px; padding-top: 6px;")
        return e

    # -- datos
    def _cargar(self) -> None:
        m, win = self.m, self.m.app.window
        m.catalogo.refrescar()
        salida, vistas = [], set()
        for c in m.catalogo.todos():
            if c.accion is None or not vivo(c.accion) or id(c.accion) in vistas:
                continue
            vistas.add(id(c.accion))
            seccion = "IngeTrazo" if c.origen == "IngeTrazo" else (
                _t("Extensions") if c.origen == "Extensions" else c.origen)
            salida.append(_Entrada(c.key, c.nombre, c.ruta or c.origen, seccion, c.accion))
        propio = _t("Toolkeeper")
        for act in win.findChildren(QAction):
            nombre = act.objectName()
            if not nombre.startswith(PREFIJO + ".") or nombre.startswith(PREFIJO + ".personal."):
                continue
            if act.isSeparator() or not plano(act.text()):
                continue
            salida.append(_Entrada(clave(act), plano(act.text()), propio, propio, act))
        for c in m.almacen.personales:
            act = win.findChild(QAction, f"{PREFIJO}.personal.{c['id']}")
            salida.append(_Entrada(m.personales.key(c), c["nombre"], _t("Personal"), propio, act, c))
        orden = {"IngeTrazo": 0, propio: 2}
        salida.sort(key=lambda e: (orden.get(e.seccion, 1), e.seccion.lower(), e.nombre.lower()))
        self._entradas = salida

    def _duenos(self, seq: QKeySequence, excepto: _Entrada | None) -> list:
        """Quién usa ya ``seq``: los comandos de la lista y, por si acaso,
        cualquier otra acción de la ventana."""
        duenos = [e for e in self._entradas if e is not excepto and e.usa(seq)]
        conocidas = {id(e.accion) for e in self._entradas if e.accion is not None}
        for act in self.m.app.window.findChildren(QAction):
            if id(act) in conocidas or act.isSeparator() or seq not in act.shortcuts():
                continue
            duenos.append(_Entrada(clave(act), plano(act.text()) or act.objectName() or "?", "",
                                   _t("Other"), act))
        return duenos

    # -- listas
    def rellenar(self) -> None:
        self._rellenar_centro()
        self._rellenar_izquierda()
        self._marcar(self._actual)

    def _marcar(self, e: _Entrada | None) -> None:
        """Deja señalado ``e`` en las dos listas (sin disparar su elección)."""
        i = None if e is None else next((n for n, x in enumerate(self._entradas) if x is e), None)
        for arbol in (self.arbol, self.izq):
            arbol.blockSignals(True)
            arbol.setCurrentItem(None)
            if i is not None:
                for it in self._items(arbol):
                    if it.data(0, Qt.UserRole) == i:
                        arbol.setCurrentItem(it)
                        arbol.scrollToItem(it)
                        break
            arbol.blockSignals(False)

    @staticmethod
    def _items(arbol: QTreeWidget):
        for n in range(arbol.topLevelItemCount()):
            arriba = arbol.topLevelItem(n)
            yield arriba
            for k in range(arriba.childCount()):
                yield arriba.child(k)

    def _filtrar_centro(self) -> None:
        self._rellenar_centro()
        self._marcar(self._actual)

    def _rellenar_centro(self) -> None:
        texto = normalizar(self.filtro.text().strip())
        solo = self.solo.isChecked()
        self.arbol.blockSignals(True)
        self.arbol.clear()
        secciones: dict = {}
        for i, e in enumerate(self._entradas):
            tecla = e.atajo()
            if solo and not tecla:
                continue
            if texto and texto not in normalizar(f"{tecla} {e.nombre} {e.ruta} {e.seccion}"):
                continue
            padre = secciones.get(e.seccion)
            if padre is None:
                padre = QTreeWidgetItem([e.seccion])
                fondo, tinta = _colores(e.seccion)
                for col in range(3):
                    padre.setBackground(col, QColor(fondo))
                    padre.setForeground(col, QColor(tinta))
                f = padre.font(0)
                f.setBold(True)
                padre.setFont(0, f)
                padre.setFlags(Qt.ItemIsEnabled)
                self.arbol.addTopLevelItem(padre)
                padre.setFirstColumnSpanned(True)   # solo tiene efecto ya dentro del árbol
                secciones[e.seccion] = padre
            it = QTreeWidgetItem([tecla, e.nombre, e.ruta])
            it.setData(0, Qt.UserRole, i)
            it.setForeground(0, QColor(TECLA))
            it.setForeground(2, QColor(TEXTO_SUAVE))
            padre.addChild(it)
        for padre in secciones.values():
            padre.setText(0, f"{padre.text(0).split('  (')[0]}  ({padre.childCount()})")
        self.arbol.expandAll()
        self.arbol.blockSignals(False)

    def _item_elegido(self, item, _previo=None) -> None:
        if item is None:
            return
        i = item.data(0, Qt.UserRole)
        if i is not None:
            e = self._entradas[int(i)]
            self._mostrar(e)
            self._marcar(e)

    # -- buscador del panel
    def _buscar(self, texto: str) -> None:
        self.resultados.clear()
        texto = normalizar(texto.strip())
        if not texto:
            self.resultados.hide()
            return
        n = 0
        for i, e in enumerate(self._entradas):
            if texto not in normalizar(f"{e.nombre} {e.ruta} {e.seccion}"):
                continue
            tecla = e.atajo()
            it = QListWidgetItem(f"{e.nombre}  ·  {e.seccion}" + (f"   [{tecla}]" if tecla else ""))
            it.setData(Qt.UserRole, i)
            it.setToolTip(e.donde())
            if e.accion is not None and vivo(e.accion) and not e.accion.icon().isNull():
                it.setIcon(e.accion.icon())
            elif e.personal is not None:
                it.setIcon(self.m.personales.icono(e.personal))
            self.resultados.addItem(it)
            n += 1
            if n >= MAX_RESULTADOS:
                break
        if n == 0:
            vacio = QListWidgetItem(_t("(no matches)"))
            vacio.setFlags(Qt.NoItemFlags)
            self.resultados.addItem(vacio)
        self.resultados.show()

    def _primer_resultado(self) -> None:
        if self.resultados.count() and self.resultados.item(0).data(Qt.UserRole) is not None:
            self._resultado_elegido(self.resultados.item(0))

    def _resultado_elegido(self, item) -> None:
        i = item.data(Qt.UserRole)
        if i is None:
            return
        self._mostrar(self._entradas[int(i)])
        self.resultados.hide()
        self.busca.blockSignals(True)
        self.busca.clear()
        self.busca.blockSignals(False)
        self._marcar(self._actual)          # deja marcado el comando en las listas
        self.tecla.setFocus()

    # -- comando elegido
    def _mostrar(self, e: _Entrada | None) -> None:
        self._actual = e
        hay = e is not None
        for w in (self.tecla, self.asignar, self.quitar):
            w.setEnabled(hay)
        self.tecla.clear()
        self.aviso.hide()
        if not hay:
            self.icono.clear()
            self.nombre.setText(f"<i style='color:{TEXTO_SUAVE}'>{_t('Choose a command first')}</i>")
            self.ruta.setText("")
            self.actual.setText("")
            return
        icono = None
        if e.personal is not None:
            icono = self.m.personales.icono(e.personal)
        elif e.accion is not None and vivo(e.accion) and not e.accion.icon().isNull():
            icono = e.accion.icon()
        self.icono.setPixmap(icono.pixmap(28, 28) if icono is not None else self.m.iconos["gestor"].pixmap(28, 28))
        self.nombre.setText(f"<b style='color:#E6F1FB'>{e.nombre}</b>")
        self.ruta.setText(e.donde())
        self.actual.setText(e.atajo() or f"<i style='color:{TEXTO_SUAVE}; font-family: sans-serif; font-size: 12px'>"
                                         f"{_t('(none)')}</i>")
        self.quitar.setEnabled(bool(e.atajo()))

    def _tecla_cambiada(self, seq: QKeySequence) -> None:
        if seq.count() > 1:                 # sin setMaximumSequenceLength: solo la primera
            primera = seq.toString(QKeySequence.PortableText).split(", ")[0]
            self.tecla.setKeySequence(QKeySequence(primera))
            return
        self._comprobar()

    def _comprobar(self) -> list:
        """Pinta si la tecla está libre o a quién pertenece; devuelve los dueños."""
        seq, e = self.tecla.keySequence(), self._actual
        if seq.isEmpty() or e is None:
            self.aviso.hide()
            return []
        teclas = seq.toString(QKeySequence.PortableText)
        if e.usa(seq):
            self._aviso(_t("It is already its shortcut."), libre=True)
            return []
        duenos = self._duenos(seq, e)
        if duenos:
            d = duenos[0]
            texto = _t("{keys} is already assigned to «{name}» ({where}). Assigning it will remove it from there.",
                       keys=teclas, name=d.nombre, where=d.donde())
            if len(duenos) > 1:
                texto += " " + _t("(and {n} more)", n=len(duenos) - 1)
            self._aviso(texto, libre=False)
        else:
            self._aviso(_t("{keys} is free.", keys=teclas), libre=True)
        return duenos

    def _aviso(self, texto: str, libre: bool) -> None:
        if libre:
            estilo = "border: 1px solid #3B6D11; background: #173404; color: #C0DD97;"
        else:
            estilo = "border: 1px solid #854F0B; background: #412402; color: #FAC775;"
        self.aviso.setStyleSheet(estilo + " border-radius: 4px; padding: 6px 8px; font-size: 11px;")
        self.aviso.setText(texto)
        self.aviso.show()

    # -- cambiar
    def _poner(self, e: _Entrada, texto: str) -> bool:
        if e.personal is not None:
            e.personal["atajo"] = texto
            self.m.almacen.guardar()
            self.m.personales._atajo(e.personal)
            e.accion = self.m.app.window.findChild(QAction, f"{PREFIJO}.personal.{e.personal['id']}")
            return True
        if e.accion is None or not vivo(e.accion):
            return False
        e.accion.setShortcut(QKeySequence(texto))
        guardar_atajo(e.key, texto)
        return True

    def _asignar(self) -> None:
        e, seq = self._actual, self.tecla.keySequence()
        if e is None:
            self.estado.setText(_t("Choose a command first"))
            return
        if seq.isEmpty():
            self.estado.setText(_t("Press the new keys first"))
            return
        if e.usa(seq):
            return
        teclas = seq.toString(QKeySequence.PortableText)
        for d in self._duenos(seq, e):      # nadie más con esa tecla: Qt no dispararía ninguno
            self._poner(d, "")
        if not self._poner(e, teclas):
            self.estado.setText(_t("This command cannot take a shortcut now."))
            return
        self.estado.setText(_t("Shortcut {keys} assigned to «{name}».", keys=teclas, name=e.nombre))
        self._despues()

    def _quitar(self) -> None:
        e = self._actual
        if e is None or not e.atajo():
            return
        if self._poner(e, ""):
            self.estado.setText(_t("Shortcut removed from «{name}».", name=e.nombre))
            self._despues()

    def _despues(self) -> None:
        e = self._actual
        self._mostrar(e)
        self.rellenar()

    # -- imprimir
    def html(self) -> str:
        partes = [f"<h2>{_t('List of Shortcuts')}</h2><table border='1' cellspacing='0' cellpadding='3'>"]
        actual = None
        for e in self._entradas:
            tecla = e.atajo()
            if not tecla:
                continue
            if e.seccion != actual:
                partes.append(f"<tr><th colspan='3' style='background:#1a237e;color:white'>{e.seccion}</th></tr>")
                actual = e.seccion
            partes.append(f"<tr><td><b>{tecla}</b></td><td>{e.nombre}</td><td>{e.ruta}</td></tr>")
        partes.append("</table>")
        return "".join(partes)

    def _imprimir(self) -> None:
        from ._parametros import imprimir_html
        imprimir_html(self, self.html())
