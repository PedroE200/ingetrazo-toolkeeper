# SPDX-License-Identifier: GPL-3.0-or-later
"""Textos de Toolkeeper: las cadenas base en inglés y su
traducción por idioma (el catálogo central de IngeTrazo no traduce plugins).

El idioma lo elige el usuario (Extensiones ▸ Toolkeeper ▸
Idioma, o el botón 🌐 del gestor maestro) y se guarda en QSettings
«IngeTrazo/igz_toolkeeper», clave ``idioma``: vacío = el de IngeTrazo; si no,
uno de ``IDIOMAS``. Va aparte del JSON de datos para que importar o
restaurar una configuración no lo cambie."""
from __future__ import annotations

AJUSTES = "igz_toolkeeper"          # QSettings("IngeTrazo", AJUSTES): idioma y barras ya colocadas

# Código → nombre de cada idioma, escrito en ese idioma (no se traduce).
IDIOMAS = {"es": "Español", "en": "English", "fr": "Français"}

_TEXTS: dict = {
    "es": {
        # ---- nombre, menú y barra
        "Toolkeeper": "Toolkeeper",
        "Master Toolbar Manager": "Gestor maestro de barras",
        "Manage all toolbars loaded in IngeTrazo": "Administra todas las barras cargadas en IngeTrazo",
        "Backup config": "Copia de seguridad de la configuración",
        "Make a backup copy of the configuration now": "Hace ahora una copia de seguridad de la configuración",
        "Import config": "Importar configuración",
        "Import custom toolbars and personal commands from a file or a backup":
            "Importa barras personalizadas y comandos personales desde un archivo o una copia",
        "Import custom toolbars and personal commands from a file":
            "Importa barras personalizadas y comandos personales desde un archivo",
        "Export config": "Exportar configuración",
        "Export custom toolbars and personal commands to a file":
            "Exporta barras personalizadas y comandos personales a un archivo",
        "List of all shortcuts": "Lista de todos los atajos",
        "Help": "Ayuda",
        "Help on Toolkeeper": "Ayuda de Toolkeeper",
        "Import from a config file…": "Importar desde un archivo de configuración…",
        "Restore a backup": "Restaurar una copia de seguridad",
        "(no backups yet)": "(aún no hay copias)",
        "Language": "Idioma",
        "Automatic (as IngeTrazo)": "Automático (como IngeTrazo)",
        "Language of Toolkeeper": "Idioma de Toolkeeper",
        "The IngeTrazo extension manager was not found.": "No se ha encontrado el gestor de extensiones de IngeTrazo.",
        "The Master Toolbar Manager could not open: {err}": "No se pudo abrir el gestor maestro: {err}",
        "The list of shortcuts could not open: {err}": "No se pudo abrir la lista de atajos: {err}",
        "«{name}» is not available now.": "«{name}» no está disponible ahora.",
        # ---- gestor maestro
        "Filter": "Filtro",
        "Recent filters": "Filtros recientes",
        "(no recent filters)": "(sin filtros recientes)",
        "Collapse all": "Plegar todo",
        "Expand all": "Desplegar todo",
        "Collapse every section of the tree": "Pliega todos los apartados del árbol",
        "Expand every section of the tree": "Despliega todos los apartados del árbol",
        "Click to collapse or expand": "Clic para plegar o desplegar",
        "Shortcuts": "Atajos",
        "Open the list of all shortcuts": "Abre la lista de todos los atajos",
        "Extensions": "Extensiones",
        "Open the IngeTrazo extension manager": "Abre el gestor de extensiones de IngeTrazo",
        "Print": "Imprimir",
        "Printing is not available in this IngeTrazo build.": "Imprimir no está disponible en esta compilación de IngeTrazo.",
        "Click on an icon to execute command - Click-Drag-Drop to add the icon to a custom toolbar":
            "Clic en un icono para ejecutar el comando - Arrastrar y soltar para añadirlo a una barra personalizada",
        "Personal Commands": "Comandos personales",
        "New…": "Nuevo…",
        "IngeTrazo native commands": "Comandos nativos de IngeTrazo",
        "Click to toggle the visibility of the toolbar": "Clic para mostrar u ocultar la barra",
        "Custom toolbars": "Barras personalizadas",
        "(no custom toolbars yet)": "(todavía no hay barras personalizadas)",
        "Drag icons from the tree here": "Arrastra aquí iconos del árbol",
        "Click to rename the custom toolbar": "Pulsa para renombrar la barra",
        "Click and Drag to insert a separator in a custom toolbar":
            "Clic y arrastrar para insertar un separador en una barra personalizada",
        "Create Custom toolbar…": "Crear barra personalizada…",
        "Click to Delete the custom toolbar": "Clic para borrar la barra personalizada",
        "Add to custom toolbar": "Añadir a una barra personalizada",
        "Edit…": "Editar…",
        "Delete": "Borrar",
        # ---- barras personalizadas
        "Name of the custom toolbar": "Nombre de la barra personalizada",
        "Toolbar {n}": "Barra {n}",
        "Rename the custom toolbar": "Renombrar la barra personalizada",
        "Rename the custom toolbar…": "Renombrar la barra personalizada…",
        "Delete the custom toolbar": "Borrar la barra personalizada",
        "Delete the custom toolbar «{name}»?": "¿Borrar la barra personalizada «{name}»?",
        "That name is already used.": "Ese nombre ya está en uso.",
        "Hide the toolbar": "Ocultar la barra",
        "(empty — drag icons here from the Master Toolbar Manager)":
            "(vacía: arrastra iconos aquí desde el gestor maestro)",
        "Added to «{name}».": "Añadido a «{name}».",
        "Run": "Ejecutar",
        "Remove command icon: {name}": "Quitar el icono del comando: {name}",
        "Insert Separator before Command [{name}]": "Insertar separador antes del comando [{name}]",
        "Insert Separator after Command [{name}]": "Insertar separador después del comando [{name}]",
        "{name}\n(not available)": "{name}\n(no disponible)",
        # ---- comandos personales
        "File shortcut": "Acceso directo", "Folder": "Carpeta", "Web Link": "Enlace web", "Menu": "Menú",
        "Python script": "Script de Python",
        "Personal": "Personal",
        "{type} {n}": "{type} {n}",
        "New Personal Command [{type}]": "Nuevo comando personal [{type}]",
        "Personal Command [{type}]": "Comando personal [{type}]",
        "Name": "Nombre", "Description": "Descripción", "Shortcut": "Atajo",
        "Use Color": "Usar color", "Icon": "Icono", "Choose…": "Elegir…",
        "Click to choose an image file (PNG/SVG); right-click to use the default icon":
            "Clic para elegir una imagen (PNG/SVG); clic derecho para usar el icono por defecto",
        "Cancel": "Cancelar", "Save": "Guardar",
        "Create Personal Command": "Crear comando personal",
        "You must give a valid name": "Debes dar un nombre válido",
        "You must give a target": "Debes indicar el destino",
        "Delete the personal command «{name}»?": "¿Borrar el comando personal «{name}»?",
        "{name}: {err}": "{name}: {err}",
        # ---- lista de atajos
        "List of Shortcuts": "Lista de atajos",
        "Search…": "Buscar…",
        "Only with shortcut": "Solo con atajo",
        "Done": "Hecho",
        "With shortcut ({n})": "Con atajo ({n})",
        "Command": "Comando",
        "Assigned by": "Asignado por",
        "Click a column title to sort; click again to reverse":
            "Pulsa el título de una columna para ordenar; otra vez para invertir",
        "Search a command…": "Buscar un comando…",
        "Current shortcut": "Atajo actual",
        "New shortcut (press the keys)": "Nuevo atajo (pulsa las teclas)",
        "(none)": "(ninguno)",
        "(no matches)": "(sin coincidencias)",
        "(and {n} more)": "(y {n} más)",
        "Assign": "Asignar",
        "Remove shortcut": "Quitar atajo",
        "Other": "Otros",
        "Choose a command first": "Elige antes un comando",
        "Press the new keys first": "Pulsa antes las teclas nuevas",
        "Choose a command from the list or the search box to change its shortcut":
            "Elige un comando de la lista o del buscador para cambiar su atajo",
        "{keys} is free.": "{keys} está libre.",
        "It is already its shortcut.": "Ya es su atajo.",
        "{keys} is already assigned to «{name}» ({where}). Assigning it will remove it from there.":
            "{keys} ya está asignado a «{name}» ({where}). Al asignarlo se le quitará.",
        "Shortcut {keys} assigned to «{name}».": "Atajo {keys} asignado a «{name}».",
        "Shortcut removed from «{name}».": "Atajo quitado de «{name}».",
        "This command cannot take a shortcut now.": "Este comando no admite atajo ahora.",
        "Saved where IngeTrazo keeps its shortcuts; applied at once, also to extension commands.":
            "Se guarda donde IngeTrazo guarda sus atajos y se aplica al momento, también a los comandos de extensiones.",
        # ---- copias, importar, exportar
        "Export config to file (extension will be {ext})": "Exportar la configuración a un archivo (extensión {ext})",
        "Exported to {path}": "Exportado a {path}",
        "Merge the file with your current data, or replace everything?":
            "¿Combinar el archivo con tus datos actuales o reemplazarlo todo?",
        "Merge": "Combinar", "Replace": "Reemplazar",
        "Backup saved: {path}": "Copia guardada: {path}",
        # ---- ayuda
        "Close": "Cerrar",
        "Toolbar manager for IngeTrazo: custom toolbars, personal commands, backups and shortcuts.":
            "Gestor de barras de herramientas para IngeTrazo: barras personalizadas, comandos personales, copias de seguridad y atajos.",
        "Backup, import, export": "Copias, importar, exportar",
        "Every command, grouped: IngeTrazo native commands by toolbar and one section per extension (tick a "
        "toolbar to show or hide it); on the right, custom toolbars (real dockable toolbars) and personal "
        "commands (folder, web link, menu, Python script, file shortcut). Click an icon to run it; drag it "
        "to a custom toolbar. The Filter box searches by name (wildcard *).":
            "Todos los comandos, agrupados: comandos nativos de IngeTrazo por barra y una sección por extensión "
            "(marca una barra para mostrarla u ocultarla); a la derecha, las barras personalizadas (barras "
            "acoplables reales) y los comandos personales (carpeta, enlace web, menú, script de Python, acceso "
            "directo). Clic en un icono lo ejecuta; arrástralo a una barra personalizada. El filtro busca por "
            "nombre (comodín *).",
        "The configuration (custom toolbars and personal commands) is backed up automatically once a "
        "session in the «backups» folder next to the data file, and purged after 30 days. You can export it "
        "to a file and import it (merging or replacing) or restore a backup from the Import menu.":
            "La configuración (barras personalizadas y comandos personales) se copia sola una vez por sesión en "
            "la carpeta «backups» junto al archivo de datos, y las copias se borran a los 30 días. Puedes "
            "exportarla a un archivo e importarla (combinando o reemplazando) o restaurar una copia desde el "
            "menú Importar.",
        "Every shortcut of IngeTrazo, of the extensions and of your personal commands, by sections; "
        "it can be filtered and printed.":
            "Todos los atajos de IngeTrazo, de las extensiones y de tus comandos personales, por secciones; "
            "se puede filtrar e imprimir.",
        "Choose Automatic (the language of IngeTrazo), Español, English or Français in Language, in the "
        "menu of the extension, or with the 🌐 button of the Master Toolbar Manager. It changes at once.":
            "Elige Automático (el idioma de IngeTrazo), Español, English o Français en Idioma, en el menú de la "
            "extensión, o con el botón 🌐 del gestor maestro. Cambia al momento.",
    },
    "fr": {
        # ---- nombre, menú y barra
        "Toolkeeper": "Toolkeeper",
        "Master Toolbar Manager": "Gestionnaire principal des barres",
        "Manage all toolbars loaded in IngeTrazo": "Gère toutes les barres d'outils chargées dans IngeTrazo",
        "Backup config": "Sauvegarde de la configuration",
        "Make a backup copy of the configuration now": "Fait maintenant une copie de sauvegarde de la configuration",
        "Import config": "Importer la configuration",
        "Import custom toolbars and personal commands from a file or a backup":
            "Importe les barres personnalisées et les commandes personnelles depuis un fichier ou une sauvegarde",
        "Import custom toolbars and personal commands from a file":
            "Importe les barres personnalisées et les commandes personnelles depuis un fichier",
        "Export config": "Exporter la configuration",
        "Export custom toolbars and personal commands to a file":
            "Exporte les barres personnalisées et les commandes personnelles vers un fichier",
        "List of all shortcuts": "Liste de tous les raccourcis",
        "Help": "Aide",
        "Help on Toolkeeper": "Aide de Toolkeeper",
        "Import from a config file…": "Importer depuis un fichier de configuration…",
        "Restore a backup": "Restaurer une sauvegarde",
        "(no backups yet)": "(pas encore de sauvegardes)",
        "Language": "Langue",
        "Automatic (as IngeTrazo)": "Automatique (comme IngeTrazo)",
        "Language of Toolkeeper": "Langue de Toolkeeper",
        "The IngeTrazo extension manager was not found.": "Le gestionnaire d'extensions d'IngeTrazo est introuvable.",
        "The Master Toolbar Manager could not open: {err}": "Le gestionnaire principal n'a pas pu s'ouvrir : {err}",
        "The list of shortcuts could not open: {err}": "La liste des raccourcis n'a pas pu s'ouvrir : {err}",
        "«{name}» is not available now.": "« {name} » n'est pas disponible pour l'instant.",
        # ---- gestor maestro
        "Filter": "Filtre",
        "Recent filters": "Filtres récents",
        "(no recent filters)": "(aucun filtre récent)",
        "Collapse all": "Tout replier",
        "Expand all": "Tout déplier",
        "Collapse every section of the tree": "Replie toutes les sections de l'arbre",
        "Expand every section of the tree": "Déplie toutes les sections de l'arbre",
        "Click to collapse or expand": "Clic pour replier ou déplier",
        "Shortcuts": "Raccourcis",
        "Open the list of all shortcuts": "Ouvre la liste de tous les raccourcis",
        "Extensions": "Extensions",
        "Open the IngeTrazo extension manager": "Ouvre le gestionnaire d'extensions d'IngeTrazo",
        "Print": "Imprimer",
        "Printing is not available in this IngeTrazo build.": "L'impression n'est pas disponible dans cette version d'IngeTrazo.",
        "Click on an icon to execute command - Click-Drag-Drop to add the icon to a custom toolbar":
            "Clic sur une icône pour exécuter la commande - Glisser-déposer pour l'ajouter à une barre personnalisée",
        "Personal Commands": "Commandes personnelles",
        "New…": "Nouveau…",
        "IngeTrazo native commands": "Commandes natives d'IngeTrazo",
        "Click to toggle the visibility of the toolbar": "Clic pour afficher ou masquer la barre",
        "Custom toolbars": "Barres personnalisées",
        "(no custom toolbars yet)": "(pas encore de barres personnalisées)",
        "Drag icons from the tree here": "Glissez ici des icônes de l'arbre",
        "Click to rename the custom toolbar": "Cliquez pour renommer la barre",
        "Click and Drag to insert a separator in a custom toolbar":
            "Cliquer-glisser pour insérer un séparateur dans une barre personnalisée",
        "Create Custom toolbar…": "Créer une barre personnalisée…",
        "Click to Delete the custom toolbar": "Clic pour supprimer la barre personnalisée",
        "Add to custom toolbar": "Ajouter à une barre personnalisée",
        "Edit…": "Modifier…",
        "Delete": "Supprimer",
        # ---- barras personalizadas
        "Name of the custom toolbar": "Nom de la barre personnalisée",
        "Toolbar {n}": "Barre {n}",
        "Rename the custom toolbar": "Renommer la barre personnalisée",
        "Rename the custom toolbar…": "Renommer la barre personnalisée…",
        "Delete the custom toolbar": "Supprimer la barre personnalisée",
        "Delete the custom toolbar «{name}»?": "Supprimer la barre personnalisée « {name} » ?",
        "That name is already used.": "Ce nom est déjà utilisé.",
        "Hide the toolbar": "Masquer la barre",
        "(empty — drag icons here from the Master Toolbar Manager)":
            "(vide : glissez ici des icônes depuis le gestionnaire principal)",
        "Added to «{name}».": "Ajouté à « {name} ».",
        "Run": "Exécuter",
        "Remove command icon: {name}": "Retirer l'icône de la commande : {name}",
        "Insert Separator before Command [{name}]": "Insérer un séparateur avant la commande [{name}]",
        "Insert Separator after Command [{name}]": "Insérer un séparateur après la commande [{name}]",
        "{name}\n(not available)": "{name}\n(non disponible)",
        # ---- comandos personales
        "File shortcut": "Raccourci de fichier", "Folder": "Dossier", "Web Link": "Lien web", "Menu": "Menu",
        "Python script": "Script Python",
        "Personal": "Personnel",
        "{type} {n}": "{type} {n}",
        "New Personal Command [{type}]": "Nouvelle commande personnelle [{type}]",
        "Personal Command [{type}]": "Commande personnelle [{type}]",
        "Name": "Nom", "Description": "Description", "Shortcut": "Raccourci",
        "Use Color": "Utiliser une couleur", "Icon": "Icône", "Choose…": "Choisir…",
        "Click to choose an image file (PNG/SVG); right-click to use the default icon":
            "Clic pour choisir une image (PNG/SVG) ; clic droit pour l'icône par défaut",
        "Cancel": "Annuler", "Save": "Enregistrer",
        "Create Personal Command": "Créer la commande personnelle",
        "You must give a valid name": "Vous devez donner un nom valide",
        "You must give a target": "Vous devez indiquer la cible",
        "Delete the personal command «{name}»?": "Supprimer la commande personnelle « {name} » ?",
        "{name}: {err}": "{name} : {err}",
        # ---- lista de atajos
        "List of Shortcuts": "Liste des raccourcis",
        "Search…": "Rechercher…",
        "Only with shortcut": "Seulement avec raccourci",
        "Done": "Terminé",
        "With shortcut ({n})": "Avec raccourci ({n})",
        "Command": "Commande",
        "Assigned by": "Attribué par",
        "Click a column title to sort; click again to reverse":
            "Cliquez sur le titre d'une colonne pour trier ; encore une fois pour inverser",
        "Search a command…": "Rechercher une commande…",
        "Current shortcut": "Raccourci actuel",
        "New shortcut (press the keys)": "Nouveau raccourci (appuyez sur les touches)",
        "(none)": "(aucun)",
        "(no matches)": "(aucun résultat)",
        "(and {n} more)": "(et {n} de plus)",
        "Assign": "Attribuer",
        "Remove shortcut": "Retirer le raccourci",
        "Other": "Autres",
        "Choose a command first": "Choisissez d'abord une commande",
        "Press the new keys first": "Appuyez d'abord sur les nouvelles touches",
        "Choose a command from the list or the search box to change its shortcut":
            "Choisissez une commande dans la liste ou la recherche pour changer son raccourci",
        "{keys} is free.": "{keys} est libre.",
        "It is already its shortcut.": "C'est déjà son raccourci.",
        "{keys} is already assigned to «{name}» ({where}). Assigning it will remove it from there.":
            "{keys} est déjà attribué à « {name} » ({where}). L'attribuer le lui retirera.",
        "Shortcut {keys} assigned to «{name}».": "Raccourci {keys} attribué à « {name} ».",
        "Shortcut removed from «{name}».": "Raccourci retiré de « {name} ».",
        "This command cannot take a shortcut now.": "Cette commande n'accepte pas de raccourci pour l'instant.",
        "Saved where IngeTrazo keeps its shortcuts; applied at once, also to extension commands.":
            "Enregistré là où IngeTrazo garde ses raccourcis et appliqué aussitôt, y compris aux commandes des extensions.",
        # ---- copias, importar, exportar
        "Export config to file (extension will be {ext})": "Exporter la configuration vers un fichier (extension {ext})",
        "Exported to {path}": "Exporté vers {path}",
        "Merge the file with your current data, or replace everything?":
            "Fusionner le fichier avec vos données actuelles ou tout remplacer ?",
        "Merge": "Fusionner", "Replace": "Remplacer",
        "Backup saved: {path}": "Sauvegarde enregistrée : {path}",
        # ---- ayuda
        "Close": "Fermer",
        "Toolbar manager for IngeTrazo: custom toolbars, personal commands, backups and shortcuts.":
            "Gestionnaire de barres d'outils pour IngeTrazo : barres personnalisées, commandes personnelles, sauvegardes et raccourcis.",
        "Backup, import, export": "Sauvegardes, importer, exporter",
        "Every command, grouped: IngeTrazo native commands by toolbar and one section per extension (tick a "
        "toolbar to show or hide it); on the right, custom toolbars (real dockable toolbars) and personal "
        "commands (folder, web link, menu, Python script, file shortcut). Click an icon to run it; drag it "
        "to a custom toolbar. The Filter box searches by name (wildcard *).":
            "Toutes les commandes, regroupées : commandes natives d'IngeTrazo par barre et une section par "
            "extension (cochez une barre pour l'afficher ou la masquer) ; à droite, les barres personnalisées "
            "(vraies barres ancrables) et les commandes personnelles (dossier, lien web, menu, script Python, "
            "raccourci de fichier). Un clic sur une icône l'exécute ; glissez-la vers une barre personnalisée. "
            "Le filtre cherche par nom (joker *).",
        "The configuration (custom toolbars and personal commands) is backed up automatically once a "
        "session in the «backups» folder next to the data file, and purged after 30 days. You can export it "
        "to a file and import it (merging or replacing) or restore a backup from the Import menu.":
            "La configuration (barres personnalisées et commandes personnelles) est sauvegardée automatiquement "
            "une fois par session dans le dossier « backups » à côté du fichier de données, et les copies sont "
            "supprimées au bout de 30 jours. Vous pouvez l'exporter vers un fichier et l'importer (en fusionnant "
            "ou en remplaçant) ou restaurer une sauvegarde depuis le menu Importer.",
        "Every shortcut of IngeTrazo, of the extensions and of your personal commands, by sections; "
        "it can be filtered and printed.":
            "Tous les raccourcis d'IngeTrazo, des extensions et de vos commandes personnelles, par sections ; "
            "la liste peut être filtrée et imprimée.",
        "Choose Automatic (the language of IngeTrazo), Español, English or Français in Language, in the "
        "menu of the extension, or with the 🌐 button of the Master Toolbar Manager. It changes at once.":
            "Choisissez Automatique (la langue d'IngeTrazo), Español, English ou Français dans Langue, dans le "
            "menu de l'extension, ou avec le bouton 🌐 du gestionnaire principal. Le changement est immédiat.",
    },
}

_elegido: str | None = None     # None = aún sin leer de QSettings


def _ajustes():
    from PySide6.QtCore import QSettings
    return QSettings("IngeTrazo", AJUSTES)


def idioma_elegido() -> str:
    """El código que eligió el usuario, o "" si sigue el de IngeTrazo."""
    global _elegido
    if _elegido is None:
        try:
            valor = str(_ajustes().value("idioma", "") or "")
        except Exception:  # noqa: BLE001
            valor = ""
        _elegido = valor if valor in IDIOMAS else ""
    return _elegido


def poner_idioma(codigo: str) -> None:
    global _elegido
    _elegido = codigo if codigo in IDIOMAS else ""
    try:
        _ajustes().setValue("idioma", _elegido)
    except Exception:  # noqa: BLE001
        pass


def _lang() -> str:
    elegido = idioma_elegido()
    if elegido:
        return elegido
    try:
        from core.i18n import current_language
        return current_language()
    except Exception:  # noqa: BLE001
        return "en"


def _t(text: str, **kw) -> str:
    out = _TEXTS.get(_lang(), {}).get(text, text)
    return out.format(**kw) if kw else out
