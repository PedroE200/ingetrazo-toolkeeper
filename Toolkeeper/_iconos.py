# SPDX-License-Identifier: GPL-3.0-or-later
"""Iconos de Toolkeeper dibujados con QPainter: trazo en el
color de texto del tema (claro u oscuro) y el naranja de acento de IngeTrazo."""
from __future__ import annotations

import math
import re
import zlib

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF

ACENTO = "#f37329"
ORO = "#d4a017"
LADO = 64


def _lienzo():
    pm = QPixmap(LADO, LADO)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    return pm, p


def _pluma(tinta, ancho=4.0):
    return QPen(tinta, ancho, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)


def _brocha(color, alfa=1.0) -> QBrush:
    c = QColor(color)
    c.setAlphaF(alfa)
    return QBrush(c)


def _anillo(p, tinta):
    """Anillo dorado, fondo de los iconos de las órdenes propias."""
    p.setPen(_pluma(QColor(ORO), 7))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(28, 36), 20, 14)
    p.setPen(_pluma(tinta, 1.5))
    p.drawEllipse(QPointF(28, 36), 20, 14)


def gestor(tinta) -> QIcon:
    """Anillo con engranaje: las órdenes propias (menos el gestor, que es el dragón)."""
    pm, p = _lienzo()
    _anillo(p, tinta)
    cx, cy = 44, 22
    p.setPen(_pluma(tinta, 2))
    p.setBrush(_brocha(ACENTO))
    pts = []
    for i in range(16):
        r = 15 if i % 2 == 0 else 11
        a = math.radians(i * 22.5)
        pts.append(QPointF(cx + r * math.cos(a), cy + r * math.sin(a)))
    p.drawPolygon(QPolygonF(pts))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(cx, cy), 4.5, 4.5)
    p.end()
    return QIcon(pm)


def tipo_personal(tipo: str, tinta) -> QIcon:
    """Iconos de los comandos personales: acceso directo, carpeta, web, menú, script."""
    pm, p = _lienzo()
    p.setPen(_pluma(tinta, 3.5))
    p.setBrush(Qt.NoBrush)
    if tipo == "documento":                 # acceso directo a un archivo
        hoja = QPainterPath()
        hoja.moveTo(14, 6)
        hoja.lineTo(38, 6)
        hoja.lineTo(50, 18)
        hoja.lineTo(50, 58)
        hoja.lineTo(14, 58)
        hoja.closeSubpath()
        p.drawPath(hoja)
        p.drawPolyline([QPointF(38, 6), QPointF(38, 18), QPointF(50, 18)])
        for y in (30, 38, 46):
            p.drawLine(QPointF(22, y), QPointF(42, y))
    elif tipo == "carpeta":
        c = QPainterPath()
        c.moveTo(6, 14)
        c.lineTo(24, 14)
        c.lineTo(29, 20)
        c.lineTo(58, 20)
        c.lineTo(58, 52)
        c.lineTo(6, 52)
        c.closeSubpath()
        p.setBrush(_brocha(ORO, 0.8))
        p.drawPath(c)
    elif tipo == "web":
        p.drawEllipse(QPointF(32, 32), 24, 24)
        p.drawEllipse(QPointF(32, 32), 10, 24)
        p.drawLine(QPointF(8, 32), QPointF(56, 32))
        p.drawLine(QPointF(12, 20), QPointF(52, 20))
        p.drawLine(QPointF(12, 44), QPointF(52, 44))
    elif tipo == "menu":
        for y in (16, 32, 48):
            p.drawLine(QPointF(10, y), QPointF(54, y))
    else:   # script
        p.setBrush(_brocha("#c41e3a", 0.9))
        p.setPen(_pluma(tinta, 2.5))
        p.drawRoundedRect(QRectF(10, 10, 44, 44), 8, 8)
        p.setPen(_pluma(QColor("white"), 4))
        p.drawPolyline([QPointF(26, 24), QPointF(18, 32), QPointF(26, 40)])
        p.drawPolyline([QPointF(38, 24), QPointF(46, 32), QPointF(38, 40)])
    p.end()
    return QIcon(pm)


def letras(nombre: str, key: str, disponible: bool = True, color: str = "") -> QIcon:
    """Cuadrado redondeado de color (fijo por clave, o el dado) con las
    iniciales del comando. Gris con «?» si el comando ya no existe."""
    pm, p = _lienzo()
    if disponible:
        fondo = QColor(color) if color else QColor.fromHsv(
            zlib.crc32(key.encode("utf-8")) % 360, 150, 205)
        palabras = re.findall(r"[^\W_]+", nombre or key)
        if len(palabras) >= 2:
            txt = palabras[0][0] + palabras[1][0]
        else:
            txt = palabras[0][:2] if palabras else "?"
        txt = txt[:1].upper() + txt[1:2].lower()
    else:
        fondo, txt = QColor(140, 140, 140), "?"
    p.setPen(Qt.NoPen)
    p.setBrush(fondo)
    p.drawRoundedRect(QRectF(4, 4, LADO - 8, LADO - 8), 12, 12)
    f = QFont()
    f.setBold(True)
    f.setPixelSize(28 if len(txt) > 1 else 34)
    p.setFont(f)
    claro = fondo.lightness() > 150
    p.setPen(QColor("black") if claro else QColor("white"))
    p.drawText(QRectF(0, 0, LADO, LADO), Qt.AlignCenter, txt)
    p.end()
    return QIcon(pm)


def con_color(icono: QIcon, color: str) -> QIcon:
    """El icono sobre un fondo de color (comandos personales «Usar color»)."""
    if not color:
        return icono
    pm = QPixmap(LADO, LADO)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(color))
    p.drawRoundedRect(QRectF(2, 2, LADO - 4, LADO - 4), 10, 10)
    icono.paint(p, 6, 6, LADO - 12, LADO - 12)
    p.end()
    return QIcon(pm)
