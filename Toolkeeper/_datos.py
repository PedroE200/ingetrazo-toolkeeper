# SPDX-License-Identifier: GPL-3.0-or-later
"""Dónde guarda Toolkeeper lo suyo: un JSON global en
``%APPDATA%\\IngeTrazo\\igz_toolkeeper\\igz_toolkeeper.json`` (fuera de la
carpeta del plugin para que reinstalarlo no lo borre) con:

- ``parametros``: los valores de serie (ver ``_parametros.DEFECTOS``);
- ``barras``: las barras personalizadas (QToolBar reales);
- ``personales``: los comandos personales (carpeta, web, menú, script, acceso directo);
- ``filtros``: últimos textos del filtro del gestor de barras;
- ``plegados``: apartados del gestor de barras que se dejaron plegados;
- ``estados``: colocaciones de barras y paneles guardadas con un nombre;
- ``conjuntos``: conjuntos de extensiones (activas / inactivas, y si se
  pide, la colocación de barras), ``conjunto_anterior`` (lo que había antes
  de aplicar uno) y ``colocacion_pendiente`` (la que se aplica al arrancar).

Las copias de seguridad (``backups/igz_toolkeeper_YYYYMMDD_HHMMSS.json``) se
hacen una vez por sesión o por día, y se purgan a los N días.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import QTimer

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")

VERSION_DATOS = 1
SEPARADOR = "|"           # separador entre iconos
PERSONAL = "personal:"    # comandos personales (clave = personal:<id>)
EXT_CONFIG = ".igz_toolkeeper.json"
COPIA = "igz_toolkeeper_"     # prefijo de las copias de seguridad


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def nuevo_id() -> str:
    return uuid.uuid4().hex[:8]


def carpeta_usuario_plugins() -> Path:
    try:
        from core.extensions import user_plugins_dir
        return Path(user_plugins_dir())
    except Exception:  # noqa: BLE001 — misma regla que IngeTrazo 0.5.8
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "IngeTrazo" / "plugins"


def carpeta_datos() -> Path:
    return carpeta_usuario_plugins().parent / "igz_toolkeeper"


def ruta_datos() -> Path:
    return carpeta_datos() / "igz_toolkeeper.json"


# ---- Modelos -------------------------------------------------------------------

def nueva_barra(nombre: str) -> dict:
    return {"id": nuevo_id(), "nombre": nombre, "visible": True, "items": []}


def nuevo_personal(tipo: str, nombre: str) -> dict:
    return {"id": nuevo_id(), "tipo": tipo, "nombre": nombre, "descripcion": "",
            "atajo": "", "color": "", "icono": "", "destino": ""}


def _valida_barra(b) -> dict | None:
    if not isinstance(b, dict) or not b.get("id"):
        return None
    base = nueva_barra(str(b.get("nombre") or "?"))
    base.update({k: b[k] for k in base if k in b})
    base["id"] = str(base["id"])
    base["items"] = [str(k) for k in (base["items"] or []) if k]
    return base


def _valida_estado(e) -> dict | None:
    if not isinstance(e, dict) or not e.get("nombre") or not isinstance(e.get("qt"), str):
        return None
    return {"nombre": str(e["nombre"]), "qt": e["qt"], "fecha": str(e.get("fecha") or "")}


def _ids(valor) -> list:
    return [str(i) for i in valor if isinstance(i, str) and i] if isinstance(valor, list) else []


def _valida_conjunto(c) -> dict | None:
    if not isinstance(c, dict) or not c.get("nombre"):
        return None
    activas, inactivas = _ids(c.get("activas")), _ids(c.get("inactivas"))
    if not activas and not inactivas:
        return None
    qt = c.get("qt") if isinstance(c.get("qt"), str) else ""
    return {"nombre": str(c["nombre"]), "fecha": str(c.get("fecha") or ""),
            "activas": activas, "inactivas": [i for i in inactivas if i not in activas], "qt": qt}


def _valida_anterior(a) -> dict:
    if not isinstance(a, dict):
        return {}
    limpio = {"activas": _ids(a.get("activas")), "inactivas": _ids(a.get("inactivas"))}
    if isinstance(a.get("qt"), str) and a["qt"]:
        limpio["qt"] = a["qt"]
    return limpio if limpio["activas"] or limpio["inactivas"] else {}


def _valida_personal(c) -> dict | None:
    if not isinstance(c, dict) or not c.get("id") or c.get("tipo") not in (
            "documento", "carpeta", "web", "menu", "script"):
        return None
    base = nuevo_personal(c["tipo"], str(c.get("nombre") or "?"))
    base.update({k: c[k] for k in base if k in c})
    base["id"] = str(base["id"])
    return base


# ---- Almacén -------------------------------------------------------------------

class Almacen:
    """El JSON global. Se lee una vez y se escribe entero (atómico); los
    cambios frecuentes (filtros, visibilidad) se agrupan con
    ``guardar_pronto``."""

    def __init__(self, ruta: Path | None = None, parametros_defecto: dict | None = None) -> None:
        self.ruta = ruta or ruta_datos()
        self.defecto = dict(parametros_defecto or {})
        self.datos = self._vacio()
        self._temporizador = QTimer()
        self._temporizador.setSingleShot(True)
        self._temporizador.setInterval(1500)
        self._temporizador.timeout.connect(self.guardar)
        self._leer()

    def _vacio(self) -> dict:
        return {"version": VERSION_DATOS, "parametros": dict(self.defecto),
                "barras": [], "personales": [], "filtros": [], "plegados": [], "estados": [],
                "conjuntos": [], "conjunto_anterior": {}, "colocacion_pendiente": "", "ultimo_backup": ""}

    # -- lectura / escritura
    def _leer(self) -> None:
        try:
            crudo = json.loads(self.ruta.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, ValueError):
            log.exception("igz_toolkeeper.json ilegible; se aparta y se empieza de cero")
            try:
                self.ruta.replace(self.ruta.with_suffix(".json.roto"))
            except OSError:
                pass
            return
        self.cargar(crudo)

    def cargar(self, crudo) -> None:
        """Toma ``crudo`` (dict leído de un JSON) validando cada parte; lo que
        no es de Toolkeeper se ignora."""
        self.datos = self._vacio()
        if not isinstance(crudo, dict):
            return
        for clave, defecto in self._vacio().items():
            valor = crudo.get(clave, defecto)
            if type(valor) is type(defecto):
                self.datos[clave] = valor
        self.datos["version"] = VERSION_DATOS
        # Sin diálogo de parámetros: siempre los de serie (un archivo
        # importado no cambia el nombre de la barra propia).
        self.datos["parametros"] = dict(self.defecto)
        self.datos["barras"] = [b for b in map(_valida_barra, self.datos["barras"]) if b]
        self.datos["personales"] = [c for c in map(_valida_personal, self.datos["personales"]) if c]
        self.datos["filtros"] = [str(f) for f in self.datos["filtros"]][:12]
        self.datos["plegados"] = [str(s) for s in self.datos["plegados"]][:200]
        self.datos["estados"] = [e for e in map(_valida_estado, self.datos["estados"]) if e]
        self.datos["conjuntos"] = [c for c in map(_valida_conjunto, self.datos["conjuntos"]) if c]
        self.datos["conjunto_anterior"] = _valida_anterior(self.datos["conjunto_anterior"])

    def volcado(self) -> dict:
        return json.loads(json.dumps(self.datos, ensure_ascii=False))

    def guardar(self) -> None:
        self._temporizador.stop()
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.ruta.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(self.volcado(), ensure_ascii=False, indent=1),
                           encoding="utf-8")
            os.replace(tmp, self.ruta)
        except OSError:
            log.exception("no se pudo guardar %s", self.ruta)

    def guardar_pronto(self) -> None:
        self._temporizador.start()

    # -- parámetros
    @property
    def parametros(self) -> dict:
        return self.datos["parametros"]

    def p(self, clave, defecto=None):
        return self.parametros.get(clave, self.defecto.get(clave, defecto))

    # -- barras personalizadas
    @property
    def barras(self) -> list:
        return self.datos["barras"]

    def barra(self, bid: str) -> dict | None:
        return next((b for b in self.barras if b["id"] == bid), None)

    # -- comandos personales
    @property
    def personales(self) -> list:
        return self.datos["personales"]

    def personal(self, cid: str) -> dict | None:
        return next((c for c in self.personales if c["id"] == cid), None)

    # -- filtros
    @property
    def filtros(self) -> list:
        return self.datos["filtros"]

    def recordar_filtro(self, texto: str) -> None:
        texto = (texto or "").strip()
        if not texto:
            return
        if texto in self.filtros:
            self.filtros.remove(texto)
        self.filtros.insert(0, texto)
        del self.filtros[12:]
        self.guardar_pronto()

    # -- apartados plegados del gestor de barras
    @property
    def plegados(self) -> list:
        return self.datos["plegados"]

    def poner_plegados(self, claves) -> None:
        self.datos["plegados"] = [str(c) for c in claves][:200]
        self.guardar_pronto()

    # -- estados de las barras
    @property
    def estados(self) -> list:
        return self.datos["estados"]

    def estado(self, nombre: str) -> dict | None:
        clave = nombre.casefold()
        return next((e for e in self.estados if e["nombre"].casefold() == clave), None)

    def poner_estado(self, nombre: str, qt: str) -> None:
        e = self.estado(nombre)
        if e is None:
            e = {"nombre": nombre}
            self.estados.append(e)
        e["qt"], e["fecha"] = qt, ahora()
        self.guardar()

    def borrar_estado(self, nombre: str) -> None:
        self.datos["estados"] = [e for e in self.estados if e["nombre"] != nombre]
        self.guardar()

    # -- conjuntos de extensiones
    @property
    def conjuntos(self) -> list:
        return self.datos["conjuntos"]

    def conjunto(self, nombre: str) -> dict | None:
        clave = (nombre or "").casefold()
        return next((c for c in self.conjuntos if c["nombre"].casefold() == clave), None)

    def poner_conjunto(self, nombre: str, estado: dict, qt: str = "") -> None:
        c = self.conjunto(nombre)
        if c is None:
            c = {"nombre": nombre}
            self.conjuntos.append(c)
        c["activas"] = sorted((i for i, v in estado.items() if v), key=str.casefold)
        c["inactivas"] = sorted((i for i, v in estado.items() if not v), key=str.casefold)
        c["qt"], c["fecha"] = qt or "", ahora()
        self.guardar()

    def renombrar_conjunto(self, nombre: str, nuevo: str) -> None:
        c = self.conjunto(nombre)
        if c is not None:
            c["nombre"] = nuevo
            self.guardar()

    def borrar_conjunto(self, nombre: str) -> None:
        self.datos["conjuntos"] = [c for c in self.conjuntos if c["nombre"] != nombre]
        self.guardar()

    def importar_conjuntos(self, crudo) -> list:
        """Añade los conjuntos de ``crudo`` (un archivo de conjuntos o una
        configuración completa) que no estén ya por nombre. Devuelve sus nombres."""
        lista = crudo.get("conjuntos") if isinstance(crudo, dict) else crudo
        if isinstance(crudo, dict) and lista is None and "nombre" in crudo:
            lista = [crudo]
        nuevos = []
        for c in map(_valida_conjunto, lista if isinstance(lista, list) else []):
            if c and self.conjunto(c["nombre"]) is None:
                self.conjuntos.append(c)
                nuevos.append(c["nombre"])
        if nuevos:
            self.guardar()
        return nuevos

    @property
    def conjunto_anterior(self) -> dict:
        return self.datos["conjunto_anterior"]

    def poner_anterior(self, anterior: dict) -> None:
        self.datos["conjunto_anterior"] = _valida_anterior(anterior)
        self.guardar()

    @property
    def colocacion_pendiente(self) -> str:
        return self.datos["colocacion_pendiente"]

    def poner_colocacion_pendiente(self, qt: str) -> None:
        self.datos["colocacion_pendiente"] = qt or ""
        self.guardar()

    # -- exportar / importar / copias
    def exportar(self, ruta) -> None:
        Path(ruta).write_text(json.dumps(self.volcado(), ensure_ascii=False, indent=1),
                              encoding="utf-8")

    def importar(self, ruta, combinar: bool) -> None:
        crudo = json.loads(Path(ruta).read_text(encoding="utf-8"))
        if not combinar:
            # Un archivo sin estados o sin conjuntos no borra los que hay; lo
            # pendiente de este PC (anterior, colocación) tampoco viaja.
            guardado = {k: self.datos[k] for k in ("estados", "conjuntos")}
            local = {k: self.datos[k] for k in ("conjunto_anterior", "colocacion_pendiente")}
            self.cargar(crudo)
            for k, v in guardado.items():
                if not isinstance(crudo, dict) or k not in crudo:
                    self.datos[k] = v
            self.datos.update(local)
            self.guardar()
            return
        otro = Almacen.__new__(Almacen)
        otro.defecto = self.defecto
        otro.datos = otro._vacio()
        Almacen.cargar(otro, crudo)
        for b in otro.barras:
            if self.barra(b["id"]) is not None:
                b["id"] = nuevo_id()
            self.barras.append(b)
        for c in otro.personales:
            if self.personal(c["id"]) is None:
                self.personales.append(c)
        for e in otro.estados:
            if self.estado(e["nombre"]) is None:
                self.estados.append(e)
        for c in otro.conjuntos:
            if self.conjunto(c["nombre"]) is None:
                self.conjuntos.append(c)
        self.guardar()

    def carpeta_backups(self) -> Path:
        return self.ruta.parent / "backups"

    def backups(self) -> list:
        try:
            archivos = sorted(self.carpeta_backups().glob(COPIA + "*.json"), reverse=True)
        except OSError:
            return []
        return archivos

    def hacer_backup(self, forzar: bool = False) -> Path | None:
        """Copia de seguridad según el parámetro ``backup_auto``:
        «sesion» (una por sesión), «dia» (una al día) o «no»."""
        modo = str(self.p("backup_auto", "sesion"))
        if not forzar:
            if modo == "no":
                return None
            ultimo = self.datos.get("ultimo_backup") or ""
            if modo == "dia" and ultimo[:10] == ahora()[:10]:
                return None
            if modo == "sesion" and getattr(self, "_backup_sesion", False):
                return None
        try:
            carpeta = self.carpeta_backups()
            carpeta.mkdir(parents=True, exist_ok=True)
            destino = carpeta / f"{COPIA}{datetime.now():%Y%m%d_%H%M%S}.json"
            destino.write_text(json.dumps(self.volcado(), ensure_ascii=False, indent=1),
                               encoding="utf-8")
        except OSError:
            log.exception("no se pudo hacer la copia de seguridad")
            return None
        self._backup_sesion = True
        self.datos["ultimo_backup"] = ahora()
        self.guardar_pronto()
        self.purgar_backups()
        return destino

    def purgar_backups(self, dias: int | None = None) -> int:
        dias = int(self.p("backup_purga_dias", 30) if dias is None else dias)
        limite = datetime.now() - timedelta(days=max(1, dias))
        borrados = 0
        for f in self.backups():
            try:
                if datetime.fromtimestamp(f.stat().st_mtime) < limite:
                    f.unlink()
                    borrados += 1
            except OSError:
                pass
        return borrados
