# sources/hsk

Lista de vocabulario del HSK 3.0 (versión de 2021), para situar cada palabra en su nivel y ver huecos. Es una señal, no una fuente: nada entra al mazo por estar aquí.

- `hsk3.tsv`: una fila por palabra: `level` (1–6; el 7 agrupa los niveles 7, 8 y 9, que comparten lista), `freq_rank` (rango de frecuencia que trae la lista de origen; menor es más frecuente) `hanzi` y `pinyin` (varias lecturas separadas por ` / `) y `pos` (categorías gramaticales en notación de corpus, v, n, a, d, q, r…, separadas por comas, la principal primero; añadida el 2026-09-29 desde el mismo origen y commit). Ordenada por nivel y frecuencia.
- Origen: [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary), `wordlists/exclusive/new/`, commit `7ac65bf1a638`, descargada el 2026-09-27. Licencia MIT, en `LICENSE` (se conserva con el archivo).
- No se copian sus glosas en inglés (vienen de CC-CEDICT, con otra licencia) ni sus variantes tradicionales.
- Para actualizarla, el agente la vuelve a generar desde el origen y anota aquí el commit nuevo.
