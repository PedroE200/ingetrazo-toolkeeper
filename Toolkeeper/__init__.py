# SPDX-License-Identifier: GPL-3.0-or-later
"""TOOLKEEPER — gestor de barras de herramientas para
IngeTrazo (API 2): el gestor de barras, las copias de seguridad, importar y
exportar la configuración, la lista de atajos y la ayuda.

Gestor de barras
    Filtro, comandos nativos de IngeTrazo por barra, una sección por
    extensión (con casilla para mostrar u ocultar cada barra), barras
    personalizadas (QToolBar reales), comandos personales (carpeta, enlace
    web, menú, script Python, acceso directo), importar/exportar/imprimir.

Idioma propio (``_i18n.py``): automático (el de IngeTrazo), español, inglés
o francés, elegido en el menú ▸ Idioma o con el botón 🌐 del gestor.
Estados de las barras (``_estados.py``): la colocación de barras y paneles,
guardada con un nombre para recuperarla.
Conjuntos de extensiones (``_conjuntos.py``): qué extensiones están activas
y cuáles no, guardado con un nombre; se aplica al reiniciar IngeTrazo.
Los datos van en ``%APPDATA%\\IngeTrazo\\igz_toolkeeper\\``.

Las demás extensiones (Rosco) la encuentran en ``window._igz_toolkeeper`` y
arrastran sus iconos con el MIME ``application/x-igz-toolkeeper``. La clave de
extensión, que IngeTrazo saca del nombre de la carpeta, se fija en
``igz_toolkeeper`` en ``setup``.

Instalar: copiar la carpeta ``Toolkeeper`` a
%APPDATA%\\IngeTrazo\\plugins y reiniciar IngeTrazo.
"""
from __future__ import annotations

import logging

__version__ = "2.6.0"
__plugin_name__ = "Toolkeeper"
CLAVE = "igz_toolkeeper"

log = logging.getLogger("ingetrazo.plugins.igz_toolkeeper")


def setup(app):
    if getattr(app, "api_version", 0) < 2:
        raise RuntimeError("Toolkeeper requiere la API de extensiones 2")
    maestro = getattr(app.window, "_igz_toolkeeper", None)
    if maestro is not None:                 # setup ya corrió
        return maestro
    # IngeTrazo saca la clave del nombre de la carpeta; se fija
    # para que los menús y lo que se guarde por ella no dependan de ese nombre.
    app.key = CLAVE
    from ._maestro import Maestro
    maestro = Maestro(app)
    maestro.instalar()
    app.window._igz_toolkeeper = maestro        # el nombre por el que la buscan las demás (Rosco)
    log.info("Toolkeeper %s cargado", __version__)
    return maestro
