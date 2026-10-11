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

Tres lotes en una semana trajeron unas 900 tarjetas; a 20 nuevas al día eso es más de un mes y medio de nuevas pendientes, y lo de la última clase sale al final. Criterio: lo que entra en un lote tiene que caber en unas dos semanas de estudio; si sobra, primero lo de clase y lo básico, y lo demás con un `use` más bajo o esperando. Descartado: subir las nuevas al día sin que lo decida YAGO, y quitar tipos de tarjeta (cada uno cubre una capacidad distinta). Vive en: `docs/goal.md` («Cuánto entra»). (revocada: 2026-10-02)

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

### 2026-10-02 · Cada hanzi del mazo tiene su porqué

`3-data/hanzi.yaml` guarda, para cada carácter que aparece en el mazo (también los que solo viven dentro de palabras, como 足 y 球 de 足球), su glosa, su origen redactado con palabras propias (pictograma, ideograma, fonético-semántico o «sin historia: se usa por su sonido»), la forma tradicional cuando la simplificada esconde el dibujo y una confianza (`medium` si el origen es discutido); y `parts`, qué significa cada pieza. Lo calculable (tipo, piezas, cuál da el sonido y cuál el significado, si el sonido se parece) sigue saliendo de `sources/hanzi`; cuando la fuente choca con lo comprobado, la entrada lo corrige con `type`/`phonetic`/`semantic` y su `override` (el porqué), y la ficha muestra lo corregido. La exportación lo lleva como `characters` (el cuaderno web: la ficha flotante y «Sus caracteres»). `check` avisa del hanzi sin porqué y del que sobra. No genera tarjetas: el análisis va de apoyo en el reverso, en la sección «Sus caracteres» («Por qué se escribe así» si la palabra es un solo carácter). Los grupos del reverso pasan a filas por columnas (hanzi, pinyin, significado, pista), sin raya. Pedido por YAGO para que «llegue a la raíz de las cosas». Vive en: `3-data/README.md` (esquema), `docs/goal.md` («Cómo se explica un carácter»), `anki.py` (`export_characters`, `character_lines`).

### 2026-10-02 · La imagen para recordar un hanzi, aparte de su origen

`3-data/hanzi.yaml` admite `memory: {es, en}`: una imagen para recordar el carácter desde su forma de hoy (再 como algo que se pesa dos veces). Se muestra siempre rotulada «Para recordarlo (no es su origen)», en la ficha del cuaderno y en el reverso de las tarjetas de un solo carácter, para que nunca se confunda con la historia de la forma antigua. Los orígenes de confianza media se repasaron a mano: los que la consulta confirmó suben a `high`; donde hay dos lecturas, el texto dice las dos. Vive en: `3-data/README.md`, `anki.py` (`export_characters`, `character_lines`).

### 2026-10-02 · Lo discutido no se cuenta; los componentes dicen la palabra de verdad

YAGO, al ver la ficha de 再 en el cuaderno: «si es discutido, no lo digas»; la imagen para recordarlo, en cambio, le pareció de lo más útil. Un origen con `confidence: medium` y sin corrección comprobada ya no sale ni en el reverso ni en la web (ni su historia ni su tipo); queda la glosa y la imagen para recordar. Además, lo mínimo de cada carácter en el reverso de las palabras: qué significa, una frase y dónde más sale en el mazo (再 → 再说一遍). Los componentes dicen cuál es la palabra de verdad (`real_word`): 目 no es «ojo» al hablar, es 眼睛. Al revisarlo apareció un error de verdad: el mazo decía que 口 suelto es «boca» (al hablar es 嘴) y que 月 es «luna» (es «mes»; la luna es 月亮); corregido, también en la teoría. Las tarjetas de un hanzi solo enseñan qué otros caracteres suenan igual y qué otros sentidos tiene, y la teoría explica que un carácter casi siempre tiene un solo sonido (con los polifónicos como excepción) y una sílaba, muchos caracteres. Vive en: `docs/goal.md` («Cómo se explica un carácter»), `docs/design.md` («Comentarios», «Garantías»), `3-data/theory.yaml` (`t.polyphones`).

