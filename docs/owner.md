# Notas del dueño

Configuración y decisiones propias de este mazo (Yago Mendoza). Nada secreto: el repositorio es público y las claves nunca entran aquí. Quien use el sistema con sus propios apuntes sustituye este archivo por el suyo.

## Quién estudia y cómo

- Objetivo, nivel y forma de estudiar: `docs/design.md`, «Objetivo» (ahí se usan para decidir el contenido).
- Escribe con teclado chino en el móvil (pinyin con tildes o hanzi) y estudia el mazo padre mezclado. Sus otros mazos de Anki (HSK, Pimsleur, Spoonfed…) son práctica aparte: no se tocan ni se cuentan.

## Entorno

- Proyecto en `C:\Users\yagom\dev\apkg-chinese-structs`, Python en `.venv`, Windows.
- Anki desktop en este PC con AnkiConnect (`2055492159`) y sesión de AnkiWeb iniciada: `push` sincroniza y el móvil recibe los cambios al sincronizar.
- Azure AI Speech: recurso `apkg-chinese-structs`, región North Europe (West Europe no admitía clientes nuevos), nivel **S0** desde el 2026-09-27. Clave y región como variables de entorno del usuario de Windows (`AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`). Aviso de presupuesto recomendado: 1 € al mes en Cost Management → Budgets (Azure no permite un tope que corte el gasto en pago por uso). Solo se gasta al ejecutar `anki.py audio`: unos céntimos por lote.

## Decisiones

- Voz `zh-CN-YunyangNeural` (elegida escuchando muestras: clara y estable para fijar tonos); voces HD descartadas por ahora.
- Velocidad: -30 % en frases y -40 % en palabras sueltas, con 200 ms de silencio inicial.
- Ritmo: 30 nuevas y 300 repasos al día (15 se quedaba corto). Se cambia en `anki.py`, no a mano en Anki, porque `push` lo vuelve a fijar.
- No se corrige nada dentro de Anki: las correcciones se piden al agente.
- **Fase de pruebas**: mientras el sistema no sea estable, se reinicia el progreso a petición (`push --reset`). Cuando lo sea, el progreso se conserva.
- `2-raw/` se versiona: los apuntes no son privados.
- Licencia: MIT para el código y CC BY 4.0 para el contenido, con cita obligatoria y uso comercial permitido (2026-09-27).

## Si algo falla

- **`push` dice que AnkiConnect no responde**: abrir Anki en el PC; si ya estaba abierto, cerrarlo del todo y reabrirlo (el complemento se carga al arrancar).
- **Sin sincronizar**: iniciar sesión en AnkiWeb desde el botón Sincronizar de Anki desktop.
- **El móvil muestra algo viejo**: sincronizar el móvil después de cada `push`.
- **Antes de un lote grande**: sincronizar el móvil primero, para que AnkiWeb tenga los repasos del día antes de que `push` suba cambios (si Anki pidiera una sincronización completa, no se pierde nada del móvil).
- **Un lote salió mal**: volver a la etiqueta del lote anterior (`lote-NNN`) y hacer `push` (ver «Lotes disruptivos» en `docs/design.md`).
- **`audio` falla**: comprobar las variables de entorno (reiniciar la terminal tras cambiarlas) y que el recurso de Azure sigue activo.
- **Pocas tarjetas azules un día**: Anki cuenta las nuevas ya empezadas hoy contra el límite; se puede ampliar solo para hoy (Estudio personalizado → aumentar el límite de nuevas de hoy) o pedirlo al agente.

## Por comprobar en uso real

- Que el móvil conserva lo escrito entre anverso y reverso (si no, las tarjetas escritas quedan como autoevaluación).
- Que el historial de repaso se conserva al reimportar, cuando termine la fase de pruebas.
