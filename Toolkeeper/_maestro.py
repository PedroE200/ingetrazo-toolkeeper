# SPDX-License-Identifier: GPL-3.0-or-later
"""Une las piezas de Toolkeeper: almacén, catálogo, comandos
personales, barras personalizadas, la barra y el menú propios, y los
diálogos que quedan (gestor de barras, atajos, ayuda)."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox, QToolBar

from . import _iconos
from ._barras import BarrasPersonalizadas, ESPERA_MS, crear_barra, tamano_icono, vaciar
from ._catalogo import PREFIJO, Catalogo, de_maestro, origen_ingles, plano, tr_app
from ._conjuntos import Conjuntos
from ._datos import COPIA, Almacen, EXT_CONFIG
from ._estados import Estados
from ._i18n import IDIOMAS, _t, idioma_elegido, poner_idioma
from ._parametros import DEFECTOS
from ._personales import Personales, TIPOS
from ._voz import pedir_texto

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

ATAJOS = {"atajos": "Ctrl+Alt+Shift+5"}
# Textos originales (en inglés) de la orden de IngeTrazo 0.5.8 que abre el gestor de extensiones.
GESTOR_EXTENSIONES = ("Manage extensions", "Extension manager")
# El dragón azul: icono del gestor de barras (barra, menú y ventana).
ICONO_GESTOR = Path(__file__).with_name("icono_gestor.png")


class _VigiaTema(QObject):
    def __init__(self, maestro) -> None:
        super().__init__(maestro.app.window)
        self.m = maestro
        self._pronto = QTimer(self)
        self._pronto.setSingleShot(True)
        self._pronto.setInterval(150)
        self._pronto.timeout.connect(maestro.redibujar_iconos)

    def eventFilter(self, obj, ev) -> bool:
        if ev.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
            self._pronto.start()
        return False


class Maestro:
    def __init__(self, app) -> None:
        self.app = app
        self.saliendo = False
        self.almacen = Almacen(parametros_defecto=DEFECTOS)
        self.catalogo = Catalogo(app.window)
        self.personales = Personales(self)
        self.catalogo.extra = self.personales.comando
        self.iconos: dict = {}
        self.acciones: dict = {}
        self._textos: dict = {}             # aid → (texto, consejo) en inglés, para traducir
        self._master = None
        self.redibujar_iconos(solo_dibujar=True)
        self.barras = BarrasPersonalizadas(self)
        self.estados = Estados(self)
        self.conjuntos = Conjuntos(self)

    # ---- instalación ----------------------------------------------------------
    def instalar(self) -> None:
        self._crear_acciones()
        self._crear_barra_propia()
        self._crear_menu()
        self.personales.instalar_atajos()
        QTimer.singleShot(ESPERA_MS, self._tras_arranque)
        QApplication.instance().aboutToQuit.connect(self._al_salir)

    def _tras_arranque(self) -> None:
        """Con todas las extensiones ya cargadas: sus comandos existen."""
        self.catalogo.refrescar()
        self.barras.construir_todas()
        try:                                # atajos personalizados de los comandos de extensiones
            from ._atajos import aplicar_atajos_guardados
            aplicar_atajos_guardados(self.app.window)
        except Exception:  # noqa: BLE001
            log.exception("atajos guardados no aplicados")
        self._vigia = _VigiaTema(self)
        self.app.window.installEventFilter(self._vigia)
        try:                                # colocación de barras que dejó un conjunto
            self.conjuntos.tras_arranque()
        except Exception:  # noqa: BLE001
            log.exception("colocación pendiente de un conjunto")
        try:
            self.almacen.hacer_backup()
        except Exception:  # noqa: BLE001
            log.exception("copia de seguridad automática")

    def _al_salir(self) -> None:
        self.saliendo = True
        self.almacen.guardar()

    # ---- iconos / tema --------------------------------------------------------
    def tinta(self):
        return self.app.window.palette().windowText().color()

    def redibujar_iconos(self, solo_dibujar: bool = False) -> None:
        tinta = self.tinta()
        self.iconos["gestor"] = _iconos.gestor(tinta)
        dragon = QIcon(str(ICONO_GESTOR)) if ICONO_GESTOR.is_file() else QIcon()
        self.iconos["dragon"] = self.iconos["gestor"] if dragon.isNull() else dragon
        for tipo in TIPOS:
            self.iconos["personal_" + tipo] = _iconos.tipo_personal(tipo, tinta)
        self.personales._iconos.clear()
        if solo_dibujar:
            return
        for aid, act in self.acciones.items():
            act.setIcon(self._icono_accion(aid))

    def _icono_accion(self, aid: str) -> QIcon:
        return self.iconos["dragon" if aid == "master" else "gestor"]

    @property
    def tamano_icono(self) -> int:
        return tamano_icono()

    # ---- comandos -------------------------------------------------------------
    def p(self, clave_p: str, defecto=None):
        return self.almacen.p(clave_p, defecto)

    # ---- destinos de otras extensiones --------------------------------------
    # Otra extensión (Rosco) se apunta en ``window._maestro_destinos`` con
    # un objeto que da ``prefijo``, ``titulo``, ``secciones()`` (sus botones
    # para el árbol), ``nombre(key)``, ``icono(key)``, ``descripcion(key)``,
    # ``ejecutar(key)`` y ``crear_panel(maestro, padre)`` (su apartado del
    # lateral, que acepta lo que se arrastra desde el árbol).
    def destinos(self) -> list:
        lista = getattr(self.app.window, "_maestro_destinos", None)
        return [d for d in lista if getattr(d, "prefijo", "")] if isinstance(lista, list) else []

    def destino_de(self, key: str):
        return next((d for d in self.destinos() if key.startswith(d.prefijo)), None)

    def comando(self, key: str):
        d = self.destino_de(key)
        if d is not None:
            from ._catalogo import Comando
            return Comando(key, d.nombre(key), f"{d.titulo} ▸ {key[len(d.prefijo):]}", None,
                           origen=d.titulo, descripcion=d.descripcion(key),
                           run=lambda k=key, dd=d: dd.ejecutar(k))
        return self.catalogo.comando(key)

    def nombre(self, key: str) -> str:
        d = self.destino_de(key)
        if d is not None:
            return d.nombre(key)
        return self.catalogo.nombre(key)

    def icono(self, key: str) -> QIcon:
        d = self.destino_de(key)
        if d is not None:
            return d.icono(key)
        c = self.personales.de_key(key)
        if c is not None:
            return self.personales.icono(c)
        if self.comando(key) is None:
            return _iconos.letras(self.nombre(key), key, disponible=False)
        return self.catalogo.icono(key, self.nombre(key))

    def ejecutar(self, key: str, origen: str = "") -> bool:
        d = self.destino_de(key)
        if d is not None:                   # botón de otra extensión: ella sabe qué hacer
            d.ejecutar(key)
            return True
        if origen == "master" and self._master is not None and self._master.isVisible() \
                and self.p("cerrar_master_al_ejecutar", True):
            self._master.hide()
        c = self.comando(key)
        if c is None or not c.disponible():
            self.app.viewport.flash_status(_t("«{name}» is not available now.", name=self.nombre(key)), 3000)
            return False
        if c.run is not None:
            QTimer.singleShot(0, c.run)
            return True
        QTimer.singleShot(0, c.accion.trigger)
        return True

    def barra_por_titulo(self, titulo: str) -> QToolBar | None:
        for tb in self.app.window.findChildren(QToolBar):
            if tb.parent() is self.app.window and tb.windowTitle() == titulo \
                    and not tb.objectName().startswith(PREFIJO):
                return tb
        return None

    def atajo_ocupado(self, atajo: str, excepto=None) -> bool:
        seq = QKeySequence(atajo)
        if seq.isEmpty():
            return False
        return any(a is not excepto and a.shortcut() == seq for a in self.app.window.findChildren(QAction))

    # ---- acciones, barra y menú propios ---------------------------------------
    def _accion(self, aid: str, texto: str, consejo: str, al_pulsar, atajo: str | None = None) -> QAction:
        """``texto`` y ``consejo`` van en inglés: se traducen aquí y otra vez
        al cambiar de idioma (``_poner_textos``)."""
        win = self.app.window
        act = QAction(self._icono_accion(aid), "", win)
        act.setObjectName(f"{PREFIJO}.{aid}")
        act.triggered.connect(lambda _c=False: al_pulsar())
        if atajo and not self.atajo_ocupado(atajo):
            act.setShortcut(QKeySequence(atajo))
        self.acciones[aid] = act
        self._textos[aid] = (texto, consejo)
        self._poner_textos(aid)
        win.addAction(act)
        return act

    def _poner_textos(self, aid: str) -> None:
        act = self.acciones[aid]
        texto, consejo = (_t(s) if s else "" for s in self._textos[aid])
        atajo = act.shortcut().toString(QKeySequence.NativeText)
        act.setText(texto)
        cabeza = f"{texto} ({atajo})" if atajo else texto
        act.setToolTip(f"{cabeza}\n{consejo}" if consejo else cabeza)
        act.setStatusTip(consejo)

    def _crear_acciones(self) -> None:
        A = self._accion
        A("master", "Toolbar Manager", "Manage all toolbars loaded in IngeTrazo", self.abrir_master)
        A("backup", "Backup config", "Make a backup copy of the configuration now", self.backup_manual)
        A("importar", "Import config", "Import custom toolbars and personal commands from a file or a backup",
          self.importar_archivo)
        A("exportar", "Export config", "Export custom toolbars and personal commands to a file", self.exportar)
        A("atajos", "List of all shortcuts", "", self.abrir_atajos, ATAJOS["atajos"])
        A("ayuda", "Help", "", self.abrir_ayuda)

    def _crear_barra_propia(self) -> None:
        self.tb_propia = crear_barra(self.app, PREFIJO + "_principal", str(self.p("nombre_barra", "Toolkeeper")))
        self._rellenar_barra_propia()

    def _rellenar_barra_propia(self) -> None:
        tb = self.tb_propia
        vaciar(tb)
        tb.setWindowTitle(str(self.p("nombre_barra", "Toolkeeper")))
        for aid in self.p("iconos_barra", []) or []:
            if aid in self.acciones:
                tb.addAction(self.acciones[aid])

    def _crear_menu(self) -> None:
        menu = self.app.add_menu(_t("Toolkeeper"))
        if menu is None:
            return
        if not menu.objectName():
            menu.setObjectName(PREFIJO + "_menu")
        a = self.acciones
        menu.addAction(a["master"])
        menu.addSeparator()
        menu.addAction(a["backup"])
        sub = menu.addMenu(_t("Import config"))
        sub.setObjectName(PREFIJO + "_menu_importar")
        sub.aboutToShow.connect(lambda: self.menu_importar(sub))
        menu.addAction(a["exportar"])
        menu.addSeparator()
        estados = menu.addMenu(_t("Toolbar states"))
        estados.setObjectName(PREFIJO + "_menu_estados")
        estados.aboutToShow.connect(lambda: self.estados.menu(estados))
        conjuntos = menu.addMenu("🧩 " + _t("Extension sets"))
        conjuntos.setObjectName(PREFIJO + "_menu_conjuntos")
        conjuntos.aboutToShow.connect(lambda: self.conjuntos.menu(conjuntos))
        menu.addSeparator()
        menu.addAction(a["atajos"])
        idioma = menu.addMenu(_t("Language"))
        idioma.setObjectName(PREFIJO + "_menu_idioma")
        idioma.aboutToShow.connect(lambda: self.menu_idioma(idioma))
        menu.addAction(a["ayuda"])
        self.menu = menu
        self._menu_importar = sub
        self._menu_idioma = idioma
        self._menu_estados = estados
        self._menu_conjuntos = conjuntos

    def menu_idioma(self, menu: QMenu) -> None:
        """Automático / Español / English / Français, con el elegido marcado."""
        menu.clear()
        grupo = QActionGroup(menu)
        elegido = idioma_elegido()
        for codigo, nombre in (("", _t("Automatic (as IngeTrazo)")), *IDIOMAS.items()):
            act = menu.addAction(nombre, lambda c=codigo: self.cambiar_idioma(c))
            act.setCheckable(True)
            act.setChecked(codigo == elegido)
            grupo.addAction(act)
            if not codigo:
                menu.addSeparator()

    def cambiar_idioma(self, codigo: str) -> None:
        """Cambia el idioma de la extensión al momento: menú, botones de la
        barra, barras personalizadas y el gestor de barras (se rehace)."""
        if codigo == idioma_elegido():
            return
        poner_idioma(codigo)
        for aid in self.acciones:
            self._poner_textos(aid)
        if getattr(self, "menu", None) is not None:
            self.menu.setTitle(_t("Toolkeeper"))
            self._menu_importar.setTitle(_t("Import config"))
            self._menu_idioma.setTitle(_t("Language"))
            self._menu_estados.setTitle(_t("Toolbar states"))
            self._menu_conjuntos.setTitle("🧩 " + _t("Extension sets"))
        self.barras.construir_todas()
        self.conjuntos.idioma_cambiado()
        if self._master is not None:
            visible = self._master.isVisible()
            sitio = self._master.saveGeometry()
            self._master.close()
            self._master.deleteLater()
            self._master = None
            if visible:                     # vuelve a abrirse donde estaba, ya traducido
                QTimer.singleShot(0, lambda: (self.abrir_master(),
                                              self._master and self._master.restoreGeometry(sitio)))

    def menu_importar(self, menu: QMenu) -> None:
        menu.clear()
        menu.addAction(_t("Import from a config file…"), self.importar_archivo)
        copias = self.almacen.backups()
        if copias:
            sub = menu.addMenu(_t("Restore a backup"))
            for f in copias[:20]:
                sub.addAction(f.stem.replace(COPIA, ""), lambda r=f: self.importar_backup(r))
        else:
            menu.addAction(_t("(no backups yet)")).setEnabled(False)

    # ---- cambios --------------------------------------------------------------
    def todo_cambiado(self) -> None:
        self.catalogo.refrescar()
        self.barras.construir_todas()
        if self._master is not None and self._master.isVisible():
            self._master.rellenar()

    def barras_cambiadas(self) -> None:
        """Una barra personalizada ganó, perdió o cambió algo: el lateral del
        gestor de barras se rehace (después, por si el aviso llega desde un
        widget del propio lateral, p. ej. al soltar un icono en él)."""
        if self._master is not None and self._master.isVisible():
            QTimer.singleShot(0, self._master.refrescar_lateral)

    def parametros_cambiados(self) -> None:
        self._rellenar_barra_propia()
        self.todo_cambiado()

    # ---- diálogos -------------------------------------------------------------
    def abrir_master(self) -> None:
        try:
            if self._master is None:
                from ._maestro_dlg import GestorMaestro
                self._master = GestorMaestro(self)
            self._master.abrir()
        except Exception as err:  # noqa: BLE001 — que el fallo se vea en vez de no abrir nada
            log.exception("el gestor de barras no se pudo abrir")
            self.app.viewport.flash_status(_t("The Toolbar Manager could not open: {err}", err=err), 8000)

    def abrir_atajos(self) -> None:
        try:
            from ._atajos import DialogoAtajos
            DialogoAtajos(self).exec()
        except Exception as err:  # noqa: BLE001 — que el fallo se vea en vez de no abrir nada
            log.exception("la lista de atajos no se pudo abrir")
            self.app.viewport.flash_status(_t("The list of shortcuts could not open: {err}", err=err), 8000)

    def abrir_ayuda(self) -> None:
        from ._ayuda import DialogoAyuda
        DialogoAyuda(self).exec()

    def abrir_gestor_extensiones(self) -> None:
        """Dispara la orden «Manage extensions…» de IngeTrazo, buscada por su
        texto original en inglés (o el traducido) para no depender del idioma."""
        textos = set(GESTOR_EXTENSIONES) | {plano(tr_app(t)) for t in GESTOR_EXTENSIONES}
        for act in self.app.window.findChildren(QAction):
            if act.isSeparator() or act.menu() is not None or de_maestro(act):
                continue
            if plano(act.text()) in textos or plano(origen_ingles(act.text())) in textos:
                if act.isEnabled():
                    QTimer.singleShot(0, act.trigger)
                    return
        self.app.viewport.flash_status(_t("The IngeTrazo extension manager was not found."), 3000)

    # -- barras personalizadas
    def nueva_barra_dialogo(self, items=None) -> dict | None:
        nombre, ok = pedir_texto(self.app.window, _t("Name of the custom toolbar"),
                                 _t("Name of the custom toolbar"),
                                 _t("Toolbar {n}", n=len(self.almacen.barras) + 1))
        nombre = (nombre or "").strip()
        if not ok or not nombre:
            return None
        if any(b["nombre"] == nombre for b in self.almacen.barras):
            QMessageBox.warning(self.app.window, _t("Toolkeeper"), _t("That name is already used."))
            return None
        b = self.barras.nueva(nombre, items)
        self.barras_cambiadas()
        return b

    def renombrar_barra_dialogo(self, bid: str) -> None:
        b = self.almacen.barra(bid)
        if b is None:
            return
        nombre, ok = pedir_texto(self.app.window, _t("Rename the custom toolbar"), _t("Name of the custom toolbar"),
                                 b["nombre"])
        if ok and nombre.strip():
            self.renombrar_barra(bid, nombre)

    def renombrar_barra(self, bid: str, nombre: str) -> bool:
        """Cambia el nombre de una barra personalizada si no lo usa otra."""
        nombre = (nombre or "").strip()
        b = self.almacen.barra(bid)
        if b is None or not nombre or nombre == b["nombre"]:
            return False
        if any(o["nombre"] == nombre and o["id"] != bid for o in self.almacen.barras):
            self.app.viewport.flash_status(_t("That name is already used."), 3000)
            return False
        self.barras.renombrar(bid, nombre)
        self.barras_cambiadas()
        return True

    def borrar_barra_dialogo(self, bid: str) -> None:
        b = self.almacen.barra(bid)
        if b is None:
            return
        if QMessageBox.question(self.app.window, _t("Toolkeeper"),
                                _t("Delete the custom toolbar «{name}»?", name=b["nombre"])) == QMessageBox.Yes:
            self.barras.borrar(bid)
            self.barras_cambiadas()

    # -- comandos personales
    def nuevo_personal_dialogo(self, tipo: str) -> dict | None:
        from ._personales import DialogoPersonal
        dlg = DialogoPersonal(self, tipo)
        if not dlg.exec():
            return None
        c = self.personales.nuevo(dlg.datos)
        self.todo_cambiado()
        return c

    def editar_personal_dialogo(self, cid: str) -> None:
        from ._personales import DialogoPersonal
        c = self.almacen.personal(cid)
        if c is None:
            return
        dlg = DialogoPersonal(self, c["tipo"], c)
        if dlg.exec():
            self.personales.guardar(c)

    def borrar_personal_dialogo(self, cid: str) -> None:
        c = self.almacen.personal(cid)
        if c is None:
            return
        if QMessageBox.question(self.app.window, _t("Toolkeeper"),
                                _t("Delete the personal command «{name}»?", name=c["nombre"])) == QMessageBox.Yes:
            self.personales.borrar(cid)

    # -- copias, importar, exportar
    def exportar(self) -> None:
        ruta, _f = QFileDialog.getSaveFileName(self.app.window, _t("Export config to file (extension will be {ext})", ext=EXT_CONFIG),
                                               "configuracion" + EXT_CONFIG, f"Toolkeeper (*{EXT_CONFIG})")
        if not ruta:
            return
        if not ruta.endswith(EXT_CONFIG):
            ruta += EXT_CONFIG
        try:
            self.almacen.exportar(ruta)
            self.app.viewport.flash_status(_t("Exported to {path}", path=ruta), 4000)
        except OSError as err:
            QMessageBox.critical(self.app.window, _t("Toolkeeper"), str(err))

    def importar_archivo(self) -> None:
        ruta, _f = QFileDialog.getOpenFileName(self.app.window, _t("Import config"), "",
                                               f"Toolkeeper (*{EXT_CONFIG} *.json)")
        if ruta:
            self._importar(ruta)

    def importar_backup(self, ruta) -> None:
        self._importar(ruta)

    def _importar(self, ruta) -> None:
        caja = QMessageBox(QMessageBox.Question, _t("Toolkeeper"),
                           _t("Merge the file with your current data, or replace everything?"), parent=self.app.window)
        combinar = caja.addButton(_t("Merge"), QMessageBox.AcceptRole)
        reemplazar = caja.addButton(_t("Replace"), QMessageBox.DestructiveRole)
        caja.addButton(QMessageBox.Cancel)
        caja.exec()
        if caja.clickedButton() not in (combinar, reemplazar):
            return
        try:
            self.almacen.hacer_backup(forzar=True)
            self.almacen.importar(ruta, combinar=caja.clickedButton() is combinar)
        except (OSError, ValueError) as err:
            QMessageBox.critical(self.app.window, _t("Toolkeeper"), str(err))
            return
        self.personales.instalar_atajos()
        self.parametros_cambiados()

    def backup_manual(self) -> None:
        ruta = self.almacen.hacer_backup(forzar=True)
        if ruta is not None:
            self.app.viewport.flash_status(_t("Backup saved: {path}", path=str(ruta)), 4000)
