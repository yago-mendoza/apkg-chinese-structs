# 2-digests

El log de cada lote (`summary-<lote>.md`), escrito por el agente al procesarlo: qué entró, qué no y por qué, correcciones y reorganizaciones. Es el análisis de ese lote; la base de conocimiento está en `3-data/`.

No se reescribe. Si algo se corrige después, el cambio va a `3-data/` y aquí se añade al final una línea en «Cambios posteriores» con la fecha. Para opinar sobre un lote: su review en `1-inbox/`.

`state.md` es otra cosa: el estado vivo (nivel, clases, método, avisos y decisiones abiertas), que el agente reescribe en cada lote. Cada punto enlaza al log o al review archivado de donde sale, para ir a lo profundo cuando haga falta. Reglas: `docs/design.md`, «Log, review y estado».
