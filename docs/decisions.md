# Decisiones

Por qué el sistema es como es. Cada entrada: qué se decidió, por qué, qué se descartó si hubo alternativa y dónde vive hoy la regla. El detalle de cada lote está en su log (`2-digests/`); aquí solo lo que cambia cómo funciona el sistema.

**Qué va aquí y qué no**

- Va: decisiones sobre reglas, formato, flujo, código o configuración, con fecha. Es un registro histórico: no se reescribe. Si una decisión se revoca, se añade una entrada nueva que lo dice y la antigua lleva al final «(revocada: AAAA-MM-DD)».
- No va: la regla en sí (vive en `docs/design.md`, `docs/goal.md` o `docs/owner.md`, en presente y sin historia), el contenido de un lote (su log) ni cifras que caducan (`anki.py gaps`).
- Los documentos de reglas no llevan fechas ni «desde el…»: quien quiera saber cuándo o por qué, viene aquí.

Cuándo y cómo se cambia una regla: `docs/design.md` (cabecera y «Retrospectiva»).

---

### 2026-09-25 · Repositorio público

Se comprobó que el repositorio es público. Nada privado ni ninguna credencial en lo versionado; push a GitHub solo cuando lo pide YAGO. Vive en: `AGENTS.md`, `docs/design.md` («Repositorio y privacidad»).

### 2026-09-26 · El modelo redacta; el código calcula

Lo que puede calcularse (tarjetas exigidas, redundancia, audio que falta) lo decide `anki.py` a partir de reglas escritas, no el criterio del agente en cada sesión. Motivo: que un modelo mejor mejore el mazo sin cambiar el sistema, y que nada dependa de que el agente se acuerde. Vive en: `docs/design.md` («Principio», «Garantías»).

### 2026-09-26 · Tarjetas por `use`

Cada entrada declara para qué la necesita el que aprende (`read`, `hear`, `say`, `drop`) y de ahí salen sus tarjetas exigidas. Descartado: decidir tarjetas a mano en cada lote. Vive en: `docs/design.md` («Cobertura»).

### 2026-09-26 · Voz y velocidad del audio

Voz `zh-CN-YunyangNeural`, elegida escuchando muestras por ser clara y estable para fijar tonos; frases al -30 %, palabras sueltas al -40 %, 200 ms de silencio inicial (algunos reproductores cortaban el primer instante: 上午 se oía «shòu»). Descartado por ahora: voces HD (más naturales, menos estables en los tonos). Vive en: `docs/owner.md` (valores), `anki.py` (`AZURE_*`).

### 2026-09-27 · Azure S0

Todo el audio se generó en el nivel de pago S0. Motivo: según las condiciones de Microsoft, solo el audio del nivel de pago puede redistribuirse, y el repositorio y la web lo publican. Región North Europe (West Europe no admitía clientes nuevos). Vive en: `docs/owner.md`, `docs/design.md` («Audio»).

### 2026-09-27 · Ritmo de estudio

20 nuevas y 300 repasos al día como máximo (primero fueron 30; 15 se quedaba corto). Un lote por semana como costumbre, sin obligación. Fijado por `push`, nunca a mano en Anki. Vive en: `docs/owner.md`, `anki.py` (`NEW_PER_DAY`, `REVIEWS_PER_DAY`).

### 2026-09-27 · Fase de pruebas

Mientras el sistema no sea estable, el progreso se puede reiniciar a petición (`push --reset`). Cuando YAGO lo dé por estable, el progreso se conserva siempre. Vive en: `docs/owner.md`. (revocada: 2026-10-01)

### 2026-09-27 · Los apuntes se versionan

`1-inbox/history/` entra en git: los apuntes no son privados. Lo que sí es privado (grabaciones, citas de libros, fuentes locales) va a `private/`. Vive en: `docs/owner.md`, `docs/design.md` («Repositorio y privacidad»).

### 2026-09-27 · Licencias

MIT para el código y CC BY 4.0 para el contenido, con cita obligatoria y uso comercial permitido. Lo de terceros (`sources/`) conserva su propia licencia. Vive en: `LICENSE`, `LICENSE-CONTENT`, `README.md`.

### 2026-09-27 · Subdecks por tema, no por fecha

Descartado: subdecks por fecha o por lote (cada uno sería un poco de todo). El lote solo queda como procedencia (`source.batch`). Vive en: `docs/design.md` («Anki»).

### 2026-09-27 · La escucha de palabras es dictado tecleado

Las tarjetas de escucha que solo se autoevaluaban pasaron a dictado (escribir lo oído en pinyin o hanzi), con ID nuevo. Motivo: la autoevaluación no fijaba el pinyin. Vive en: `docs/design.md` («Tarjetas»).

