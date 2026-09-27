# inbox

Apuntes en bruto: cualquier archivo, con o sin extensión, sin formato (palabras de clase, dudas, frases, lo que dijo la profesora). Conviene poner la fecha de lo apuntado al principio, o al principio de cada parte si un archivo mezcla días.

Después, pedir al agente «procesa el inbox». El agente edita `3-data/`, pregunta lo dudoso, deja fuera lo privado, mueve los apuntes a `2-raw/<lote>/` y resume los cambios. Aquí solo queda lo pendiente y, tras cada lote, un gaps-<lote>.md editable con lo que falta: escribe encima y entra en el siguiente lote. Procedimiento completo: `docs/design.md`, «Flujo de un lote».

Lo pendiente de `1-inbox/` no se versiona; al procesarlo pasa a `2-raw/<lote>/`, que sí se versiona.