### 2026-10-02 · La mejor configuración para su memoria

YAGO pidió la mejor configuración posible y dejó claro que no quiere limitar lo que entra: avanza, aprende cosas laterales y quiere seguir metiéndolas en el diccionario, con Anki en paralelo. Se simularon 120 días con sus hábitos (6 de 7 días, 20 a 40 minutos, un día largo por semana, rachas sin estudiar, dos lotes semanales). Resultados, en tarjetas que recordaría con al menos un 90 % al final: la configuración que tenía (graduar a 7 días, «Fácil» a 14, un fallo a 3 días) se quedaba en un 69 % de acierto en los repasos y unas 840 sabidas; la estándar (1 día, 4, fallo a 1) sube a un 86 % y unas 920; FSRS con retención del 90 %, a un 88 % y unas 1270, con el mismo tiempo. Lo que limita es su tiempo, no el número de nuevas: absorbe unas 12 a 15 al día de media.

Decidido, con los principios de la memoria detrás: el primer repaso al día siguiente, tras dormir; un fallo, también al día siguiente; repasos antes que nuevas, para que un día corto no deje caer lo que ya se aprende; entre los repasos, primero los que más se están olvidando; retención del 90 % (el 85 % ahorra poco y deja bastante menos sabido); FSRS, que programa cada tarjeta según la memoria real en vez de multiplicar por una cifra fija (lo activa YAGO: es para toda la colección). No se limita lo que entra: se prioriza lo que sale, lo que se va a decir antes que lo que se va a oír o solo a reconocer. Revoca «Cuánto entra por lote». Vive en: `anki.py` (`ensure_limits`, `new_card_order`), `docs/goal.md` («Qué entra y qué sale primero»), `docs/design.md` («Anki»), `docs/owner.md`.

### 2026-10-05 · La pareja, rotulada; preguntas que se pueden contestar

YAGO vio en la tarjeta de 十 la frase 我不是中国人，我是西班牙人 y en la de 要 la de 我很喜欢我的工作, y pensó que los ejemplos se elegían mal. Era la regla «lo que se confunde aparece junto»: la frase de la pareja (是, 喜欢) iba mezclada con los ejemplos sin decir por qué. Ahora va aparte, «Para no confundirlo con 是 shì». En el mismo lote pidió: quitar las preguntas que piden describir un sonido («¿cómo suena…?», «la lengua…») y cambiarlas por preguntas con respuesta; tarjetas de oír una sílaba y elegir (shì / chī, sì / cì, zh / z, j / x, -n / -ng), «de lo más importante»; tarjetas de situación con la respuesta hecha (对不起, 没关系, 不客气, 你回来了); el pinyin en las respuestas de matiz; el audio entero en los huecos; y separar el análisis del carácter del uso (comentario `character`). De su review del lote 004: lo tradicional queda fuera (哪里哪里), lo que sale dentro de los ejercicios de clase cuenta como de clase, y un ID repetido detiene `check` y `scaffold`. Notó también que llevaba dos días con solo tarjetas de leer: era cierto (cada paso iba dos temas por detrás del anterior); ahora va uno. Vive en: `anki.py` (`partner_example`, `annotate_pinyin`, `duplicate_ids`), `docs/goal.md` («Filtro de lo que entra», «Cómo se practican las frases»), `docs/design.md` («Tarjetas», «Comentarios»).

### 2026-10-05 · Cada hanzi difícil, con su imagen para recordarlo

YAGO preguntó si el mazo inventa mnemotecnias propias para los hanzi difíciles de recordar, y lo pidió como «importantísimo». No era una norma: solo 30 de 258 caracteres tenían imagen para recordarlo. Ahora lo es: todo hanzi cuyo porqué no ayuda (origen discutido, que no se cuenta, o usado solo por su sonido) lleva una, inventada desde su forma de hoy y rotulada como imagen, nunca como origen; `check` avisa si falta. Se escribieron las 44 que faltaban. Vive en: `docs/goal.md` («Cómo se explica un carácter»), `anki.py` (`needs_memory`), `3-data/hanzi.yaml`.

