# Notas del dueño

Configuración y decisiones propias de este mazo (Yago Mendoza). Nada secreto: el repositorio es público y las claves nunca entran aquí. Quien use el sistema con sus propios apuntes sustituye este archivo por el suyo. Aquí van los valores vigentes y cómo está montado el entorno; el porqué de cada decisión, en `docs/decisions.md`; lo que depende de quién aprende, en `docs/goal.md`.

## Quién estudia y cómo

- Objetivo, nivel y forma de estudiar: `docs/goal.md` (ahí se usan para decidir el contenido).
- Escribe con teclado chino en el móvil (pinyin con tildes o hanzi) y estudia el mazo padre entero, mezclado: las nuevas ya salen nivel a nivel. Sus otros mazos de Anki: regla en `AGENTS.md`.

## Entorno

- Proyecto en `C:\Users\yagom\dev\apkg-chinese-structs`, Python en `.venv`, Windows.
- Grabaciones de clase (`tools/class_audio.py`): entorno aparte `.venv-audio` con Python 3.13 (`py -3.13 -m venv .venv-audio`, luego `pip install -r tools/requirements-audio.txt`). PyAV fijado en 18.1.0 porque Smart App Control de Windows bloquea la DLL de la 19.0.0. La primera vez descarga los modelos (Whisper large-v3 y small en la caché de Hugging Face, unos 3,5 GB; la huella de voz en `.venv-audio/models/`). Todo en CPU: 4 trozos en paralelo, unos 40 minutos para una clase de 73.
- Anki desktop en este PC con AnkiConnect (`2055492159`) y sesión de AnkiWeb iniciada: `push` sincroniza y el móvil recibe los cambios al sincronizar.
- Azure AI Speech: recurso `apkg-chinese-structs`, región North Europe (West Europe no admitía clientes nuevos), nivel **S0**. Clave y región como variables de entorno del usuario de Windows (`AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`). Aviso de presupuesto recomendado: 1 € al mes en Cost Management → Budgets (Azure no permite un tope que corte el gasto en pago por uso). Solo se gasta al ejecutar `anki.py audio`: unos céntimos por lote.

## Decisiones

- Voz `zh-CN-YunyangNeural` (elegida escuchando muestras: clara y estable para fijar tonos); voces HD descartadas por ahora.
- Velocidad: -30 % en frases y -40 % en palabras sueltas, con 200 ms de silencio inicial.
- Ritmo: 30 nuevas y 300 repasos al día (historia en `docs/decisions.md`). Lotes: uno por semana como costumbre, sin obligación. Se cambia en `anki.py`, no a mano en Anki, porque `push` lo vuelve a fijar.
- No se corrige nada dentro de Anki: las correcciones se piden al agente.
- **Fase de pruebas: cerrada.** El progreso de Anki se conserva siempre; `push --reset` se niega (`TESTING_PHASE = False` en `anki.py`) y solo lo haría con `--force` si YAGO lo pide expresamente.
- `1-inbox/history/` se versiona: los apuntes no son privados.
- Licencia: MIT para el código y CC BY 4.0 para el contenido, con cita obligatoria y uso comercial permitido.

## Si algo falla

- **`push` dice que AnkiConnect no responde**: abrir Anki en el PC; si ya estaba abierto, cerrarlo del todo y reabrirlo (el complemento se carga al arrancar).
- **Sin sincronizar**: iniciar sesión en AnkiWeb desde el botón Sincronizar de Anki desktop.
- **El móvil muestra algo viejo**: sincronizar el móvil después de cada `push`.
- **Antes de un lote grande**: sincronizar el móvil primero, para que AnkiWeb tenga los repasos del día antes de que `push` suba cambios (si Anki pidiera una sincronización completa, no se pierde nada del móvil).
- **Un lote salió mal**: volver a la etiqueta del lote anterior (`lote-NNN`) y hacer `push` (ver «Lotes disruptivos» en `docs/design.md`).
- **`audio` falla**: comprobar las variables de entorno (reiniciar la terminal tras cambiarlas) y que el recurso de Azure sigue activo.
- **Pocas tarjetas azules un día**: Anki cuenta las nuevas ya empezadas hoy contra el límite; se puede ampliar solo para hoy (Estudio personalizado → aumentar el límite de nuevas de hoy) o pedirlo al agente.

## Mantenimiento

Cada 4 lotes (el review lo recuerda con su propio apartado) o una vez al mes:

- **Borrar los audios que ya no usa ninguna tarjeta**: en Anki desktop, Herramientas → Comprobar multimedia → Borrar no utilizados. Al cambiar o retirar tarjetas quedan audios huérfanos en la colección; no afecta a ninguna tarjeta ni a ningún progreso, y vale para toda la colección (solo borra lo que nada usa). Antes, sincronizar; después, sincronizar otra vez.
- **Comprobar la base de datos** (Herramientas → Comprobar base de datos) si Anki avisa de algo raro.

## Por comprobar en uso real

- Que el móvil conserva lo escrito entre anverso y reverso (si no, las tarjetas escritas quedan como autoevaluación).

Comprobado: el progreso se conserva al reimportar y al cambiar de subdeck (prueba en este Anki, ver `docs/decisions.md`, 2026-10-01).
