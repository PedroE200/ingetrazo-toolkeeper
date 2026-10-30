# Toolkeeper 1.0 — para IngeTrazo

Gestor de barras de herramientas para IngeTrazo (API de extensiones 2,
IngeTrazo 0.5.8). Órdenes del menú:

| Orden | Qué hace |
|---|---|
| **Gestor maestro de barras** | Icono: el dragón azul (`icono_gestor.png`). Ventana en tema oscuro. Cabecera: filtro (con recientes), Plegar/Desplegar todo, Atajos, Extensiones (gestor de extensiones de IngeTrazo), Idioma (🌐), ayuda, importar, exportar, imprimir. A la izquierda, un árbol de apartados plegables (comandos nativos de IngeTrazo por barra, una sección por extensión con casilla para mostrar/ocultar cada barra); se recuerda qué apartados quedaron plegados y al filtrar se despliegan los que tienen coincidencias. En el lateral derecho, también plegables, las barras personalizadas (casilla para mostrarla, nombre que se renombra pulsándolo, papelera; el lateral se refresca solo al soltar iconos) y debajo los comandos personales (carpeta, enlace web, menú, script de Python y acceso directo). Clic en un icono lo ejecuta; arrastrarlo lo lleva a una barra personalizada. |
| **Copia de seguridad de la configuración** | Copia ahora (además de la automática, una por sesión; se borran a los 30 días). |
| **Importar configuración** | Desde un archivo `.igz_toolkeeper.json` (o cualquier `.json` con barras y comandos personales) o restaurando una copia (combinar o reemplazar). |
| **Exportar configuración** | Barras personalizadas y comandos personales a un `.igz_toolkeeper.json`. |
| **Lista de todos los atajos** | A la izquierda, solo los comandos con atajo (Atajo · Comando · Asignado por), ordenables pulsando el encabezado; por tecla: letras solas A…Z, luego Ctrl+…, Alt+…, Mayús+… (cada uno: combinaciones con otra modificadora, números, letras, símbolos, resto, teclas de función) y al final teclas de función, números, símbolos y el resto sin modificadora. En el centro, todos los comandos (IngeTrazo, cada extensión, Toolkeeper y comandos personales) con su tecla; buscar, «Solo con atajo», imprimir. Panel derecho para cambiar la tecla de cualquier comando: buscador propio, comprobación de si la tecla ya la usa otro (y quién), Asignar (se la quita al otro) y Quitar atajo. Se guarda donde IngeTrazo guarda sus atajos (registro `IngeTrazo\shortcuts`) y Toolkeeper lo aplica al arrancar también a los comandos de extensiones. |
| **Idioma** | Automático (el de IngeTrazo), Español, English o Français; también con el botón 🌐 del gestor maestro. Cambia al momento (menú, barra, barras personalizadas y gestor) y se recuerda en el registro (`IngeTrazo\igz_toolkeeper`, `idioma`), aparte de la configuración, para que importar no lo cambie. |
| **Ayuda** | |

## Instalar

Copia la carpeta `Toolkeeper` a `%APPDATA%\IngeTrazo\plugins\` y reinicia
IngeTrazo. Aparecen la barra **Toolkeeper** y el menú
**Extensiones ▸ Toolkeeper**.

## Datos

`%APPDATA%\IngeTrazo\igz_toolkeeper\igz_toolkeeper.json` y la carpeta `backups\`
al lado (copias `igz_toolkeeper_AAAAMMDD_HHMMSS.json`).

Identificadores internos: objectName `igz_toolkeeper…` (IngeTrazo recuerda
por ellos la posición de las barras), ajustes `QSettings("IngeTrazo",
"igz_toolkeeper")`, `window._igz_toolkeeper` y el MIME
`application/x-igz-toolkeeper` de los arrastres. La clave de extensión, que
IngeTrazo saca del nombre de la carpeta, se fija en `igz_toolkeeper`.

Todos estos identificadores son distintos de los de **Maestro de
Barras-Toolkeeper**, así que las dos extensiones pueden estar instaladas a la
vez sin pisarse (cada una ve a la otra como una extensión más en su árbol).
Toolkeeper no tiene el apartado de barras de otras extensiones: solo barras
personalizadas y comandos personales.

Licencia: GPL-3.0-or-later (la de IngeTrazo).