### 2026-10-06 · Una app para revisar, y la historia por lotes

YAGO quería ver cómo va todo a la vez: abrir las tarjetas del mazo, saber qué entrada respalda cada una y cuándo cambió qué. Como el repositorio trabaja por lotes explícitos (lo que entra en la bandeja se procesa de golpe), el eje del tiempo son los lotes y los ajustes entre lotes, no las horas. La historia no se guarda: sale de git cada vez, porque git ya la tiene entera. Lo único que se guarda es lo que solo YAGO sabe (su visto bueno, sus pedidos), en `records/`, versionado: YAGO lo quiso visible en el repositorio aunque sea público. Las relaciones entre elementos (qué provocó el cambio o el nacimiento de qué) se deducen de los datos donde se puede (una tarjeta nace de su entrada) y se apuntan al atender un pedido; no se inventan.

### 2026-10-06 · Materiales de clase, cuaderno de deberes y a qué nivel se arregla

YAGO pidió que cada lote revise la carpeta de materiales de clase, recuerde qué se procesó y resuelva los ejercicios para sacar de las soluciones frases y vocabulario; un documento fijo en el inbox para lo que anota al hacer los deberes; y que ante cada sugerencia se busque el nivel del arreglo (una nota, cómo se muestra, el tipo de tarjeta y, casi nunca, el esquema, sin romper el cuaderno web). Además, `close-batch` comprueba ahora los nombres privados antes de archivar: en el lote 005 los comprobaba después y uno llegó al commit. Vive en: `docs/design.md` («Flujo de un lote»), `anki.py` (`materials`, `HOMEWORK`, `close_batch_plan`), `1-inbox/README.md`.

### 2026-10-06 · Hanzi sueltos con su sílaba

YAGO propuso asociar hanzi sueltos con su sonido, porque el mazo le hace leer mucho. Para no inflarlo, solo los que salen en dos o más palabras del mazo y no son palabra propia: 34 al empezar (学, 们, 怎, 么, 机…), y más a medida que crece el mazo, que es lo que pidió. El hanzi suelto no lleva audio (la voz sintética leería mal 什 o 么); suenan sus palabras. Vive en: `anki.py` (`char_sound_picks`, tipo `charsound`), `docs/design.md` («Tarjetas»), `docs/goal.md` («Cómo se explica un carácter»).

### 2026-10-06 · Sin app de revisión: solo la historia

La app de revisión del mismo día se quitó. Aquí siempre edita el agente y YAGO no aprueba nada: su opinión llega por la bandeja, así que un visto bueno por tarjeta, los pedidos y el aviso de por revisar duplicaban lo que ya hace el lote. Se queda lo que sí aporta, la historia de cada elemento por lote, escrita en `records/history.json` al cerrar cada lote, para poder ver si un lote se ensaña con unas pocas tarjetas o crea demasiado a partir de una entrada.

### 2026-10-07 · Las expresiones, palabra a palabra

YAGO pidió entender las expresiones hechas a través de las palabras que las forman, con su traducción literal, y no solo de memoria. Ahora toda expresión lleva una línea «Palabra a palabra», y `check` avisa si falta. Vive en: `docs/goal.md` («Cómo se explica un carácter»), `anki.py` (`validate`).

### 2026-10-09 · `push` toca solo las nuevas que cambian de sitio

