# SPDX-License-Identifier: GPL-3.0-or-later
"""El gestor de barras, siempre en tema oscuro:

- cabecera: Filtro (con los filtros recientes), Plegar / Desplegar todo,
  Atajos (la lista de todos los atajos), Extensiones (el gestor de
  extensiones de IngeTrazo y conjuntos de extensiones), Estados, Idioma, ayuda, importar, exportar, imprimir;
- a la izquierda, un árbol de apartados plegables (se recuerda cuáles se
  dejaron plegados): «Comandos nativos de IngeTrazo» con una fila por barra
  nativa (y por menú), y una sección por extensión, con una fila por barra
  o submenú y una casilla para mostrar u ocultar la barra;
- en el lateral derecho, también plegables: los paneles de otras
  extensiones (Barra Rosco), «Barras personalizadas» con el tirador de
  separador y «Crear barra personalizada…» (cada barra con casilla,
  renombrar, borrar y sus iconos), y debajo «Comandos personales» con
  [Nuevo…] y una fila por tipo;
- línea de estado con el comando señalado.

Cada icono: clic ejecuta (y cierra el gestor); arrastrar lo lleva a una
barra personalizada. Mientras se filtra, los apartados con coincidencias
se despliegan solos.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, QTimer
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QCheckBox, QCompleter, QDialog, QFrame, QHBoxLayout, QLabel, QLayout, QLineEdit, QMenu,
    QPushButton, QScrollArea, QSizePolicy, QSplitter, QToolButton, QVBoxLayout, QWidget,
)

from ._boton import BotonComando, datos_arrastre, leer_arrastre
from ._catalogo import PREFIJO, coincide, vivo
from ._datos import SEPARADOR
from ._i18n import _t, idioma_elegido
from ._personales import TIPOS, etiqueta_tipo
from ._voz import con_microfono

# Tema oscuro: (fondo de la cabecera, texto) de cada clase de apartado.
FONDO, FONDO_CAB, FONDO_HONDO, TEXTO, TEXTO_SUAVE, BORDE = \
    "#232323", "#2a2a2a", "#1b1b1b", "#D3D1C7", "#888780", "#4a4a48"
PERSONALES = ("#633806", "#FAC775")
NATIVOS = ("#791F1F", "#F7C1C1")
EXTENSION = ("#0C447C", "#B5D4F4")
BARRAS = ("#27500A", "#C0DD97")
DESTINO = ("#3C3489", "#CECBF6")        # apartados de otras extensiones (Rosco)
FONDO_LATERAL, FONDO_BARRAS, BORDE_LATERAL = "#1e1e1e", "#1f2a1a", "#2f3d27"
ANCHO_LATERAL = 300
ETIQUETA_ARBOL = 150            # ancho del nombre de cada fila del árbol

ESTILO = f"""
QDialog {{ background: {FONDO}; color: {TEXTO}; }}
QWidget#{PREFIJO}_cabecera {{ background: {FONDO_CAB}; border-bottom: 1px solid #3a3a3a; }}
QLabel {{ color: {TEXTO}; background: transparent; }}
QCheckBox {{ color: {TEXTO}; background: transparent; }}
QLineEdit {{ background: {FONDO_HONDO}; color: {TEXTO}; border: 1px solid {BORDE};
            border-radius: 4px; padding: 2px 6px; selection-background-color: #f37329; }}
QPushButton, QToolButton#{PREFIJO}_boton {{ background: #333333; color: {TEXTO};
            border: 1px solid {BORDE}; border-radius: 4px; padding: 3px 9px; }}
