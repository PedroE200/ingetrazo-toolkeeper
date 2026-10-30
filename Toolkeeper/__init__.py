# SPDX-License-Identifier: GPL-3.0-or-later
"""TOOLKEEPER — gestor de barras de herramientas para
IngeTrazo (API 2): el gestor maestro, las copias de seguridad, importar y
exportar la configuración, la lista de atajos y la ayuda.

Gestor maestro
    Filtro, comandos nativos de IngeTrazo por barra, una sección por
    extensión (con casilla para mostrar u ocultar cada barra), barras
    personalizadas (QToolBar reales), comandos personales (carpeta, enlace
    web, menú, script Python, acceso directo), importar/exportar/imprimir.

Idioma propio (``_i18n.py``): automático (el de IngeTrazo), español, inglés
o francés, elegido en el menú ▸ Idioma o con el botón 🌐 del gestor.
Los datos van en ``%APPDATA%\\IngeTrazo\\igz_toolkeeper\\``.

La clave de extensión, que IngeTrazo saca del nombre de la carpeta, se fija
en ``igz_toolkeeper`` en ``setup``. Todos los identificadores internos
(clave, objectName, QSettings, carpeta de datos, MIME de los arrastres,
``window._igz_toolkeeper``) son propios, distintos de los de Maestro de
Barras-Toolkeeper, para que las dos extensiones puedan convivir.

Instalar: copiar la carpeta ``Toolkeeper`` a
%APPDATA%\\IngeTrazo\\plugins y reiniciar IngeTrazo.
"""
from __future__ import annotations

import logging

__version__ = "1.0.0"
__plugin_name__ = "Toolkeeper"
CLAVE = "igz_toolkeeper"

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")


def setup(app):
    if getattr(app, "api_version", 0) < 2:
        raise RuntimeError("Toolkeeper requiere la API de extensiones 2")
    maestro = getattr(app.window, "_igz_toolkeeper", None)
    if maestro is not None:                 # setup ya corrió
        return maestro
    # IngeTrazo saca la clave del nombre de la carpeta (con espacios); se fija
    # para que los menús y lo que se guarde por ella no dependan de ese nombre.
    app.key = CLAVE
    from ._maestro import Maestro
    maestro = Maestro(app)
    maestro.instalar()
    app.window._igz_toolkeeper = maestro        # una sola instancia por ventana
    log.info("Toolkeeper %s cargado", __version__)
    return maestro