Tras subir el lote 008, 98 tarjetas que YAGO estaba aprendiendo en el móvil (en sus pasos de minutos; las 29 de HSK 2 y las 20 de HSK 3 que empezó entrando en esos subdecks, y 64 de HSK 1, entre otras) volvieron a nuevas. Ninguna ya aprendida se tocó. La causa probable: el móvil no había sincronizado lo estudiado; en el ordenador seguían nuevas, y `push` les cambió la posición, como a todas las nuevas en cada subida (las numeraba seguidas desde la más baja, así que cualquier inserción o cambio de base las movía todas). Al sincronizar, Anki se quedó con la versión modificada más tarde, la del ordenador. Comprobado: las 131 tarjetas nuevas con repasos en el registro se modificaron todas en la subida del lote 008. Ahora `push` deja quietas las nuevas que ya están en buen orden entre sí, mueve solo las demás a los huecos entre sus vecinas y, cuando tiene que renumerar, deja `NEW_DUE_GAP` entre posiciones para que lo de los lotes siguientes quepa sin desplazar nada; a igualdad, se quedan quietas las primeras de la cola, que son las que se están estudiando. YAGO lo pidió. Además, el procedimiento de sincronización de los dispositivos queda escrito en `docs/owner.md`. Vive en: `anki.py` (`new_due_plan`, `reorder_new`), `docs/design.md` («Anki» y «Garantías»), `docs/owner.md` («Sincronizar sin perder nada»), pruebas en `tests/`.

### 2026-10-09 · Cada cosa, una vez por tarjeta

YAGO pidió una crítica del mazo con lo que le importa (pronunciación intuitiva, el porqué de los hanzi, contrastes) y sin saturar las notas con lo mismo en muchos sitios. Medido sobre las 2150 tarjetas, la tarjeta típica estaba bien (3 o 4 apartados), pero la repetición era sistemática: el apartado «Para no confundirlo con…» salía en 416 tarjetas y su pareja estaba siempre ya en un recuadro encima; 149 de 209 pistas de los recuadros repetían el pinyin o el significado de su fila; 16 hanzi tenían dos imágenes para recordar en la misma tarjeta (casi siempre la suya y la del sistema); 32 tarjetas contrastaban la misma pareja en dos recuadros; y unos 30 comentarios repetían un recuadro. Ahora: la frase de la pareja va en su fila; cada pista dice solo lo que separa (164 reescritas; `check` avisa); su propia imagen, o su análisis del carácter, sustituye a la del sistema en esa tarjeta, sin borrar nada de `hanzi.yaml`; una tarjeta de matiz no repite su respuesta en recuadros, una de contraste trae solo el suyo y un recuadro contenido en otro no se repite; los comentarios que solo repetían un recuadro se quitaron y los que mezclaban se recortaron. La línea de AFI deja las tarjetas: la pronunciación intuitiva la dan las notas en palabras; sigue en el cuaderno y la web. Contó también que en las tarjetas de decir no teclea: responde de cabeza, mira y se puntúa; el 71 % de «Otra vez» es su propia nota, no un efecto de teclear. Vive en: `anki.py` (`partner_example`, `covered_groups_dropped`, `cue_repeats`, `memory_chars`), `docs/design.md` («Ejemplos automáticos», «Grupos», «Garantías»), `3-data/lexicon/`.

### 2026-10-09 · Equilibrio medido: tope por palabra, mezcla de lo que viene y cola

YAGO preguntó si las tarjetas por palabra y las proporciones no deberían estar indicadas y luego comprobadas. Las tarjetas por palabra ya se dirigían al escribir (`use` fija la base y `scaffold` solo genera esa), pero los extras se acumulaban sin tope (十 tenía 10, 要 9) y ninguna proporción estaba escrita. Ahora: el presupuesto es su tiempo y la cifra que se cuida son las palabras nuevas al día; tope de 6 tarjetas por palabra para lo que entre desde hoy (lo anterior lleva progreso y se queda), con `accept_cards` si un extra se justifica; la mezcla se mide en las próximas 400 nuevas, no en el mazo (oír ≥ 1/3, decir ≥ 1/4, leer ≤ 1/4, otros ≤ 1/4; hoy, 40, 28, 15 y 17 %); y la cola de su nivel avisa por encima de 21 días (hoy, 47). Todo sale solo en `stats` y en el review de cada lote. Las primeras cifras reales: unos 14 minutos y 15 nuevas por día de estudio, 9,5 palabras nuevas. Escalonar las tarjetas de decir tras las de leer y escuchar cambia cómo estudia: queda como decisión suya en el próximo review. Vive en: `docs/goal.md` («Cuánto y en qué proporción»), `anki.py` (`balance_report`, `balance_section`, `cards_per_item`), `docs/design.md` («Lo que se queda», «Review», «Garantías»).

