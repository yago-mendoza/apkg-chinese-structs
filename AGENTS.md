# Trabajo en este repositorio

Leer `docs/design.md` antes de implementar o añadir contenido: diseño canónico, repertorio de ejercicios y decisiones pendientes. El mapa de carpetas y las convenciones de nombres están en `README.md`. No duplicar ninguno de los dos aquí.

- Entorno: local en Windows, `C:\Users\yagom\dev\apkg-chinese-structs`, Python en `.venv` (`.\.venv\Scripts\python anki.py ...`). No instalar dependencias fuera de `.venv`.
- Prioridad: mandarín cotidiano y práctico, pinyin y tonos, audio en respuestas y ejemplos. YAGO está empezando.
- Solo el agente edita `3-data/`. YAGO escribe en `1-inbox/` y saca resultados de `5-output/`.
- Antes de añadir contenido: `anki.py lookup <término>` y `anki.py gaps`. Después: `anki.py check`. Revisar los avisos; no ignorarlos ni aceptarlos automáticamente (`accept_pinyin_mismatch` solo con motivo).
- «Procesa el inbox»: seguir «Inbox: entrada por lotes» de `docs/design.md`. No cambiar el hanzi de respuestas o frases con audio salvo error (ver «Estabilidad»).
- Distinguir objetivo evaluado (`targets`), contexto (`context`) y ejemplo revelado (`reveal`).
- El LLM redacta y revisa; la compilación consume contenido guardado sin llamar a un LLM. No regenerar ejercicios al compilar.
- Preservar IDs y comentarios personales literalmente. Guardar cada comentario en el ámbito que describe; separar mnemotecnia, profesora y explicación verificada.
- Trabajar incrementalmente. No implementar publicaciones, rankings completos o servicios anticipados.
- Nombres: carpetas y archivos en inglés; documentación de carpeta siempre `README.md`, nunca traducida.
- UTF-8 explícito en archivos y ejecución de Python sobre Windows.
- El repositorio es público (comprobado 2026-09-25): no guardar comentarios privados ni credenciales. Revisar cambios antes de subirlos; no hacer push sin que YAGO lo pida.
- No elegir una licencia de publicación en nombre de YAGO. Mantener procedencia y condiciones de recursos externos.
- La colección de Anki de YAGO tiene otros mazos descargados (HSK, Pimsleur, Spoonfed…): son práctica aparte, independientes de este proyecto. No modificarlos ni borrarlos y no contarlos en ninguna métrica. Hoy no son fuente; más adelante (hacia HSK 7) podrán servir para explorar vocabulario, solo cuando YAGO lo pida, y lo elegido entra como un lote más. Toda operación en Anki se limita al mazo `🐉 Chino práctico`.
- Verificar en Anki antes de afirmar que se preserva el progreso.