### 2026-09-27 · Comentarios redactados, con su original

Lo que se muestra (`text`) va bien escrito; lo que YAGO apuntó queda tal cual en `original`, que nunca sale de `3-data/`. Vive en: `docs/design.md` («Comentarios»).

### 2026-09-27 · Exportación pública

`anki.py export` produce `5-output/dictionary.json`, el contrato con InfraPhysics. Vive en: `docs/design.md` («Exportación pública»).

### 2026-09-27 · El objetivo, un módulo aparte

Todo lo que depende de quién aprende va en `docs/goal.md`; `docs/design.md` dice cómo funciona y no lleva preferencias personales. Motivo: cambiar de persona u objetivo es reescribir un archivo. Vive en: `docs/goal.md`, `docs/design.md`.

### 2026-09-27 · Seguimiento en cada lote

Cada lote cierra con una reflexión acumulativa (nivel, clases, método, avisos), al final del log y al principio del review. Vive en: `docs/design.md` («Seguimiento»).

### 2026-09-29 · Niveles del HSK 3.0 como primera división

El mazo se ordena por nivel y, dentro, por tema. El HSK es la escala, no la meta. Vive en: `docs/design.md` («Niveles»), `docs/goal.md` («Orden»).

### 2026-09-29 · El pinyin por delante

YAGO investigaba los hanzi tras clase y descuidaba el pinyin; lo nuevo se practica primero oyéndolo y diciéndolo, y el análisis de caracteres va de apoyo. Vive en: `docs/goal.md`.

### 2026-09-29 · Hablar se entrena fuera del mazo

YAGO conversa con su profesora y lee en voz alta todo lo que estudia; el mazo no necesita muchas tarjetas de voz alta y la pista de pronunciación no tiene prisa. Vive en: `docs/goal.md`.

### 2026-09-29 · Cómo se explica un carácter

Palabra, ligada o componente siempre; mnemotecnia separada del origen; series fonéticas; conexiones cruzadas; otros niveles marcados con [HSK n]. Vive en: `docs/goal.md`, `check`.

### 2026-09-29 · «En clase», no «Profesora»

El rótulo de las notas de la profesora en las tarjetas es «En clase» (lo pidió YAGO). Vive en: `docs/goal.md`, `anki.py` (`NOTE_KIND`).

### 2026-09-29 · Citas de libros

Solo se retira la copia literal (entre comillas o con su página); la misma idea con otras palabras se queda, sin nombrar la fuente. Vive en: `docs/design.md` («Repositorio y privacidad»).

### 2026-09-29 · Desván

Lo que no entra pero merece guardarse espera con su contexto y vuelve cuando algo lo despierta. Lo propuso YAGO: «lo que no entró no entra, pero se conserva, y el día que coja colores, que lo arrastre». Vive en: `docs/design.md` («Desván»).

### 2026-09-29 · Gramática visible

Categoría gramatical de cada palabra y estructuras de frase con huecos visibles (propuesta de YAGO). Vive en: `docs/design.md` («Gramática»).

### 2026-09-29 · Mantenimiento de Anki cada 4 lotes

Borrar multimedia no utilizada y comprobar la base de datos; el review lo recuerda. Vive en: `docs/owner.md`, `anki.py` (`MAINTENANCE_EVERY`).

### 2026-09-30 · Grabaciones de clase

Una grabación se transcribe en local (Whisper large-v3, el más preciso para chino; la voz de la profesora separada de la de YAGO) y se usa como contexto del lote, nunca como fuente segura. Ni la grabación ni la transcripción se versionan. Vive en: `docs/design.md` («Grabaciones de clase»), `docs/owner.md` (entorno).

### 2026-10-01 · Nada de producción libre

Las tarjetas «di una frase con esta estructura» se retiraron: obligaban a inventar sin modelo y no educaban. Cada estructura se practica oponiendo la frase buena a un calco erróneo. Vive en: `docs/goal.md`, `docs/design.md` («Gramática»).

### 2026-10-01 · Sonar natural y solo mandarín estándar

El objetivo pasa a ser sonar natural, no solo correcto: lo forzado se corrige con ⚠️. Las formas regionales (erhua del norte, cantonés) no entran ni se mencionan: se descartan. Vive en: `docs/goal.md`, `check` (`standard_rules`).

### 2026-10-01 · Lo que se confunde, contrastado

Grupos `soundalike` con tarjeta que se oye; aviso cuando dos palabras suenan igual sin tonos y no comparten grupo; la pareja aparece en los ejemplos del reverso. Vive en: `docs/goal.md`, `docs/design.md` («Datos», «Garantías»).