### 2026-10-10 · Tarjetas que se puntúan de cabeza, huecos, parejas que suenan juntas y nuevas siempre mezcladas

El review 008 trajo, en «Tus notas», una crítica del diseño: casi no le salían huecos ni traducciones ni situaciones; las tarjetas de «¿cuándo cada uno?» con seis opciones y un párrafo detrás no se pueden puntuar («bórralas»); las parejas de sílabas sonaban de una en una, sin la otra para comparar («si no puedo contrastar de oído en una misma tarjeta, no me sirve»), y las pasaba con «fácil» sin saberlas; las de «lee en voz alta» con el pinyin delante no aportan, porque ya imita cada audio; la teoría de pronunciación la quiere como preguntas directas y en corto, sin tanto texto debajo; el reverso, de más a menos importante; y el grupo entero de las palabras de pregunta debajo de 谁 «extralimita el propósito de la tarjeta». Después: «el mazo siempre debe estar mezclado en términos de tipo de tarjeta». Visto en Anki: las primeras 100 nuevas no traían ninguna de decir, porque el orden por pasos y temas hacía bloques de un solo tipo. Decidido: las nuevas se mezclan siempre por lo que entrenan, en proporción y calculado sobre las que siguen nuevas (la primera subida lo calculaba con todas, y como casi todas las de leer del principio ya estaban vistas, la pronunciación quedaba en bloque al frente: ahora va en su propia cola, repartida, más o menos 1 de cada 10), con los pasos de una palabra separados un día de estudio (resuelve también la decisión pendiente de escalonar decir tras leer y oír); una tarjeta pide una cosa con respuesta corta (aviso por encima de 160 caracteres), y los 13 matices de párrafo pasan a situaciones y huecos; varios huecos por regla, cada uno en su frase, con las opciones en la consigna; las parejas para oír suenan las dos en la misma tarjeta (las 24 tarjetas de una sílaba pasan a 12 de pareja, más 出 / 去 y el sandhi de 一 y 不); las de «lee en voz alta» de pronunciación pasan a preguntas directas (`x.rule.`) y se añaden vocales para oír y completar; el reverso se ordena por importancia, con hasta tres ejemplos con audio y la sílaba de cada carácter; fuera de su tarjeta, un grupo de más de cuatro no se muestra. Las respuestas por defecto del review 008 que se aplican: nada de un nivel superior en los recuadros (las notas que nombran una palabra de más arriba siguen marcadas con «[HSK n]», 24 de 458, y se pregunta qué hacer con ellas), cuatro o cinco diálogos por lote, «Tus notas» del review como sitio oficial de sus apuntes (`homework-feedback.md` queda como cuaderno opcional) y `sense_level` para fijar el nivel de un sentido (entra 王 apellido). Se borran 56 tarjetas sustituidas; casi ninguna tenía repasos. Vive en: `docs/goal.md` («Cuánto y en qué proporción», «Cómo se practican las frases»), `docs/design.md` («Tarjetas», «Anki», «Datos», «Niveles», «Garantías»), `anki.py` (`new_card_order`, `interleave_streams`, `card_fields`, `validate`). (revocada en parte: 2026-10-11, las preguntas de teoría de pronunciación)

### 2026-10-10 · Sin cuaderno de deberes

En el review 008, YAGO contestó que `homework-feedback.md` «se puede borrar»: nunca lo usó y sus apuntes llegan siempre en «Tus notas» del review. El lote 009 lo había dejado como cuaderno opcional; al repasar el review después del cierre se vio que no era lo que pidió. Decidido: se quita el archivo y su manejo en `close-batch`; los apuntes entre clases y de los deberes van en «Tus notas» del review abierto. Vive en: `docs/design.md` («Flujo de un lote»), `1-inbox/README.md`, `anki.py` (`close_batch_plan`).

