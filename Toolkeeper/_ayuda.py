# SPDX-License-Identifier: GPL-3.0-or-later
"""La ayuda de Toolkeeper."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout

from ._catalogo import PREFIJO
from ._i18n import _t


class DialogoAyuda(QDialog):
    def __init__(self, maestro) -> None:
        super().__init__(maestro.app.window)
        self.setObjectName(PREFIJO + "_dlg_ayuda")
        self.setWindowTitle(_t("Help on Toolkeeper"))
        self.resize(640, 480)
        lay = QVBoxLayout(self)
        texto = QTextBrowser()
        texto.setOpenExternalLinks(True)
        texto.setHtml(self.html())
        lay.addWidget(texto, 1)
        fila = QHBoxLayout()
        fila.addStretch(1)
        cerrar = QPushButton(_t("Close"))
        cerrar.setDefault(True)
        cerrar.clicked.connect(self.accept)
        fila.addWidget(cerrar)
        lay.addLayout(fila)

    @staticmethod
    def html() -> str:
        secciones = (
            (_t("Toolbar Manager"), _t(
                "Every command, grouped: IngeTrazo native commands by toolbar and one section per extension (tick a "
                "toolbar to show or hide it); on the right, custom toolbars (real dockable toolbars) and personal "
                "commands (folder, web link, menu, Python script, file shortcut). Click an icon to run it; drag it "
                "to a custom toolbar. The Filter box searches by name (wildcard *).")),
            (_t("Backup, import, export"), _t(
                "The configuration (custom toolbars and personal commands) is backed up automatically once a "
                "session in the «backups» folder next to the data file, and purged after 30 days. You can export it "
                "to a file and import it (merging or replacing) or restore a backup from the Import menu.")),
            (_t("List of all shortcuts"), _t(
                "Every shortcut of IngeTrazo, of the extensions and of your personal commands, by sections; "
                "it can be filtered and printed.")),
            (_t("Toolbar states"), _t(
                "Save the layout of toolbars and panels under a name in States, in the window or in the menu of the "
                "extension, and choose that name to bring it back. Only the layout changes, never what the panels contain.")),
            (_t("Extension sets"), _t(
                "Save under a name which extensions are on and which are off (Sets, in the window or in the menu of the "
                "extension) and choose that name to go back to it. IngeTrazo only loads extensions when it starts: applying a "
                "set leaves the changes ready and offers to restart. «Back to the previous one» undoes the last set applied. "
                "A set can also remember where the toolbars and panels are.")),
            (_t("Language"), _t(
                "Choose Automatic (the language of IngeTrazo), Español, English or Français in Language, in the "
                "menu of the extension, or with the 🌐 button of the Toolbar Manager. It changes at once.")),
        )
        partes = [f"<h2>{_t('Toolkeeper')}</h2><p><i>{_t('Toolbar manager for IngeTrazo: custom toolbars, personal commands, backups and shortcuts.')}</i></p>"]
        for titulo, cuerpo in secciones:
            partes.append(f"<h3>{titulo}</h3><p>{cuerpo}</p>")
        return "".join(partes)