QPushButton:hover, QToolButton#{PREFIJO}_boton:hover {{ border-color: #f37329; }}
QPushButton:pressed, QToolButton#{PREFIJO}_boton:pressed {{ background: #3d3d3d; }}
QToolButton#{PREFIJO}_boton::menu-indicator {{ image: none; width: 0; }}
QScrollArea {{ border: none; background: {FONDO}; }}
QWidget#{PREFIJO}_arbol {{ background: {FONDO}; }}
QWidget#{PREFIJO}_lateral {{ background: {FONDO_LATERAL}; }}
QSplitter::handle {{ background: #3a3a3a; }}
QScrollBar:vertical {{ background: {FONDO_HONDO}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {BORDE}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
QMenu {{ background: {FONDO_CAB}; color: {TEXTO}; border: 1px solid {BORDE}; }}
QMenu::item {{ padding: 4px 18px; }}
QMenu::item:selected {{ background: #3a3a3a; }}
QMenu::item:disabled {{ color: {TEXTO_SUAVE}; }}
QLabel#{PREFIJO}_estado {{ background: {FONDO_HONDO}; color: {TEXTO_SUAVE}; font-style: italic;
            font-size: 11px; padding: 3px 6px; border-top: 1px solid #3a3a3a; }}
"""


class FlowLayout(QLayout):
    """Iconos en fila que saltan de línea (el ejemplo clásico de Qt)."""

    def __init__(self, parent=None, margen=2, espacio=2) -> None:
        super().__init__(parent)
        self._items: list = []
        self._espacio = espacio
        self.setContentsMargins(margen, margen, margen, margen)

    def addItem(self, item) -> None:
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, i):
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i):
        return self._items.pop(i) if 0 <= i < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, w: int) -> int:
        return self._colocar(QRect(0, 0, w, 0), True)

    def setGeometry(self, r) -> None:
        super().setGeometry(r)
        self._colocar(r, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        s = QSize()
        for it in self._items:
            s = s.expandedTo(it.minimumSize())
        m = self.contentsMargins()
        return s + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _colocar(self, r, solo_altura: bool) -> int:
        m = self.contentsMargins()
        x, y, alto = r.x() + m.left(), r.y() + m.top(), 0
        derecha = r.right() - m.right()
        for it in self._items:
            w = it.widget()
            if w is not None and w.isHidden():
                continue
            s = it.sizeHint()
            if x + s.width() > derecha and alto > 0:
                x, y, alto = r.x() + m.left(), y + alto + self._espacio, 0
            if not solo_altura:
                it.setGeometry(QRect(QPoint(x, y), s))
            x += s.width() + self._espacio
            alto = max(alto, s.height())
        return y + alto + m.bottom() - r.y()


class _Tirador(QLabel):
    """«Click and Drag to insert a separator in a custom toolbar»."""

    def __init__(self, parent=None) -> None:
        super().__init__("|", parent)
        self.setFixedSize(18, 20)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #97C459; color: #EAF3DE; background: transparent; font-weight: bold;")
        self.setToolTip(_t("Click and Drag to insert a separator in a custom toolbar"))
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton:
            drag = QDrag(self)
            drag.setMimeData(datos_arrastre(SEPARADOR, "master", -1))
            drag.exec(Qt.CopyAction)


class _FilaBarra(QWidget):
    """Una barra personalizada en el lateral: acepta iconos soltados."""

    def __init__(self, dialogo, bid: str) -> None:
        super().__init__()
        self.d, self.bid = dialogo, bid
        self.setAcceptDrops(True)

    def dragEnterEvent(self, ev) -> None:
        if leer_arrastre(ev.mimeData()) is not None:
            ev.acceptProposedAction()

    def dropEvent(self, ev) -> None:
        info = leer_arrastre(ev.mimeData())
        if info is None:
            return
        self.d.m.barras.anadir_item(self.bid, info["key"])
        ev.acceptProposedAction()


class _NombreBarra(QWidget):
    """Nombre de una barra personalizada: un clic lo vuelve editable ahí
    mismo; Intro o clic fuera guardan, Esc cancela."""

    def __init__(self, maestro, bid: str, nombre: str) -> None:
        super().__init__()
        self.m, self.bid, self.nombre = maestro, bid, nombre
        self._terminando = False
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        self.rotulo = QLabel(nombre)
        self.rotulo.setObjectName("nombre_barra")
        self.rotulo.setToolTip(_t("Click to rename the custom toolbar"))
        self.rotulo.setCursor(Qt.IBeamCursor)
        self.rotulo.setAttribute(Qt.WA_Hover, True)
        self.rotulo.setStyleSheet(
            f"QLabel#nombre_barra {{ font-style: italic; color: {BARRAS[1]}; padding: 1px 4px;"
            " border: 1px solid transparent; border-radius: 3px; }"
            " QLabel#nombre_barra:hover { border-color: #639922; background: #27361f; }")
        h.addWidget(self.rotulo, 1)
        self.edicion = con_microfono(QLineEdit(nombre))
        self.edicion.setStyleSheet("QLineEdit { background: #1b1b1b; color: #EAF3DE; border: 1px solid #f37329;"
                                   " border-radius: 3px; padding: 1px 4px; }")
        self.edicion.editingFinished.connect(self._guardar)
        self.edicion.hide()
        h.addWidget(self.edicion, 1)
        # Los filtros, con los dos widgets ya creados: Qt manda eventos en
        # cuanto se colocan, y el filtro mira ``self.edicion``.
        self.rotulo.installEventFilter(self)
        self.edicion.installEventFilter(self)

    def eventFilter(self, obj, ev) -> bool:
        if obj is self.rotulo and ev.type() == QEvent.MouseButtonRelease and ev.button() == Qt.LeftButton:
            self._editar()
            return True
        if obj is self.edicion and ev.type() == QEvent.KeyPress:
            if ev.key() == Qt.Key_Escape:
                self.edicion.setText(self.nombre)
                self._terminar()
                return True
            if ev.key() in (Qt.Key_Return, Qt.Key_Enter):    # que no llegue al botón por defecto del diálogo
                self._guardar()
                return True
        return super().eventFilter(obj, ev)

    def _editar(self) -> None:
        self._terminando = False
        self.edicion.setText(self.nombre)
        self.rotulo.hide()
        self.edicion.show()
        self.edicion.setFocus()
        self.edicion.selectAll()

    def _guardar(self) -> None:
        if self._terminando or self.edicion.isHidden():
            return
        texto = self.edicion.text().strip()
        if self.m.renombrar_barra(self.bid, texto):
            self.nombre = texto
            self.rotulo.setText(texto)
        self._terminar()

    def _terminar(self) -> None:
        self._terminando = True
        self.edicion.hide()
        self.rotulo.show()


class _Cabecera(QWidget):
    """Cabecera de un apartado del árbol: flecha, título y número de
    comandos; un clic pliega o despliega el apartado."""

    def __init__(self, seccion, titulo: str, colores: tuple, n: int) -> None:
        super().__init__()
        self.seccion = seccion
        self.setObjectName("cabecera_seccion")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"QWidget#cabecera_seccion {{ background: {colores[0]}; border-bottom: 1px solid #141414; }}")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(_t("Click to collapse or expand"))
        h = QHBoxLayout(self)
        h.setContentsMargins(6, 3, 6, 3)
        h.setSpacing(6)
        self.flecha = QLabel()
        self.flecha.setFixedWidth(12)
        self.flecha.setStyleSheet(f"color: {colores[1]}; background: transparent;")
        h.addWidget(self.flecha)
        e = QLabel(f"<b style='color:{colores[1]}'>{titulo}</b> "
                   f"<span style='color:{colores[1]}'>({n})</span>")
        h.addWidget(e)
        self.extra = h                       # para añadir botones (New…)

    def mouseReleaseEvent(self, ev) -> None:
        if ev.button() == Qt.LeftButton and self.rect().contains(ev.position().toPoint()):
            self.seccion.alternar()
            return
        super().mouseReleaseEvent(ev)


class _Seccion(QWidget):
    """Apartado plegable del árbol: cabecera + cuerpo con las filas."""

    def __init__(self, dialogo, clave: str, titulo: str, colores: tuple, n: int, fijo: bool = False) -> None:
        super().__init__()
        self.d, self.clave = dialogo, clave
        self.fijo = fijo                     # no se esconde al filtrar (barras: reciben iconos)
        self.lateral = False                 # está en el lateral derecho
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        self.cabecera = _Cabecera(self, titulo, colores, n)
        v.addWidget(self.cabecera)
        self.cuerpo = QWidget()
        self.filas = QVBoxLayout(self.cuerpo)
        self.filas.setContentsMargins(0, 0, 0, 0)
        self.filas.setSpacing(0)
        v.addWidget(self.cuerpo)
        self.abierta = clave not in dialogo.m.almacen.plegados
        self.mostrar(self.abierta)

    def anadir(self, fila: QWidget) -> None:
        self.filas.addWidget(fila)

    def mostrar(self, abierta: bool) -> None:
        self.cuerpo.setVisible(abierta)
        self.cabecera.flecha.setText("▾" if abierta else "▸")

    def poner(self, abierta: bool) -> None:
        self.abierta = abierta
        self.mostrar(abierta)

    def alternar(self) -> None:
        self.poner(not self.abierta)
        self.d.plegado_cambiado()


class GestorMaestro(QDialog):
    def __init__(self, maestro) -> None:
        super().__init__(maestro.app.window)
        self.m = maestro
        self.setObjectName(PREFIJO + "_dlg_master")
        self.setWindowTitle(_t("Toolkeeper"))
        self.setWindowIcon(maestro.iconos["dragon"])
        self.setStyleSheet(ESTILO)
        self.resize(1000, 700)
        self._botones: list = []
        self._secciones: list = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        barra = QWidget()
        barra.setObjectName(PREFIJO + "_cabecera")
        barra.setAttribute(Qt.WA_StyledBackground, True)
        cab = QHBoxLayout(barra)
        cab.setContentsMargins(8, 6, 8, 6)
        cab.setSpacing(6)
        cab.addWidget(QLabel(f"<b>{_t('Filter')}</b>"))
        self.filtro = con_microfono(QLineEdit())
        self.filtro.setClearButtonEnabled(True)
        self.filtro.textChanged.connect(lambda _t_: self._filtrar())
        self.filtro.editingFinished.connect(lambda: maestro.almacen.recordar_filtro(self.filtro.text()))
        self._completador()
        cab.addWidget(self.filtro, 1)
        recientes = self._boton("▼", _t("Recent filters"))
        recientes.setPopupMode(QToolButton.InstantPopup)
        menu_rec = QMenu(recientes)
        menu_rec.aboutToShow.connect(lambda: self._menu_recientes(menu_rec))
        recientes.setMenu(menu_rec)
        cab.addWidget(recientes)
        cab.addSpacing(10)
        self.todo = self._boton("", "", self._alternar_todo)
        cab.addWidget(self.todo)
        cab.addWidget(self._boton("⌨ " + _t("Shortcuts"), _t("Open the list of all shortcuts"), maestro.abrir_atajos))
        # Extensiones: el gestor de extensiones de IngeTrazo y los conjuntos de extensiones.
        extensiones = self._boton("🧩 " + _t("Extensions") + " ▾",
                                  _t("Open the IngeTrazo extension manager or save and bring back which "
                                     "extensions are on and off"))
        extensiones.setPopupMode(QToolButton.InstantPopup)
        menu_ext = QMenu(extensiones)
        menu_ext.aboutToShow.connect(lambda: maestro.conjuntos.menu(menu_ext, con_gestor=True))
        extensiones.setMenu(menu_ext)
        cab.addWidget(extensiones)
        # Estados: el mismo submenú que el del menú de la extensión.
        estados = self._boton(_t("States") + " ▾", _t("Save and bring back the layout of toolbars and panels"))
        estados.setPopupMode(QToolButton.InstantPopup)
        menu_estados = QMenu(estados)
        menu_estados.aboutToShow.connect(lambda: maestro.estados.menu(menu_estados))
        estados.setMenu(menu_estados)
        cab.addWidget(estados)
        # Idioma: el mismo submenú que Extensiones ▸ Toolkeeper ▸ Idioma;
        # al cambiarlo, el Maestro rehace esta ventana.
        idioma = self._boton(f"🌐 {(idioma_elegido() or 'Auto').upper()} ▾", _t("Language of Toolkeeper"))
        idioma.setPopupMode(QToolButton.InstantPopup)
        menu_idioma = QMenu(idioma)
        menu_idioma.aboutToShow.connect(lambda: maestro.menu_idioma(menu_idioma))
        idioma.setMenu(menu_idioma)
        cab.addWidget(idioma)
        for texto, consejo, fn in (("?", _t("Help on Toolkeeper"), maestro.abrir_ayuda),
                                   ("⤓", _t("Import custom toolbars and personal commands from a file"),
                                    maestro.importar_archivo),
                                   ("⤒", _t("Export custom toolbars and personal commands to a file"),
                                    maestro.exportar),
                                   ("🖶", _t("Print"), self._imprimir)):
            cab.addWidget(self._boton(texto, consejo, fn))
        lay.addWidget(barra)

        division = QSplitter(Qt.Horizontal)
        division.setChildrenCollapsible(False)
        division.setHandleWidth(3)
        self.area = QScrollArea()
        self.area.setWidgetResizable(True)
        self.arbol = QWidget()
        self.arbol.setObjectName(PREFIJO + "_arbol")
        self.arbol.setAttribute(Qt.WA_StyledBackground, True)
        self.vlay = QVBoxLayout(self.arbol)
        self.vlay.setContentsMargins(0, 0, 0, 0)
        self.vlay.setSpacing(0)
        self.vlay.setAlignment(Qt.AlignTop)
        self.area.setWidget(self.arbol)
        division.addWidget(self.area)
        self.area_lateral = QScrollArea()
        self.area_lateral.setWidgetResizable(True)
        self.area_lateral.setMinimumWidth(220)
        self.lateral = QWidget()
        self.lateral.setObjectName(PREFIJO + "_lateral")
        self.lateral.setAttribute(Qt.WA_StyledBackground, True)
        self.llay = QVBoxLayout(self.lateral)
        self.llay.setContentsMargins(0, 0, 0, 0)
        self.llay.setSpacing(0)
        self.llay.setAlignment(Qt.AlignTop)
        self.area_lateral.setWidget(self.lateral)
        division.addWidget(self.area_lateral)
        division.setStretchFactor(0, 1)
        division.setStretchFactor(1, 0)
        division.setSizes([1000 - ANCHO_LATERAL, ANCHO_LATERAL])
        lay.addWidget(division, 1)

        self.estado = QLabel()
        self.estado.setObjectName(PREFIJO + "_estado")
        lay.addWidget(self.estado)
        self._estado_defecto()
        self.rellenar()

    # -- cabecera
    def _boton(self, texto: str, consejo: str, fn=None) -> QToolButton:
        b = QToolButton()
        b.setObjectName(PREFIJO + "_boton")
        b.setText(texto)
        b.setToolTip(consejo)
        if fn is not None:
            b.clicked.connect(lambda _c=False, f=fn: f())
        return b

    def _completador(self) -> None:
        self.filtro.setCompleter(QCompleter(self.m.almacen.filtros, self))

    def _menu_recientes(self, menu: QMenu) -> None:
        menu.clear()
        for f in self.m.almacen.filtros:
            menu.addAction(f, lambda t=f: self.filtro.setText(t))
        if not self.m.almacen.filtros:
            menu.addAction(_t("(no recent filters)")).setEnabled(False)

    def _estado_defecto(self) -> None:
        self.estado.setText(_t("Click on an icon to execute command - Click-Drag-Drop to add the icon to a custom toolbar"))

    # -- plegar
    def _alternar_todo(self) -> None:
        abrir = not any(s.abierta for s in self._secciones)
        for s in self._secciones:
            s.poner(abrir)
        self.plegado_cambiado()

    def plegado_cambiado(self) -> None:
        """Guarda qué apartados quedan plegados y pone el texto del botón."""
        if not self.filtro.text().strip():
            self.m.almacen.poner_plegados([s.clave for s in self._secciones if not s.abierta])
        self._texto_todo()

    def _texto_todo(self) -> None:
        if any(s.abierta for s in self._secciones):
            self.todo.setText("⊟ " + _t("Collapse all"))
            self.todo.setToolTip(_t("Collapse every section of the tree"))
        else:
            self.todo.setText("⊞ " + _t("Expand all"))
            self.todo.setToolTip(_t("Expand every section of the tree"))

    # -- cuerpo
    def rellenar(self) -> None:
        for lay in (self.vlay, self.llay):
            while lay.count():
                it = lay.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
        self._botones.clear()
        self._secciones.clear()
        self._completador()
        m = self.m
        # IngeTrazo y extensiones
        for titulo, filas, nativa in m.catalogo.secciones():
            n = sum(len(comandos) for _f, comandos in filas)
            sec = self._seccion("__nativos__" if nativa else titulo,
                                _t("IngeTrazo native commands") if nativa else titulo,
                                NATIVOS if nativa else EXTENSION, n)
            sec.cabecera.extra.addStretch(1)
            for nombre_fila, comandos in filas:
                tb = m.barra_por_titulo(nombre_fila)
                if tb is not None:
                    casilla = QCheckBox(nombre_fila)
                    casilla.setStyleSheet(f"font-style: italic; color: {TEXTO_SUAVE};")
                    casilla.setToolTip(_t("Click to toggle the visibility of the toolbar"))
                    casilla.setChecked(tb.isVisible())
                    casilla.toggled.connect(lambda v, t=tb: vivo(t) and t.setVisible(v))
                    etiqueta = casilla
                else:
                    etiqueta = QLabel(f"<span style='color:{'#F09595' if nativa else '#85B7EB'}'>{nombre_fila}</span>")
                sec.anadir(self._fila(etiqueta, [c.key for c in comandos]))
        # Los botones propios de otras extensiones (Rosco): se arrastran
        # a su apartado del lateral.
        for d in m.destinos():
            try:
                filas = d.secciones()
            except Exception:  # noqa: BLE001 — un destino roto no rompe el gestor
                continue
            sec = self._seccion("__destino_" + d.prefijo, d.titulo,
                                DESTINO, sum(len(keys) for _f, keys in filas))
            sec.cabecera.extra.addStretch(1)
            for nombre_fila, keys in filas:
                etiqueta = QLabel(f"<span style='color:{DESTINO[1]}'>{nombre_fila}</span>")
                sec.anadir(self._fila(etiqueta, keys))
        self._rellenar_lateral()
        self._texto_todo()
        self._filtrar()

    def _seccion(self, clave: str, titulo: str, colores: tuple, n: int, lateral: bool = False,
                 fijo: bool = False) -> _Seccion:
        sec = _Seccion(self, clave, titulo, colores, n, fijo)
        sec.lateral = lateral
        self._secciones.append(sec)
        (self.llay if lateral else self.vlay).addWidget(sec)
        return sec

    def refrescar_lateral(self) -> None:
        """Rehace solo el lateral (comandos personales y barras), sin tocar
        el árbol ni perder la posición del desplazamiento."""
        if not self.isVisible():
            return
        barra = self.area_lateral.verticalScrollBar()
        pos = barra.value()
        viejos = set(self.lateral.findChildren(BotonComando))
        self._botones = [b for b in self._botones if b not in viejos]
        self._secciones = [s for s in self._secciones if not s.lateral]
        while self.llay.count():
            it = self.llay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        self._rellenar_lateral()
        self._texto_todo()
        self._filtrar()
        QTimer.singleShot(0, lambda: barra.setValue(pos))

    def _rellenar_lateral(self) -> None:
        m = self.m
        # Lo que configuran otras extensiones (la Barra Rosco): reciben
        # lo que se arrastra desde el árbol.
        for d in m.destinos():
            try:
                n = int(d.n_huecos())
            except Exception:  # noqa: BLE001
                n = 0
            sec = self._seccion("__panel_" + d.prefijo, _t("{name} toolbar", name=d.titulo), DESTINO, n,
                                lateral=True, fijo=True)
            try:
                sec.anadir(d.crear_panel(m, sec.cuerpo))
            except Exception:  # noqa: BLE001
                import logging
                logging.getLogger("ingetrazo.plugins.igz_toolkeeper").exception(
                    "no se pudo crear el apartado de %s", d.titulo)
        self._lateral_barras(m)
        self._lateral_personales(m)

    def _lateral_barras(self, m) -> None:
        sec = self._seccion("__barras__", _t("Custom toolbars"), BARRAS, len(m.almacen.barras),
                            lateral=True, fijo=True)
        sec.cuerpo.setObjectName("cuerpo_barras")
        sec.cuerpo.setAttribute(Qt.WA_StyledBackground, True)
        sec.cuerpo.setStyleSheet(f"QWidget#cuerpo_barras {{ background: {FONDO_BARRAS}; }}")
        sec.cabecera.extra.addStretch(1)
        sec.cabecera.extra.addWidget(_Tirador())
        crear = QPushButton("+ " + _t("Create Custom toolbar…"))
        crear.setAutoDefault(False)
        crear.clicked.connect(lambda _c=False: m.nueva_barra_dialogo())
        caja = QWidget()
        cl = QHBoxLayout(caja)
        cl.setContentsMargins(8, 6, 8, 6)
        cl.addWidget(crear)
        sec.anadir(caja)
        px = max(16, min(28, m.tamano_icono))
        for b in m.almacen.barras:
            bid = b["id"]
            bloque = _FilaBarra(self, bid)
            bloque.setObjectName("barra_lateral")
            bloque.setAttribute(Qt.WA_StyledBackground, True)
            bloque.setStyleSheet(f"QWidget#barra_lateral {{ border-top: 1px solid {BORDE_LATERAL}; }}")
            v = QVBoxLayout(bloque)
            v.setContentsMargins(8, 4, 8, 4)
            v.setSpacing(2)
            fila = QHBoxLayout()
            fila.setSpacing(4)
            casilla = QCheckBox()
            casilla.setToolTip(_t("Click to toggle the visibility of the toolbar"))
            casilla.setChecked(m.barras.visible(bid))
            casilla.toggled.connect(lambda val, i=bid: m.barras.mostrar(i, val))
            fila.addWidget(casilla)
            fila.addWidget(_NombreBarra(m, bid, b["nombre"]), 1)
            borrar = QToolButton()
            borrar.setText("🗑")
            borrar.setAutoRaise(True)
            borrar.setStyleSheet(f"color: {BARRAS[1]}; background: transparent; border: none;")
            borrar.setToolTip(_t("Click to Delete the custom toolbar"))
            borrar.clicked.connect(lambda _c=False, i=bid: m.borrar_barra_dialogo(i))
            fila.addWidget(borrar)
            v.addLayout(fila)
            iconos = QWidget()
            fl = FlowLayout(iconos)
            fl.setContentsMargins(18, 2, 0, 2)
            for i, key in enumerate(b["items"]):
                if key == SEPARADOR:
                    sep = QFrame()
                    sep.setFixedSize(4, px + 8)
                    sep.setStyleSheet("background: #639922; border: none;")
                    fl.addWidget(sep)
                    continue
                bt = self._boton_comando(key, "barra:" + bid, i, px, iconos,
                                         lambda menu, boton, i=bid: m.barras.menu_item(menu, i, boton.key))
                fl.addWidget(bt)
            iconos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            v.addWidget(iconos)
            sec.anadir(bloque)
        pista = QLabel(_t("Drag icons from the tree here"))
        pista.setStyleSheet("color: #639922; font-size: 11px; padding: 8px;")
        pista.setWordWrap(True)
        sec.anadir(pista)

    def _lateral_personales(self, m) -> None:
        sec = self._seccion("__personales__", _t("Personal Commands"), PERSONALES, len(m.almacen.personales),
                            lateral=True)
        nuevo = self._boton(_t("New…"), "")
        nuevo.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(nuevo)
        for tipo in TIPOS:
            menu.addAction(m.iconos["personal_" + tipo], etiqueta_tipo(tipo),
                           lambda t=tipo: m.nuevo_personal_dialogo(t))
        nuevo.setMenu(menu)
        sec.cabecera.extra.addStretch(1)
        sec.cabecera.extra.addWidget(nuevo)
        for tipo in TIPOS:
            etiqueta = QLabel(f"<span style='color:#EF9F27'><b>{etiqueta_tipo(tipo)}</b></span>")
            sec.anadir(self._fila(etiqueta, [m.personales.key(c) for c in m.almacen.personales if c["tipo"] == tipo],
                                  contextual=self._menu_personal, sangria=12, encima=True))

    def _fila(self, etiqueta: QWidget, keys: list, contextual=None, ancho: int = ETIQUETA_ARBOL,
              sangria: int = 24, encima: bool = False) -> QWidget:
        """Un nombre y sus iconos: a la izquierda en una columna de ``ancho``
        o, con ``encima``, en su propia línea (no se corta) y los iconos debajo."""
        w = QWidget()
        w.setAttribute(Qt.WA_StyledBackground, True)
        w.setStyleSheet("QWidget#fila { border-bottom: 1px solid #2e2e2e; }")
        w.setObjectName("fila")
        if encima:
            h = QVBoxLayout(w)
            h.setContentsMargins(sangria, 3, 4, 3)
            h.setSpacing(1)
            h.addWidget(etiqueta)
        else:
            h = QHBoxLayout(w)
            h.setContentsMargins(sangria, 1, 4, 1)
            etiqueta.setMinimumWidth(ancho)
            etiqueta.setMaximumWidth(ancho)
            h.addWidget(etiqueta, 0, Qt.AlignTop)
        iconos = QWidget()
        fl = FlowLayout(iconos)
        if encima:
            fl.setContentsMargins(10, 0, 0, 0)
        px = max(16, min(28, self.m.tamano_icono))
        for i, key in enumerate(keys):
            if key == SEPARADOR:
                sep = QFrame()
                sep.setFrameShape(QFrame.VLine)
                sep.setFixedSize(6, px + 8)
                fl.addWidget(sep)
                continue
            fl.addWidget(self._boton_comando(key, "master", i, px, iconos, contextual))
        iconos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        h.addWidget(iconos, 1)
        w._fila = True
        return w

    def _boton_comando(self, key: str, origen: str, i: int, px: int, padre, contextual) -> BotonComando:
        b = BotonComando(self.m, key, origen, i, px, padre)
        b.installEventFilter(self)
        if contextual is not None:
            b.setContextMenuPolicy(Qt.CustomContextMenu)
            b.customContextMenuRequested.connect(
                lambda pos, bt=b, fn=contextual: self._menu(bt, pos, fn))
        self._botones.append(b)
        return b

    def _menu(self, boton, pos, fn) -> None:
        menu = QMenu(self)
        menu.setObjectName(PREFIJO + "_menu_master")
        fn(menu, boton)
        if not menu.isEmpty():
            menu.exec(boton.mapToGlobal(pos))

    def _menu_personal(self, menu: QMenu, boton: BotonComando) -> None:
        c = self.m.personales.de_key(boton.key)
        if c is None:
            return
        menu.addAction(_t("Run"), lambda: self.m.ejecutar(boton.key))
        menu.addAction(_t("Edit…"), lambda: self.m.editar_personal_dialogo(c["id"]))
        menu.addAction(_t("Delete"), lambda: self.m.borrar_personal_dialogo(c["id"]))
        sub = menu.addMenu(_t("Add to custom toolbar"))
        for b in self.m.almacen.barras:
            sub.addAction(b["nombre"], lambda i=b["id"]: self.m.barras.anadir_item(i, boton.key))
        if not self.m.almacen.barras:
            sub.addAction(_t("(no custom toolbars yet)")).setEnabled(False)

    # -- filtro y estado
    def _filtrar(self) -> None:
        patron = self.filtro.text().strip()
        for b in self._botones:
            if not vivo(b):
                continue
            c = self.m.comando(b.key)
            texto = c.texto_busqueda() if c else self.m.nombre(b.key)
            b.setVisible(not patron or coincide(patron, texto))
        for s in self._secciones:
            if s.fijo:
                s.mostrar(s.abierta)
                continue
            hay = False
            for i in range(s.filas.count()):
                w = s.filas.itemAt(i).widget()
                if w is None or not getattr(w, "_fila", False):
                    continue
                botones = w.findChildren(BotonComando)
                visible = not patron or any(b.isVisibleTo(w) for b in botones)
                w.setVisible(visible)
                hay = hay or (visible and bool(botones))
            # Filtrando: solo los apartados con coincidencias, desplegados.
            s.setVisible(not patron or hay)
            s.mostrar(hay if patron else s.abierta)

    def eventFilter(self, obj, ev) -> bool:
        if isinstance(obj, BotonComando):
            if ev.type() == QEvent.Enter:
                c = self.m.comando(obj.key)
                if c is not None:
                    self.estado.setText(f"<b style='color:#85B7EB'><i>{c.nombre}</i></b>: <i>{c.descripcion or c.ruta}</i>")
            elif ev.type() == QEvent.Leave:
                self._estado_defecto()
        return super().eventFilter(obj, ev)

    def _imprimir(self) -> None:
        from ._parametros import imprimir_html
        partes = [f"<h2>{_t('Toolkeeper')}</h2>"]
        for titulo, filas, nativa in self.m.catalogo.secciones():
            partes.append(f"<h3>{_t('IngeTrazo native commands') if nativa else titulo}</h3>")
            for nombre_fila, comandos in filas:
                partes.append(f"<p><b>{nombre_fila}</b>: " + ", ".join(c.nombre for c in comandos) + "</p>")
        imprimir_html(self, "".join(partes))

    def abrir(self) -> None:
        self.rellenar()
        self.show()
        self.raise_()
        self.activateWindow()
        self.filtro.setFocus()