### 2026-10-01 · Conexiones entre hanzi, calculadas

Un recuadro de «Conexión» como mucho por tarjeta (🔊 da el sonido, 🧩 da el significado, 👀 se parece pero no tiene que ver), solo con caracteres que ya están en el mazo, y calculado con datos abiertos (Make Me a Hanzi, `sources/hanzi/`, LGPL 3: se usan hechos, no su texto, así que el contenido sigue siendo CC BY), no de memoria. El estatus de un carácter dentro de una palabra se dice solo cuando engaña. Vive en: `docs/goal.md` («Cómo se explica un carácter»), `docs/design.md` («Datos», «Garantías»), `anki.py hanzi`.

### 2026-10-01 · Comprensión lectora

YAGO pidió una tarjeta de leer un texto y, al terminar, responder una pregunta sobre lo leído. Tipo `comprehension`: frases del mazo en un párrafo, en hanzi o con el pinyin encima, nunca solo pinyin (el pinyin es su herramienta para fijar sonidos, no algo que quiera leer); la pregunta plegada, en español o en chino. Reutiliza frases con audio, así que no cuesta audio nuevo. Dos o tres por lote. Descartado: textos nuevos escritos para la tarjeta (piden audio y vocabulario sin comprobar). Vive en: `docs/goal.md` («Cómo se practican las frases»), `docs/design.md` («Tarjetas»).

### 2026-10-01 · Cuánto entra por lote

Tres lotes en una semana trajeron unas 900 tarjetas; a 20 nuevas al día eso es más de un mes y medio de nuevas pendientes, y lo de la última clase sale al final. Criterio: lo que entra en un lote tiene que caber en unas dos semanas de estudio; si sobra, primero lo de clase y lo básico, y lo demás con un `use` más bajo o esperando. Descartado: subir las nuevas al día sin que lo decida YAGO, y quitar tipos de tarjeta (cada uno cubre una capacidad distinta). Vive en: `docs/goal.md` («Cuánto entra»).

### 2026-10-01 · El progreso sobrevive a reimportar y reorganizar (comprobado)

Prueba en el Anki real de YAGO, sobre una tarjeta (`x.read.tianqi`): tras tres repasos (intervalo de 54 días, 3 repasos en el registro), se reimportó dos veces un mazo compilado de nuevo, una con el texto de la tarjeta cambiado y otra con el original, y se movió de subdeck y de vuelta. La nota se actualizó cada vez; tipo, intervalo, vencimiento, facilidad, repasos y registro no cambiaron. Después la tarjeta volvió a nueva. Hasta entonces era una suposición. Vive en: `docs/design.md` («Lotes disruptivos»).

### 2026-10-01 · El review empieza por lo imprescindible

El review creció hasta 159 líneas y el del lote 002 quedó sin una sola respuesta. Se añade arriba «Sine qua non»: lo único que el agente necesita que YAGO conteste, pocas preguntas y con enlace a lo profundo. El resto se queda debajo, porque contestarlo y buscar a partir de ahí es parte de cómo aprende YAGO. Descartado: recortar el review entero. Vive en: `docs/design.md` («Log, review y estado»), `close-batch`.

### 2026-10-01 · Estado vivo en lugar de releer todo

El seguimiento acumulativo obligaba a releer todos los logs y reviews en cada lote, y eso no escala. Ahora hay un estado vivo (`2-digests/state.md`) que se reescribe en cada lote; cada afirmación lleva enlace al log o review de donde sale. El seguimiento se escribe desde el estado y el último log. Vive en: `docs/design.md` («Seguimiento»), `close-batch`.

### 2026-10-01 · Caja negra del proceso

Git guarda qué cambió, no por qué ni qué costó. Tres registros: este archivo (por qué), una sección «Fricciones del proceso» en cada log (qué estorbó al trabajar) y `private/blackbox.jsonl` (cada orden de `anki.py`, con su duración, errores y avisos; fuera de git). Se leen en la retrospectiva cada 4 lotes. Descartado: registrar todo lo que pasa en el repositorio (ruido, nadie lo lee y riesgo de privacidad en un repositorio público). Vive en: `docs/design.md` («Retrospectiva»).

### 2026-10-01 · `stats` antes que la pista de pronunciación

El sistema medía lo que entra, no lo que se queda. `anki.py stats` lee de Anki (solo lectura, solo este mazo) los fallos y lo que cuesta, y el review lo usa como hueco del siguiente lote. Pasa por delante de la pista de pronunciación. Vive en: `docs/design.md` («Lo que se queda: `stats`»).

### 2026-10-01 · Diseño congelado salvo fallo

