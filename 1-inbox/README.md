# inbox

Apuntes en bruto de YAGO: un `.txt` por lote, sin formato (palabras de clase, dudas, frases, lo que dijo la profesora). Nombre sugerido: `AAAA-MM-DD-tema.txt`.

Después, pedir al agente «procesa el inbox». El agente edita `3-data/`, pregunta lo dudoso, deja fuera lo privado, mueve los `.txt` a `2-raw/<lote>/` y resume los cambios. Aquí solo queda lo pendiente y, tras cada lote, un gaps-<lote>.md editable con lo que falta: escribe encima y entra en el siguiente lote. Procedimiento completo: `docs/design.md`, «Flujo de un lote».

Lo pendiente de `1-inbox/` no se versiona; al procesarlo pasa a `2-raw/<lote>/`, que sí se versiona.
