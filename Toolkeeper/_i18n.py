# SPDX-License-Identifier: GPL-3.0-or-later
"""Textos de Toolkeeper: las cadenas base en inglés y su
traducción por idioma (el catálogo central de IngeTrazo no traduce plugins).

El idioma lo elige el usuario (Extensiones ▸ Toolkeeper ▸
Idioma, o el botón 🌐 del gestor de barras) y se guarda en QSettings
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
        "Toolbar Manager": "Gestor de barras",
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
        "Toolbar states": "Estados de las barras",
        "States": "Estados",
        "Save and bring back the layout of toolbars and panels": "Guarda y recupera la colocación de barras y paneles",
        "Save the current state…": "Guardar el estado actual…",
        "(no saved states yet)": "(aún no hay estados guardados)",
        "Overwrite": "Sobrescribir",
        "Name of the state": "Nombre del estado",
        "State {n}": "Estado {n}",
        "A state named «{name}» already exists. Overwrite it?": "Ya hay un estado llamado «{name}». ¿Sobrescribirlo?",
        "Delete the state «{name}»?": "¿Borrar el estado «{name}»?",
        "State «{name}» saved.": "Estado «{name}» guardado.",
        "State «{name}» restored.": "Estado «{name}» recuperado.",
        "The state «{name}» could not be restored.": "No se pudo recuperar el estado «{name}».",
        "Not included: {names}": "Sin incluir: {names}",
        "Dictate by voice": "Dictar por voz",
        "Save the layout of toolbars and panels under a name in States, in the window or in the menu of the "
        "extension, and choose that name to bring it back. Only the layout changes, never what the panels contain.":
            "Guarda con un nombre la colocación de barras y paneles en Estados, en la ventana o en el menú de la "
            "extensión, y elige ese nombre para recuperarla. Solo cambia la colocación, nunca el contenido de los paneles.",
        "Language": "Idioma",
        "Automatic (as IngeTrazo)": "Automático (como IngeTrazo)",
        "Language of Toolkeeper": "Idioma de Toolkeeper",
        "The IngeTrazo extension manager was not found.": "No se ha encontrado el gestor de extensiones de IngeTrazo.",
        "The Toolbar Manager could not open: {err}": "No se pudo abrir el gestor de barras: {err}",
        "The list of shortcuts could not open: {err}": "No se pudo abrir la lista de atajos: {err}",
        "«{name}» is not available now.": "«{name}» no está disponible ahora.",
        # ---- gestor de barras
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
        "{name} toolbar": "Barra {name}",
        "«{name}» can only go in the {bar} toolbar.": "«{name}» solo se puede poner en la barra {bar}.",
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
        "(empty — drag icons here from the Toolbar Manager)":
            "(vacía: arrastra iconos aquí desde el gestor de barras)",
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
        "menu of the extension, or with the 🌐 button of the Toolbar Manager. It changes at once.":
            "Elige Automático (el idioma de IngeTrazo), Español, English o Français en Idioma, en el menú de la "
            "extensión, o con el botón 🌐 del gestor de barras. Cambia al momento.",
    },
    "fr": {
        # ---- nombre, menú y barra
        "Toolkeeper": "Toolkeeper",
        "Toolbar Manager": "Gestionnaire de barres",
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
        "Toolbar states": "États des barres",
        "States": "États",
        "Save and bring back the layout of toolbars and panels": "Enregistre et rétablit la disposition des barres et des panneaux",
        "Save the current state…": "Enregistrer l'état actuel…",
        "(no saved states yet)": "(pas encore d'états enregistrés)",
        "Overwrite": "Écraser",
        "Name of the state": "Nom de l'état",
        "State {n}": "État {n}",
        "A state named «{name}» already exists. Overwrite it?": "Un état nommé « {name} » existe déjà. L'écraser ?",
        "Delete the state «{name}»?": "Supprimer l'état « {name} » ?",
        "State «{name}» saved.": "État « {name} » enregistré.",
        "State «{name}» restored.": "État « {name} » rétabli.",
        "The state «{name}» could not be restored.": "Impossible de rétablir l'état « {name} ».",
        "Not included: {names}": "Non inclus : {names}",
        "Dictate by voice": "Dicter à la voix",
        "Save the layout of toolbars and panels under a name in States, in the window or in the menu of the "
        "extension, and choose that name to bring it back. Only the layout changes, never what the panels contain.":
            "Enregistrez sous un nom la disposition des barres et des panneaux dans États, dans la fenêtre ou dans le "
            "menu de l'extension, et choisissez ce nom pour la rétablir. Seule la disposition change, jamais le contenu des panneaux.",
        "Language": "Langue",
        "Automatic (as IngeTrazo)": "Automatique (comme IngeTrazo)",
        "Language of Toolkeeper": "Langue de Toolkeeper",
        "The IngeTrazo extension manager was not found.": "Le gestionnaire d'extensions d'IngeTrazo est introuvable.",
        "The Toolbar Manager could not open: {err}": "Le gestionnaire de barres n'a pas pu s'ouvrir : {err}",
        "The list of shortcuts could not open: {err}": "La liste des raccourcis n'a pas pu s'ouvrir : {err}",
        "«{name}» is not available now.": "« {name} » n'est pas disponible pour l'instant.",
        # ---- gestor de barras
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
        "{name} toolbar": "Barre {name}",
        "«{name}» can only go in the {bar} toolbar.": "« {name} » ne peut aller que dans la barre {bar}.",
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
        "(empty — drag icons here from the Toolbar Manager)":
            "(vide : glissez ici des icônes depuis le gestionnaire de barres)",
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
        "menu of the extension, or with the 🌐 button of the Toolbar Manager. It changes at once.":
            "Choisissez Automatique (la langue d'IngeTrazo), Español, English ou Français dans Langue, dans le "
            "menu de l'extension, ou avec le bouton 🌐 du gestionnaire de barres. Le changement est immédiat.",
    },
}

# ---- Conjuntos de extensiones (``_conjuntos.py``) ------------------------------
_TEXTS["es"].update({
    "Manage extensions…": "Gestionar extensiones…",
    "Open the IngeTrazo extension manager or save and bring back which extensions are on and off":
        "Abre el gestor de extensiones de IngeTrazo o guarda y recupera qué extensiones están activas y cuáles no",
    "Extension sets": "Conjuntos de extensiones",
    "Sets": "Conjuntos",
    "Save and bring back which extensions are on and off": "Guarda y recupera qué extensiones están activas y cuáles no",
    "Manage sets…": "Gestionar conjuntos…",
    "Save the current set…": "Guardar el conjunto actual…",
    "Save the current set": "Guardar el conjunto actual",
    "(no saved sets yet)": "(aún no hay conjuntos guardados)",
    "Back to the previous one": "Volver al anterior",
    "Previous": "Anterior",
    "The extension sets window could not open: {err}": "No se pudo abrir la ventana de conjuntos: {err}",
    "A set named «{name}» already exists. Overwrite it?": "Ya hay un conjunto llamado «{name}». ¿Sobrescribirlo?",
    "Set «{name}» saved.": "Conjunto «{name}» guardado.",
    "Set «{name}» updated.": "Conjunto «{name}» actualizado.",
    "Set {n}": "Conjunto {n}",
    "Name of the set": "Nombre del conjunto",
    "«{name}» already exists.": "Ya existe «{name}».",
    "Not installed now (ignored): {names}": "Ahora sin instalar (se ignoran): {names}",
    "Apply the set «{name}»?": "¿Aplicar el conjunto «{name}»?",
    "Apply the ticked extensions?": "¿Aplicar las extensiones marcadas?",
    "There is no previous set.": "No hay ningún conjunto anterior.",
    "Go back to the previous set?": "¿Volver al conjunto anterior?",
    "It will turn on <b>{n}</b>: {names}": "Se activarán <b>{n}</b>: {names}",
    "It will turn off <b>{n}</b>: {names}": "Se desactivarán <b>{n}</b>: {names}",
    "No extension changes: everything is already like this.": "No cambia ninguna extensión: ya está todo así.",
    "The layout of toolbars and panels is also restored": "También se recupera la colocación de barras y paneles",
    "(at the next start).": "(en el próximo arranque).",
    "The changes take effect when IngeTrazo restarts. The current set is kept so you can go «Back to the previous one».":
        "Los cambios surten efecto al reiniciar IngeTrazo. Se guarda el estado actual para poder «Volver al anterior».",
    "Apply (I will restart later)": "Aplicar (reiniciaré luego)",
    "Apply and restart now": "Aplicar y reiniciar ahora",
    "Apply": "Aplicar",
    "Apply and restart…": "Aplicar y reiniciar…",
    "These extensions could not be changed:": "No se pudieron cambiar estas extensiones:",
    "IngeTrazo was not closed: the changes will apply at the next start.":
        "IngeTrazo no se cerró: los cambios se aplicarán en el próximo arranque.",
    "Changes saved: restart IngeTrazo to apply them.": "Cambios guardados: reinicia IngeTrazo para aplicarlos.",
    "Layout of toolbars and panels of the set restored.": "Recuperada la colocación de barras y paneles del conjunto.",
    "Export extension sets": "Exportar conjuntos de extensiones",
    "Import extension sets": "Importar conjuntos de extensiones",
    "The file has no new extension sets.": "El archivo no tiene conjuntos de extensiones nuevos.",
    "Imported: {names}": "Importados: {names}",
    "The name you will choose in the menu or in the list of sets to bring this set back.":
        "El nombre que elegirás en el menú o en la lista de conjuntos para volver a este conjunto.",
    "Also remember where the toolbars and panels are": "Recordar también dónde están las barras y los paneles",
    "Also remembers where the toolbars and panels are": "Recuerda también dónde están las barras y los paneles",
    "When the set is applied, the toolbars and panels go back to where they are now. If extensions change, it is "
    "done at the next start, when their toolbars exist.":
        "Al aplicar el conjunto, las barras y los paneles vuelven a donde están ahora. Si cambian las extensiones, "
        "se hace en el próximo arranque, cuando ya existen sus barras.",
    "Saved sets": "Conjuntos guardados",
    "New…": "Nuevo…",
    "Save the ticked extensions as a new set": "Guarda las extensiones marcadas como un conjunto nuevo",
    "Apply the selected set": "Aplica el conjunto seleccionado",
    "Update": "Actualizar",
    "Overwrite the selected set with the ticked extensions": "Sobrescribe el conjunto seleccionado con las extensiones marcadas",
    "Update the set «{name}»": "Actualizar el conjunto «{name}»",
    "Rename…": "Renombrar…",
    "Rename the selected set": "Cambia el nombre del conjunto seleccionado",
    "Rename the set": "Renombrar el conjunto",
    "Delete the selected set": "Borra el conjunto seleccionado",
    "Delete the set «{name}»?": "¿Borrar el conjunto «{name}»?",
    "Export": "Exportar",
    "Export the selected set or all of them to a file": "Exporta a un archivo el conjunto seleccionado o todos",
    "The selected set…": "El conjunto seleccionado…",
    "All the sets…": "Todos los conjuntos…",
    "Import…": "Importar…",
    "Import extension sets from a file": "Importa conjuntos de extensiones desde un archivo",
    "Select a set in the list first.": "Primero elige un conjunto de la lista.",
    "Filter…": "Filtrar…",
    "Shows only the extensions whose name contains what you type.":
        "Muestra solo las extensiones cuyo nombre contiene lo que escribes.",
    "Turn all on": "Activar todas",
    "Tick every extension": "Marca todas las extensiones",
    "Turn all off": "Desactivar todas",
    "Untick every extension (except Toolkeeper)": "Desmarca todas las extensiones (menos Toolkeeper)",
    "Extension": "Extensión",
    "Extensions ({n})": "Extensiones ({n})",
    "Extensions ({n} of {m})": "Extensiones ({n} de {m})",
    "Now": "Ahora",
    "After restart": "Al reiniciar",
    "Installed": "Instalada",
    "Loaded": "Cargada",
    "Not loaded (error?)": "Sin cargar (¿error?)",
    "Off": "Desactivada",
    "Will turn on": "Se activará",
    "Will turn off": "Se desactivará",
    "catalogue": "catálogo",
    "loose file": "archivo suelto",
    "by hand": "a mano",
    "always on": "siempre activa",
    "Discard changes": "Descartar cambios",
    "Leave the extensions as they were when IngeTrazo started": "Deja las extensiones como estaban al arrancar IngeTrazo",
    "Leave the extensions as they were when IngeTrazo started?": "¿Dejar las extensiones como estaban al arrancar IngeTrazo?",
    "{n} pending changes: they apply when IngeTrazo restarts.": "{n} cambios pendientes: se aplican al reiniciar IngeTrazo.",
    "Unsaved changes.": "Cambios sin aplicar.",
    "The extensions included with IngeTrazo (Python console, Solid inspector…) are not listed: they cannot be turned off.":
        "Las extensiones incluidas con IngeTrazo (Consola Python, Inspector de sólidos…) no aparecen: no se pueden desactivar.",
    "Saved: {date}": "Guardado: {date}",
    "On: {n} · Off: {m}": "Activas: {n} · Desactivadas: {m}",
    "It is the current set": "Es el conjunto actual",
    "Set «{name}»: the ticks show how it would leave the extensions.":
        "Conjunto «{name}»: las casillas muestran cómo dejaría las extensiones.",
    "On at startup": "Activa al arrancar",
    "Ticked: IngeTrazo loads this extension when it starts. Unticked: IngeTrazo skips it. Nothing changes until you "
    "press Apply.":
        "Marcada: IngeTrazo carga esta extensión al arrancar. Desmarcada: IngeTrazo la salta. No cambia nada hasta "
        "que pulses Aplicar.",
    "Toolkeeper cannot be turned off (you would lose this window).":
        "Toolkeeper no se puede desactivar (perderías esta ventana).",
    "Loaded at startup": "Se carga al arrancar",
    "Skipped at startup": "Se salta al arrancar",
    "Modelling": "Modelado",
    "Documentation": "Documentación",
    "Toolbars and panels": "Barras y paneles",
    "in the same place": "en el mismo sitio",
    "Save under a name which extensions are on and which are off (Sets, in the window or in the menu of the "
    "extension) and choose that name to go back to it. IngeTrazo only loads extensions when it starts: applying a "
    "set leaves the changes ready and offers to restart. «Back to the previous one» undoes the last set applied. "
    "A set can also remember where the toolbars and panels are.":
        "Guarda con un nombre qué extensiones están activas y cuáles no (Conjuntos, en la ventana o en el menú de la "
        "extensión) y elige ese nombre para volver a ello. IngeTrazo solo carga extensiones al arrancar: aplicar un "
        "conjunto deja los cambios preparados y ofrece reiniciar. «Volver al anterior» deshace el último conjunto "
        "aplicado. Un conjunto puede recordar también dónde están las barras y los paneles.",
})

_TEXTS["fr"].update({
    "Manage extensions…": "Gérer les extensions…",
    "Open the IngeTrazo extension manager or save and bring back which extensions are on and off":
        "Ouvre le gestionnaire d'extensions d'IngeTrazo ou enregistre et rétablit les extensions actives et inactives",
    "Extension sets": "Ensembles d'extensions",
    "Sets": "Ensembles",
    "Save and bring back which extensions are on and off": "Enregistre et rétablit les extensions actives et inactives",
    "Manage sets…": "Gérer les ensembles…",
    "Save the current set…": "Enregistrer l'ensemble actuel…",
    "Save the current set": "Enregistrer l'ensemble actuel",
    "(no saved sets yet)": "(pas encore d'ensembles enregistrés)",
    "Back to the previous one": "Revenir au précédent",
    "Previous": "Précédent",
    "The extension sets window could not open: {err}": "Impossible d'ouvrir la fenêtre des ensembles : {err}",
    "A set named «{name}» already exists. Overwrite it?": "Un ensemble nommé « {name} » existe déjà. L'écraser ?",
    "Set «{name}» saved.": "Ensemble « {name} » enregistré.",
    "Set «{name}» updated.": "Ensemble « {name} » mis à jour.",
    "Set {n}": "Ensemble {n}",
    "Name of the set": "Nom de l'ensemble",
    "«{name}» already exists.": "« {name} » existe déjà.",
    "Not installed now (ignored): {names}": "Non installées (ignorées) : {names}",
    "Apply the set «{name}»?": "Appliquer l'ensemble « {name} » ?",
    "Apply the ticked extensions?": "Appliquer les extensions cochées ?",
    "There is no previous set.": "Il n'y a pas d'ensemble précédent.",
    "Go back to the previous set?": "Revenir à l'ensemble précédent ?",
    "It will turn on <b>{n}</b>: {names}": "Seront activées <b>{n}</b> : {names}",
    "It will turn off <b>{n}</b>: {names}": "Seront désactivées <b>{n}</b> : {names}",
    "No extension changes: everything is already like this.": "Aucune extension ne change : tout est déjà ainsi.",
    "The layout of toolbars and panels is also restored": "La disposition des barres et panneaux est aussi rétablie",
    "(at the next start).": "(au prochain démarrage).",
    "The changes take effect when IngeTrazo restarts. The current set is kept so you can go «Back to the previous one».":
        "Les changements prennent effet au redémarrage d'IngeTrazo. L'état actuel est conservé pour pouvoir "
        "« Revenir au précédent ».",
    "Apply (I will restart later)": "Appliquer (je redémarrerai plus tard)",
    "Apply and restart now": "Appliquer et redémarrer",
    "Apply": "Appliquer",
    "Apply and restart…": "Appliquer et redémarrer…",
    "These extensions could not be changed:": "Ces extensions n'ont pas pu être modifiées :",
    "IngeTrazo was not closed: the changes will apply at the next start.":
        "IngeTrazo n'a pas été fermé : les changements s'appliqueront au prochain démarrage.",
    "Changes saved: restart IngeTrazo to apply them.": "Changements enregistrés : redémarrez IngeTrazo pour les appliquer.",
    "Layout of toolbars and panels of the set restored.": "Disposition des barres et panneaux de l'ensemble rétablie.",
    "Export extension sets": "Exporter des ensembles d'extensions",
    "Import extension sets": "Importer des ensembles d'extensions",
    "The file has no new extension sets.": "Le fichier ne contient pas de nouvel ensemble.",
    "Imported: {names}": "Importés : {names}",
    "The name you will choose in the menu or in the list of sets to bring this set back.":
        "Le nom que vous choisirez dans le menu ou dans la liste pour revenir à cet ensemble.",
    "Also remember where the toolbars and panels are": "Mémoriser aussi la position des barres et panneaux",
    "Also remembers where the toolbars and panels are": "Mémorise aussi la position des barres et panneaux",
    "When the set is applied, the toolbars and panels go back to where they are now. If extensions change, it is "
    "done at the next start, when their toolbars exist.":
        "En appliquant l'ensemble, les barres et panneaux reviennent là où ils sont maintenant. Si des extensions "
        "changent, cela se fait au prochain démarrage, quand leurs barres existent.",
    "Saved sets": "Ensembles enregistrés",
    "New…": "Nouveau…",
    "Save the ticked extensions as a new set": "Enregistre les extensions cochées comme nouvel ensemble",
    "Apply the selected set": "Applique l'ensemble sélectionné",
    "Update": "Mettre à jour",
    "Overwrite the selected set with the ticked extensions": "Écrase l'ensemble sélectionné avec les extensions cochées",
    "Update the set «{name}»": "Mettre à jour l'ensemble « {name} »",
    "Rename…": "Renommer…",
    "Rename the selected set": "Renomme l'ensemble sélectionné",
    "Rename the set": "Renommer l'ensemble",
    "Delete the selected set": "Supprime l'ensemble sélectionné",
    "Delete the set «{name}»?": "Supprimer l'ensemble « {name} » ?",
    "Export": "Exporter",
    "Export the selected set or all of them to a file": "Exporte dans un fichier l'ensemble sélectionné ou tous",
    "The selected set…": "L'ensemble sélectionné…",
    "All the sets…": "Tous les ensembles…",
    "Import…": "Importer…",
    "Import extension sets from a file": "Importe des ensembles d'extensions depuis un fichier",
    "Select a set in the list first.": "Choisissez d'abord un ensemble dans la liste.",
    "Filter…": "Filtrer…",
    "Shows only the extensions whose name contains what you type.":
        "N'affiche que les extensions dont le nom contient ce que vous tapez.",
    "Turn all on": "Tout activer",
    "Tick every extension": "Coche toutes les extensions",
    "Turn all off": "Tout désactiver",
    "Untick every extension (except Toolkeeper)": "Décoche toutes les extensions (sauf Toolkeeper)",
    "Extension": "Extension",
    "Extensions ({n})": "Extensions ({n})",
    "Extensions ({n} of {m})": "Extensions ({n} sur {m})",
    "Now": "Maintenant",
    "After restart": "Au redémarrage",
    "Installed": "Installée",
    "Loaded": "Chargée",
    "Not loaded (error?)": "Non chargée (erreur ?)",
    "Off": "Désactivée",
    "Will turn on": "Sera activée",
    "Will turn off": "Sera désactivée",
    "catalogue": "catalogue",
    "loose file": "fichier isolé",
    "by hand": "à la main",
    "always on": "toujours active",
    "Discard changes": "Annuler les changements",
    "Leave the extensions as they were when IngeTrazo started": "Laisse les extensions comme au démarrage d'IngeTrazo",
    "Leave the extensions as they were when IngeTrazo started?": "Laisser les extensions comme au démarrage d'IngeTrazo ?",
    "{n} pending changes: they apply when IngeTrazo restarts.": "{n} changements en attente : appliqués au redémarrage d'IngeTrazo.",
    "Unsaved changes.": "Changements non appliqués.",
    "The extensions included with IngeTrazo (Python console, Solid inspector…) are not listed: they cannot be turned off.":
        "Les extensions fournies avec IngeTrazo (Console Python, Inspecteur de solides…) n'apparaissent pas : "
        "elles ne peuvent pas être désactivées.",
    "Saved: {date}": "Enregistré : {date}",
    "On: {n} · Off: {m}": "Actives : {n} · Désactivées : {m}",
    "It is the current set": "C'est l'ensemble actuel",
    "Set «{name}»: the ticks show how it would leave the extensions.":
        "Ensemble « {name} » : les cases montrent comment il laisserait les extensions.",
    "On at startup": "Active au démarrage",
    "Ticked: IngeTrazo loads this extension when it starts. Unticked: IngeTrazo skips it. Nothing changes until you "
    "press Apply.":
        "Cochée : IngeTrazo charge cette extension au démarrage. Décochée : IngeTrazo l'ignore. Rien ne change tant "
        "que vous n'appuyez pas sur Appliquer.",
    "Toolkeeper cannot be turned off (you would lose this window).":
        "Toolkeeper ne peut pas être désactivé (vous perdriez cette fenêtre).",
    "Loaded at startup": "Chargée au démarrage",
    "Skipped at startup": "Ignorée au démarrage",
    "Modelling": "Modélisation",
    "Documentation": "Documentation",
    "Toolbars and panels": "Barres et panneaux",
    "in the same place": "au même endroit",
    "Save under a name which extensions are on and which are off (Sets, in the window or in the menu of the "
    "extension) and choose that name to go back to it. IngeTrazo only loads extensions when it starts: applying a "
    "set leaves the changes ready and offers to restart. «Back to the previous one» undoes the last set applied. "
    "A set can also remember where the toolbars and panels are.":
        "Enregistrez sous un nom les extensions actives et inactives (Ensembles, dans la fenêtre ou dans le menu de "
        "l'extension) et choisissez ce nom pour y revenir. IngeTrazo ne charge les extensions qu'au démarrage : "
        "appliquer un ensemble prépare les changements et propose de redémarrer. « Revenir au précédent » annule le "
        "dernier ensemble appliqué. Un ensemble peut aussi mémoriser la position des barres et panneaux.",
})

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