### 2026-10-11 · La teoría de pronunciación sale de las tarjetas

En las notas del review 009, YAGO escribió que había pasado a un cuaderno de papel todo lo que es teoría de pronunciación y que no quiere tarjetas dedicadas a ella ni reversos que se paren en explicar cuándo un tono suena como otro: «erradícalas». Lo de oír, en cambio, sí, y mucho. Pidió además que nada de la lista de reglas que el agente le había resumido en el chat (sandhi de 一 y 不, terceros tonos, aspiración, las tres familias de sibilantes, las vocales, -n y -ng) conste en ninguna tarjeta. Una de esas explicaciones, además, repetía la misma sílaba dos veces en un reverso. Decidido: se borran las 18 preguntas de regla (`x.rule.`) y las tarjetas de teoría de oído (¿con qué tono suena 不?, ¿cuántas sílabas oyes?, ¿cuál lleva soplo?, 你好 escrito frente a oído, y la pareja 一本 / 一个, que pidió borrar, con la de 不是 / 不好); el reverso ya no muestra la regla de las entradas `p.` ni las trampas del pinyin, que se quitan del código; las parejas para oír, los dictados, las vocales para completar y las tarjetas de tonos se quedan, sin la regla; las notas que solo explicaban un cambio de tono se quitan; sus propias pistas de sonido (`sound`) se quedan. Las entradas `p.` siguen en el diccionario (cuaderno y web) y ya no piden tarjeta de decir. Se descartó dejar la explicación al final del reverso, que él había aceptado en una nota anterior: la última nota pide que no conste en ninguna parte. Vive en: `docs/goal.md` («El pinyin por delante», «Cómo se practican las frases»), `docs/design.md` («Pronunciación: pista propia», «Tarjetas», «Cobertura», «Garantías»), `anki.py` (`card_fields`, `required_cards`).

### 2026-10-11 · Construir: producción libre, con material y modelos

YAGO propuso en el chat una tarjeta que le dé unas palabras de alto cruce y le obligue a montar con ellas una o varias frases, y que detrás ponga varias posibles con su audio. Pidió cinco palabras mejor que tres, para mezclar con libertad («no quiero que sea solo ordenar sino realmente usar estas u otras para crear significados»), escenas concretas, cotidianas pero poco habituales (en una tienda, antes de empezar una reunión, en el metro, cenando solo con una mesa al lado), y que sea una tarjeta principal: «es como funciona realmente la cabeza: me sé algunas palabras, pero debo hilarlas para que se acoplen bien al contexto». No retroactiva («al principio era más importante el vocabulario suelto y ahora empezamos a formar frases»), y no le importa que las sesiones se alarguen. Choca con la regla «nada de producción libre», que se escribió porque inventar sin modelo no educa: aquí hay material (palabras que ya sabe) y modelos detrás, así que la regla se cambia y queda solo para lo que no tiene ninguna de las dos cosas. Decidido: tipo `compose`, de 3 a 6 palabras del mazo y al menos dos frases modelo del mazo, cada una con otra mezcla; autoevaluación; las dudas van a «Tus notas»; varias por lote. Vive en: `docs/goal.md` («Cómo se practican las frases»), `docs/design.md` («Tarjetas», «Gramática», «Garantías»), `anki.py` (`compose_rules`, `card_fields`).

### 2026-10-11 · Elegir entre opciones y consignas a la izquierda

YAGO pidió que el texto de las preguntas vaya alineado a la izquierda («me molesta un poco que estén centrados») y poner a-b-c-d-e donde convenga, como en las preguntas de repaso que le hizo el agente en el chat. Decidido: la consigna va a la izquierda en todas las tarjetas, y cualquier tarjeta puede llevar opciones (`prompt.options`, de 2 a 5) con la buena en `answer.choice`; detrás sale la buena con su letra y la respuesta de siempre. Vive en: `docs/goal.md` («Cómo se practican las frases»), `docs/design.md` («Tarjetas», «Garantías»), `anki.py` (`choice_rules`, `card_fields`, `CSS`).
