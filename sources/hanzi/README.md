# sources/hanzi

Descomposición de unos 9.500 caracteres: de qué piezas se forma cada uno y, en los fonético-semánticos, qué pieza da el sonido y cuál el significado. Es una herramienta del agente para explicar los hanzi con datos y no de memoria (`anki.py hanzi <caracteres>`, y el aviso de series fonéticas de `check`). Nada entra al mazo por estar aquí, y no se copia su texto: lo que llega a las tarjetas son hechos («青 da el sonido a 请») redactados con palabras propias.

- `dictionary.txt`: una línea JSON por carácter. Se usan `character`, `decomposition` (descripción de piezas, como `⿰讠青`), `radical` y `etymology` (`type`: `pictophonetic`, `ideographic` o `pictographic`; `phonetic` y `semantic` en los fonético-semánticos; `hint`). No se usan sus glosas en inglés.
- Origen: [skishore/makemeahanzi](https://github.com/skishore/makemeahanzi), `dictionary.txt`, commit `bddc96d41bef`, descargado el 2026-10-01. Derivado de Unihan y CJKlib.
- Licencia: GNU LGPL 3 o posterior, en `LGPL`, con el aviso original en `COPYING`. Se conserva el archivo sin modificar.
- Ojo: es una fuente secundaria. Si choca con lo que se sabe del carácter (algunas etimologías son discutidas), manda la fuente verificada y se dice en el log.
- Para actualizarlo, el agente lo vuelve a descargar del origen y anota aquí el commit nuevo.