El sistema crecía más deprisa que el mazo (59 commits en una semana para 3 lotes). Las reglas cambian solo cuando algo falla en uso real o YAGO lo pide, y los cambios de proceso esperan a la retrospectiva. Vive en: `docs/design.md` («Retrospectiva»).

### 2026-10-01 · Fin de la fase de pruebas

YAGO cierra la fase de pruebas: desde hoy el progreso de Anki se conserva siempre. Ya estaba comprobado que reimportar y reorganizar no lo tocan, y en Anki casi todo estaba como nuevo, así que no se perdía nada. `push --reset` se niega salvo `--force` (`TESTING_PHASE = False`), para que un reinicio no pueda pasar por descuido. Vive en: `docs/owner.md`, `docs/design.md` («Anki»).

### 2026-10-01 · 30 nuevas al día

Con 1.088 nuevas pendientes (unos 54 días a 20 al día), YAGO sube a 30 nuevas al día; los repasos siguen con un máximo de 300. A ritmo estable son unos 150 a 240 repasos al día, unos 40 minutos. Sigue valiendo el criterio de volumen: los próximos lotes, más ligeros. Vive en: `docs/owner.md`, `anki.py` (`NEW_PER_DAY`).

### 2026-10-02 · Lo fallado vuelve en minutos

YAGO notó que una tarjeta fallada no volvía hasta el día siguiente: el preset tenía un solo paso de 1 día para nuevas y para fallos. Ahora `push` fija pasos de 1 y 10 minutos para las nuevas y de 10 minutos para las falladas, solo en el preset de este mazo. Así se fija en la misma sesión, que es cuando más rinde para un idioma. El límite de nuevas se queda en 30: para un día con más ganas, Estudio personalizado (aumentar las nuevas de hoy) sin subir el límite fijo, que con días irregulares acumularía repasos. Descartado por ahora: activar FSRS, que es un ajuste de toda la colección y afectaría a los otros mazos de YAGO; si lo quiere, lo activa él. Vive en: `docs/owner.md`, `anki.py` (`LEARN_STEPS`, `RELEARN_STEPS`).

### 2026-10-02 · Las nuevas, en el orden calculado

YAGO vio salir 大家 (HSK 2) entre las primeras. Las posiciones estaban bien calculadas, pero el preset recogía las nuevas al azar (notas y tarjetas al azar), así que Anki ignoraba el orden: mezclaba niveles y juntaba tarjetas de una misma palabra. Ahora `push` fija «posición más baja» y «sin reordenar» (comprobado en el código de Anki: gather 1, sort 1); la primera nueva pasó a ser 你好. Vive en: `docs/design.md` («Anki»), `anki.py` (`ensure_limits`).

### 2026-10-02 · Rutina de YAGO

Clases martes y jueves; de 20 a 40 minutos al día, hasta hora y media algunos días; puede hablar en voz alta siempre. Los lotes, mejor justo después de clase, dos a la semana y ligeros. Vive en: `docs/goal.md` («Quién aprende»).

### 2026-10-02 · Más comprensión lectora y parejas de tonos

YAGO vio pequeños los tipos minoritarios. Mirados contra su objetivo, y contando lo que ya refuerzan los reversos (985 apariciones de frases de ejemplo, 313 reversos con su grupo de contraste), lo flojo era la comprensión lectora (6 tarjetas; es lo único que entrena leer chino seguido) y los tonos de dos sílabas. Entran 24 tarjetas de comprensión con frases que ya había (sin audio nuevo) y la primera parte de la pista de pronunciación: las 20 parejas de tonos, con dos palabras cada una (27 tarjetas nuevas; las demás ya existían por neutro o sandhi). La «voz alta» ya era grande: las 128 tarjetas «decir» de frases se dicen en voz alta, y ahora `gaps` las cuenta así. Descartado: quitar las lecturas sueltas de palabras de función, que al empezar, en el HSK 1, sí ayudan (lo dijo YAGO). Vive en: `docs/design.md` («Pronunciación», «Cobertura»), `docs/goal.md` («Cómo se practican las frases»).

### 2026-10-02 · El mazo, dentro de «🀄 Chinese»

YAGO movió el mazo en Anki a su carpeta `🀄 Chinese`. Un `push` hecho justo después con la ruta antigua lo devolvió a la raíz (recreó el árbol viejo y movió allí las tarjetas, sin perder progreso); se corrigió `DECK_NAME` a `🀄 Chinese::🐉 Chino práctico`, se recolocaron las 1215 tarjetas y se borró el árbol viejo, ya vacío. Lección: si el mazo se mueve en Anki, primero `DECK_NAME`. Vive en: `anki.py` (`DECK_NAME`), `docs/owner.md`.
