# Diseño — chino práctico, pinyin y audio

Especificación canónica para agentes: cómo funciona el sistema. Cada regla se dice una vez, aquí. Las partes sin implementar llevan **[pendiente]** (ver «Estado y fases»).

**Qué va aquí y qué no.** Va el mecanismo: formatos, flujo, tarjetas, cobertura, audio, Anki y lo que comprueba el código, en presente. No va:

- lo que depende de quién aprende (qué entra, cómo quiere practicar, cómo se le habla): `docs/goal.md`, el módulo intercambiable;
- los valores de este mazo y su entorno (límites diarios, voz, recurso de Azure, fase de pruebas): `docs/owner.md`;
- por qué o cuándo se decidió algo: `docs/decisions.md`;
- cómo va ahora el que aprende: `2-digests/state.md`;
- el mapa de carpetas y las convenciones de nombres: `README.md`.

Aquí no hay fechas ni «lo pidió…». Al cambiar una regla: primero la entrada en `docs/decisions.md`; luego la regla aquí, reescrita en presente, sin dejar rastro de la versión anterior; y si se puede comprobar, en `check` con su prueba.

## Objetivo: un módulo aparte

Todo lo que depende de quién aprende está en `docs/goal.md`: quién es, para qué estudia, qué entra y para qué (`say`, `hear`, `read` o fuera), en qué orden, cómo quiere practicar y qué huecos hay que señalarle. Funciona como un módulo de prompt intercambiable: el agente lo lee antes de cada lote y lo aplica como primer filtro de cada decisión. Cambiar de objetivo (más negocios, menos lectura, otra persona) es reescribir `goal.md`: cambian las decisiones del agente sin tocar el código ni esta especificación. Si una regla de aquí choca con `goal.md` en algo que es del que aprende, manda `goal.md` y la regla se corrige.

## Principio

El modelo redacta; `anki.py` calcula y comprueba. Lo que puede calcularse (qué tarjetas faltan, qué sobra, qué audio falta) lo decide el código a partir de reglas escritas aquí, no el criterio del agente en cada sesión. El agente trabaja sobre la diferencia que el código le da (`plan`) y `check` verifica el resultado. `anki.py` no llama nunca a un LLM; compilar no regenera ejercicios.

## Glosario

- **Entrada**: un elemento del diccionario (`3-data/lexicon/`): palabra, expresión, carácter, componente, pronunciación, grupo o estructura. Una por sentido.
- **Frase**: oración segmentada (`3-data/sentences/`), reutilizable en varias tarjetas: recurso en sí (`say`) o ejemplo (`hear`).
- **Ejercicio**: una pregunta concreta; en Anki, una nota con una tarjeta.
- **`use`**: para qué necesita el que aprende una entrada o frase (`read`, `hear`, `say`, o excepción). Decide las tarjetas exigidas.
- **Rol**: `content` (palabra con significado propio) o `function` (pieza gramatical: se practica en frase).
- **Nivel**: escalón de dificultad del HSK 3.0, del 1 al 7 (el 7 agrupa los niveles 7 a 9). Oficial si la palabra está en la lista, estimado por el agente si no. Primera división del mazo (ver «Niveles»).
- **Desván**: lo que llegó y no entra ahora, guardado con su contexto hasta que algo lo despierte (`3-data/attic.yaml`; ver «Desván»).
- **Categoría gramatical** (`pos`): pronombre, verbo, clasificador… de cada palabra; ver «Gramática».
- **Estructura**: plantilla de frase con huecos visibles (`{S} + 很 + {Adj}`), con sus ejemplos; ver «Gramática».
- **Tema**: agrupación por asunto (`3-data/themes.yaml`); es el archivo en que vive cada elemento y decide el subdeck, el orden de aprendizaje y el cuaderno.
- **Grupo**: entradas que se estudian juntas (`visual`, `homophone` y `soundalike` por contraste; `pattern`, `set` y `phonetic` como familia).
- **Ósmosis**: que una palabra aparezca como contexto en frases, además de en sus propias tarjetas.
- **Lote**: una entrega de apuntes (`NNN-AAAA-MM-DD-tema`).
- **Log** (`2-digests/summary-<lote>.md`): el acta de un lote, lo que el agente decidió y por qué. Se lee; no se reescribe.
- **Review** (`1-inbox/review-<lote>.md`): lo que admite la opinión del que aprende, con una línea «>» por punto; empieza por «Sine qua non». Con sus respuestas entra en el siguiente lote.
- **Estado** (`2-digests/state.md`): la foto de ahora (nivel, clases, método, avisos, decisiones abiertas), reescrita en cada lote, cada punto con su fuente.
- **Caja negra**: lo que queda de cómo se trabajó: «Fricciones del proceso» en cada log y `private/blackbox.jsonl` (ver «Retrospectiva»).
- **Cuaderno**: todo lo aprendido por tema (`4-notebook/`), generado.
- **Trampa fonética**: letra del pinyin que un hispanohablante lee mal; la detecta una regla.

## Flujo de un lote

Un lote es una entrega de apuntes. Se nombra `NNN-AAAA-MM-DD-tema` (número de orden de procesado, fecha, tema en palabras; nunca números de hoja). El lote solo sirve para llevar la cuenta de la procedencia: dentro del mazo cada cosa va donde le toca por tema y nivel, y un ajuste sobre algo antiguo corrige la entrada antigua.

1. **Leer el inbox.** Todo archivo de `1-inbox/` salvo `README.md` y `review-*.md` es apunte pendiente, en cualquier formato y con cualquier nombre (si llega pegado en el chat, el agente lo guarda allí tal cual). Entra texto e imágenes (fotos de apuntes: el agente las lee). Una grabación de clase se transcribe primero y se usa como contexto (ver «Grabaciones de clase»). Las fechas de los apuntes, si las hay, van a `source.date` de lo que salga de cada parte; si un archivo mezcla días, se respeta la fecha de cada parte.
2. **Leer el review anterior y el estado.** Cada línea «>» con texto del review del lote anterior es una instrucción (meter, descartar, matizar, corregir); vacía, no cambia nada. Si pide una tarjeta de matiz, es `type: nuance`. `2-digests/state.md` da el contexto acumulado.
3. **Integrar cada elemento.** `lookup` (busca también en el desván); decidir si es nuevo, corrige algo, amplía una entrada o grupo, o va al desván (ver «Integración de lo nuevo» y «Desván»). Con las entradas nuevas escritas, `attic <lote>`: lo que despierta entra en este lote. Lo parecido a lo existente (forma, sonido, patrón) va a esa entrada, a `relations` o a un grupo, no a tarjetas sueltas.
4. **Asignar `use`** a cada entrada nueva (ver «Cobertura»), con motivo cuando se aparte de las señales de frecuencia, y vigilando el volumen que fija `docs/goal.md`, «Cuánto entra».
5. **Comentarios** en su ámbito, redactados en `text` y con lo que escribió en `original` (ver «Comentarios»). Lo que parezca privado no va a `3-data/`: se pregunta.
6. **Preguntar lo ambiguo** (sentido, lectura, si ya lo sabe) en vez de adivinar. Las transcripciones de fotos hechas por LLM traen errores y `[¿?]`: se marcan con ⚠️ en el log y van a «Por verificar» del review, nunca se dan por buenas.
7. **Tarjetas.** `plan` → `scaffold --write` escribe las tarjetas estándar de lo que falta (siempre con el mismo formato) → el agente revisa sus consignas y redacta a mano lo que `scaffold` marca «a mano» y las tarjetas que nunca son exigidas (matiz, comprensión) → `check` sin errores ni avisos pendientes.
8. **Revisar la estructura** (temas, grupos, `use`; ver «Reorganización») y contarlo en el log.
9. **Escribir** el log (`2-digests/summary-<lote>.md`), el review (`1-inbox/review-<lote>.md`; `plan --doc <lote>` lo empieza) y el estado (`2-digests/state.md`). Ver «Log, review y estado».
10. **Audio y Anki.** `audio` (solo lo que falta) y `push`.
11. **Cerrar.** Poner a cada apunte del inbox su prefijo de fecha y ejecutar `close-batch <lote>` (primero con `--dry-run`): comprueba el log, el review y el estado, mueve los apuntes y el review leído a `1-inbox/history/<lote>/`, regenera el cuaderno y la exportación, hace commit y pone la etiqueta `lote-NNN`; se niega si falta algo o `check` tiene errores. Cada apunte se archiva como `AAAA-MM-DD_<nombre original>`, con la fecha en que se apuntó (la que el que aprende escribe dentro); si mezcla días, `mixto_<nombre original>` y la fecha de cada parte dentro; si no tiene fecha, `sin-fecha_<nombre original>` y se usa la de procesado en `source.date`. El review conserva su nombre. Sin subcarpetas por día: el prefijo ya ordena. Dos fechas distintas: la del lote (procesado) y la de cada apunte (cuándo se aprendió). `1-inbox/` queda con su `README.md` y el review nuevo.
12. **Resumen** en el chat: añadido, cambiado, reorganizado, tarjetas antiguas tocadas y audio nuevo. El commit y la etiqueta de `close-batch` son locales; subir a GitHub solo cuando se pida.

**Ritmo de lotes**: un lote es lo que haya en el inbox cuando se pide; el sistema funciona igual con lotes más cortos o más largos (ver «Reorganización»). La costumbre recomendada está en `docs/owner.md`.

## Log, review y estado

Tres documentos con dos autores. El log y el review empiezan con un comentario que explica qué son (`LOG_HEADER` y `REVIEW_HEADER` en `anki.py`) y van **por temas, sin números de hoja ni de página**, una línea por elemento: `汉字 pinyin · significado · pista (relación, mnemotecnia, pronunciación) · ejemplo`.

- **Log** (`2-digests/`, del agente, lectura): el acta completa del lote: lo que entró (✅, 🃏 si tiene tarjeta), lo que no (🟡 solo reconocer, ❌ literario, arcaico o en desuso) con su motivo, las correcciones ⚠️ de glosas y las reorganizaciones. Apartados fijos: «Cambios en el sistema» (si los hubo), «Fricciones del proceso» y «Seguimiento». `close-batch` exige «Fricciones del proceso».
- **Review** (`1-inbox/`, para el que aprende, editable). Debajo de cada punto, una línea `  > `. Con las respuestas va a `1-inbox/history/` del lote siguiente. Apartados, en este orden:
  1. **«Sine qua non»**: lo único que hace falta contestar para que el siguiente lote salga bien (sentido o lectura dudosos, algo por verificar, una decisión). Como mucho `SINE_QUA_NON_MAX` puntos; cada uno, una pregunta concreta con un enlace a donde está el detalle (`#apartado` de este review o `/2-digests/…#apartado` del log) y su línea «>». Si no hace falta nada, «- (nada)». Un punto de aquí no se repite abajo: abajo queda el detalle al que enlaza.
  2. «Cómo vas» (el «Seguimiento» del log), «Lo que más te cuesta» (de `anki.py stats`) y «Huecos y propuestas» (según `docs/goal.md`).
  3. «Falta» (palabras `say` sin frase, calculado), «✅ Entró, con matices para ahondar» (solo los que traen relación, mnemotecnia, registro o corrección), «Pendiente: ✅ sin tarjeta todavía», «Del desván» (lo que entró desde el desván y por qué despertó), «No entró, y por qué» (señalando lo que se guarda en el desván), «Por verificar».
  4. Cada `MAINTENANCE_EVERY` lotes, «Mantenimiento» (el repaso periódico de Anki de `docs/owner.md`) y «Retrospectiva» (ver abajo).
  5. «Tus notas».

  `close-batch` comprueba que «Sine qua non» es el primer apartado, que no pasa del máximo y que cada punto lleva enlace y línea «>», y que ningún enlace del review está roto (archivo y ancla).
- **Estado** (`2-digests/state.md`, del agente): la foto de ahora, no un historial. Empieza con `STATE_HEADER` y el título `# Estado tras el lote <lote>`; apartados «Nivel», «Las clases», «Tu método», «Avisos abiertos» y «Decisiones pendientes». Se reescribe en cada lote: lo que deja de ser cierto se quita, no se tacha. Cada punto termina con el enlace a su fuente (un log `/2-digests/…#apartado`, un review archivado `/1-inbox/history/…`, un documento `/docs/…`): nada que no se pueda comprobar ahí. Los enlaces van desde la raíz del repositorio y nunca a algo que se mueve al cerrar un lote (el review del inbox). `close-batch` comprueba que está al día con el lote, que tiene sus apartados, que cada punto enlaza y que los enlaces existen.

**Seguimiento**: en cada lote el agente escribe una reflexión que va al final del log y, igual, al principio del review como «Cómo vas», con su línea «>». Se escribe desde el estado y el log del lote, no releyendo todos los anteriores: el estado ya es la memoria acumulada, y sus enlaces llevan a lo profundo cuando hace falta. Dice qué ha cambiado desde la última vez y no repite lo mismo si nada cambió. Cuatro partes, breves:

1. **Nivel**: cobertura de cada nivel y distancia al siguiente (ver «Niveles»); el cambio de nivel, cuando toque, se anuncia aquí y en el chat.
2. **Las clases**: qué está enseñando la profesora en este tramo (temas, ritmo, énfasis), contrastado con el nivel y con `docs/goal.md`: qué encaja, qué falta, qué convendría pedirle. Siempre «la profesora», sin nombre (el repositorio es público), y la opinión es sobre el contenido de las clases, nunca sobre la persona.
3. **Tu método**: cómo estudia, visto a lo largo de los lotes (qué apuntes rinden, frases frente a palabras sueltas, escuchar, hablar y leer, fechas, tamaño y frecuencia de los lotes, constancia, lo que dice `stats`) y un consejo concreto, con lo que funciona y lo que no.
4. **Avisos**: lo que el agente quiera transmitir: cambios en el mazo que le afectan, decisiones pendientes, ideas. Es el canal que se lee con seguridad.

Al terminar, el estado se actualiza con lo mismo.

**Cambios en el sistema**: si un lote cambia reglas, criterios o código, el log lo cuenta en una sección propia, con qué cambió y dónde está escrito ahora, y `docs/decisions.md` recibe la entrada.

**Fricciones del proceso**: al final de cada log, lo que estorbó al trabajar en el lote: avisos de `check` que costó resolver o que no aportaban, pasos que se rehicieron, reglas que chocaban, órdenes lentas o que fallaron. Hechos, no excusas; «- (nada)» si no hubo. Es la materia de la retrospectiva.

Histórico: un log no se reescribe. Si llega una corrección después (por el chat o por el inbox), el cambio va a `3-data/` y el log recibe al final «Cambios posteriores» con la fecha. Que algo se repita en los apuntes de varios lotes es una señal: si está como `hear` y reaparece, se propone subirlo a `say` en el review.

## Retrospectiva

Cada `MAINTENANCE_EVERY` lotes (o antes, si algo está roto), el agente revisa cómo se está trabajando, no qué se está aprendiendo:

- `anki.py retro` junta las «Fricciones del proceso» de los últimos lotes y lo que repite la caja negra (`private/blackbox.jsonl`): cada orden de `anki.py`, con su duración, cómo acabó, sus errores y sus avisos. La caja negra solo existe en local (si hay `private/`); nunca va a git ni a la CI.
- Las transcripciones de las sesiones del agente quedan además en el equipo del que trabaja; se miran solo si una fricción no se entiende con lo anterior.
- El agente propone en el review («Retrospectiva») los cambios de proceso que salgan; lo aceptado entra en `docs/decisions.md` y en su documento. Las reglas no cambian sobre la marcha fuera de aquí, salvo que algo falle en uso real o el que aprende lo pida.

## Integración de lo nuevo

Para cada elemento que llega (tras `lookup`):

| Lo que llega | Qué se hace |
|---|---|
| Algo que ya existe con el mismo sentido | Enriquecer lo antiguo: comentario, frase de contexto. Tarjetas nuevas solo si sube su `use` (las calcula `plan`) |
| El mismo hanzi con otro sentido | Entrada nueva para ese sentido, en `relations` con la antigua |
| Algo nuevo que encaja en un tema | Entrada nueva en ese tema; `plan` calcula sus tarjetas |
| Algo nuevo sin tema donde encaje | Tema nuevo, o reorganizar (ver abajo) |
| Algo que se confunde con lo que ya hay | Grupo de contraste nuevo o ampliado |
| Una frase nueva | Frase propia (`say` o `hear`); enriquece sola las tarjetas antiguas de sus palabras |

Si hay duda (sentido ambiguo, variante de algo existente, tema), se pregunta en el review en vez de adivinar.

**Ejemplos automáticos.** Al dar la vuelta a una tarjeta de palabra se muestran hasta `EXAMPLES_MAX` frases que la contienen, por el ID de la entrada (así que respetan el sentido), frases modelo primero, y cada tarjeta de la misma palabra toma otras distintas. `reveal` sigue sirviendo para fijar a mano una frase concreta. Así lo nuevo y lo antiguo se cruzan sin depender de que nadie se acuerde de enlazarlo; las tarjetas conservan su progreso porque solo cambia su reverso.

## Reorganización

La estructura se adapta a lo que llega; no se congela. En cada lote el agente revisa, y cambia si hace falta:

- **Temas**: dividir los que crecen demasiado, juntar los que se quedan con muy poco, crear uno cuando llega un asunto nuevo, mover lo que encaja mal y reordenarlos si el orden de aprendizaje ya no sirve. `check` avisa cuando un tema pasa de `THEME_MAX` entradas o baja de `THEME_MIN` (en `anki.py`); es un aviso: decide el criterio. Si se decide mantener un tema así, se anota en `themes.yaml` con `keep: <motivo>` y el aviso deja de salir.
- **Grupos**: crear familias cuando aparecen confusiones o series nuevas, y ampliar las existentes.
- **`use`**: subir lo que se repite en los apuntes o el que aprende pide decir; bajar lo que resulta que no usa o lo que `stats` muestra que no se fija.
- **Frases y entradas**: fusionar duplicados y separar sentidos que estaban mezclados (IDs nuevos para lo separado; los antiguos no se reutilizan).

Cómo: mover un elemento de tema es moverlo de archivo en `3-data/` (y sus ejercicios, al archivo del mismo tema); renombrar o reordenar temas es editar `themes.yaml`. `push` recoloca las tarjetas en Anki conservando el progreso y borra los subdecks que queden vacíos. Toda reorganización se cuenta en el log del lote, con qué se movió y por qué.

## Lotes disruptivos: qué protege y cómo se recupera

Un lote puede tocar mucho (reorganizar temas, corregir cientos de tarjetas). Lo que lo hace seguro:

- **La identidad de una tarjeta es el ID de su ejercicio**, no su texto, su tema ni su archivo. Reimportar con el contenido cambiado y moverla de subdeck conservan su progreso (tipo, intervalo, vencimiento, facilidad, repasos y registro): está comprobado en Anki real (ver `docs/decisions.md`). Solo lo pierde si su ejercicio desaparece y se borra con `--prune`.
- **El audio va por texto chino exacto.** Reorganizar no toca audio; cambiar un hanzi pide audio nuevo (céntimos) y `check` bloquea hasta que exista. Los MP3 que dejan de usarse quedan sin estorbar.
- **`check` bloquea** referencias rotas, IDs repetidos entre archivos, tarjetas exigidas ausentes, pinyin que no cuadra y audio que falta. Y **compara con la última etiqueta `lote-NNN`**: avisa de ejercicios desaparecidos (tarjetas que quedarían huérfanas), de preguntas que cambian de respuesta o de tipo con el mismo ID (deben llevar ID nuevo) y de ejercicios archivados en un tema distinto al de su objetivo. El paso 7 del flujo exige resolver los avisos antes de subir.
- **Borrar en Anki nunca es automático**: `push --prune` lista las huérfanas y, si son más de `PRUNE_MAX`, se niega salvo `--force`.

Recuperación: el estado tras cada lote está en su etiqueta `lote-NNN`. Volver a él es restaurar `3-data/` desde la etiqueta y hacer `push`: el contenido y la colocación de las tarjetas vuelven; el progreso de las que sigan existiendo nunca se tocó. Lo único irrecuperable desde el repositorio son las notas borradas con `--prune`; para eso quedan las copias automáticas de Anki (Herramientas → Copias de seguridad).

## Gramática: categorías y estructuras

**Categoría gramatical** (`pos`, calculada; `pos_of` en `anki.py`): cada palabra tiene una de pronombre, sustantivo, nombre propio, verbo, adjetivo, adverbio, clasificador, número, partícula, conjunción, preposición, interrogativo, interjección o expresión (`POS_LABEL`).

- Si está en la lista del HSK, sale de ella: `sources/hsk/hsk3.tsv` trae las etiquetas de corpus de cada palabra (v, n, a, d, q, r…), y cuenta la primera que tiene equivalente (`POS_TAGS`). Los interrogativos (什么, 谁, 几…) se fijan como tales en el código, porque la lista los da como pronombres o números. Las expresiones son `expresion`.
- La entrada fija `pos` cuando no está en la lista (门多萨, 嗯) o cuando el sentido del mazo no es el de la primera etiqueta (对 «correcto» es adjetivo aunque la lista lo dé antes como preposición); en ese caso, con `pos_reason`.
- Solo palabras y expresiones: un carácter ligado o un componente no son palabras.
- `check`: error si una palabra queda sin categoría; aviso si `pos` contradice la lista sin `pos_reason`.
- Se ve en el reverso (bajo el significado), en la etiqueta `pos::` de Anki, en el cuaderno y en la exportación.

**Estructuras** (`kind: structure`, `st.`, tema `estructuras`): una plantilla de frase con huecos, `{S} + 很 + {Adj}`.

- Piezas separadas por « + »: huecos entre llaves y piezas fijas en hanzi; la puntuación final puede ir pegada (`{S} + 呢？`). Huecos: `{S}` sujeto, `{N}` sustantivo, `{V}` verbo, `{Adj}` adjetivo, `{Num}` número, `{Nombre}`, `{Lugar}`, `{Tiempo}` y `{Frase}` (una oración entera, sin comprobar la categoría) (`SLOTS`); cada uno admite unas categorías y tiene su color.
- `refs`: las entradas de las piezas fijas, en orden. `examples`: frases del mazo que la cumplen. `meaning: {es, en}`: qué expresa y la regla, en una frase. El nivel no se escribe: es el de su pieza fija más difícil.
- `check` (determinista, `grammar_rules`): error si falta algo, si un hueco no existe, si `refs` no son las piezas fijas o si un ejemplo no las contiene en ese orden; aviso si lo que ocupa un hueco junto a una pieza fija es de otra categoría (en `{S} + 很 + {Adj}`, lo que sigue a 很 tiene que ser adjetivo). Una estructura no entra con un ejemplo que no la cumple: se cambia el ejemplo o se descarta la estructura.
- `contrast: {right, wrong, why: {es, en}}`: una frase del mazo que la cumple bien y el calco erróneo que haría un hispanohablante (他是高 frente a 他很高; 我很好，和你？ frente a 你呢？), con el porqué.
- Tarjeta `pattern` (`x.calque.`, exigida si `use` incluye oír o decir; la genera `scaffold` desde `contrast`): delante, la frase en español y las dos versiones en chino con su pinyin, en orden barajado pero fijo: «¿Cuál se dice así en chino?»; detrás, la buena con su audio, la mala tachada con su porqué, la plantilla con los huecos como cajas de color y los demás ejemplos. Autoevaluación. Nunca hay tarjetas de producción libre («di una frase con esta estructura»; ver `docs/goal.md`). `check` da error si una estructura que se practica no tiene `contrast` o si el calco es igual que la frase buena.
- Qué estructuras entran lo decide el agente con `docs/goal.md` (las de clase primero); las frases de ejemplo son las del mazo, así que una estructura nueva suele pedir una frase nueva en el review.

## Desván

`3-data/attic.yaml` guarda lo que llega en los apuntes y no entra ahora, con todo su contexto, para que no se pierda ni ensucie el mazo, y lo devuelve cuando algo con lo que conecta entra.

**Qué va al desván y qué no**

- Va: lo de la investigación propia que es de un nivel superior y está poco conectado con lo que ya hay (发票, 灰色, 欠), lo que llega suelto y sin frase (左, 右), las piezas con un uso real más adelante (疒 con 病) y lo que el que aprende quiere ver algún día.
- No va, **nunca**: lo de clase (entra en el mazo, en su nivel; ver `docs/goal.md`); lo que ya es una nota de otra entrada y no tiene uso propio (叟 dentro de 瘦); lo literario, arcaico o en desuso (se descarta con ❌ y su motivo, sin desván). El desván no es un sitio para aplazar decisiones difíciles: si algo pasa el filtro y conecta, entra.

**Cada elemento** (esquema en `3-data/README.md`): hanzi, pinyin, significado, nivel (oficial, o `level` con `level_reason`), `theme` (dónde iría), `links` (qué palabras lo despiertan), `reason` (por qué no entró), `notes` (sus observaciones, redactadas como cualquier comentario, con `original` si hace falta) y `source` (lote, archivo y fecha). Un hanzi, un elemento: si vuelve a aparecer en otro lote, se amplían sus notas.

**Cuándo despierta** (`anki.py attic <lote>`, determinista, `attic_awake`):

1. una entrada nueva del lote es uno de sus `links` (un enlace de un solo hanzi solo cuenta si es esa palabra exacta: 猫 no despierta con 小猫; uno de varios, también dentro de otra palabra);
2. una entrada nueva contiene su hanzi (日 despierta con 生日);
3. su nivel está a punto de cerrarse: el mazo cubre ya el 60 % de ese nivel (`ATTIC_NEAR`), y lo que espera ayuda a completarlo.

Lo que despierta entra en ese mismo lote: pasa a `3-data/` como una entrada más (con sus notas como comentarios y `source: {origin: attic, batch, file, date, rescued: <lote en que entra>}`: el lote, el archivo y la fecha son los de cuando se apuntó), sale del desván y el log y el review («Del desván») lo cuentan con el motivo. Si el agente decide que aún no, lo deja con `snooze: <lote>` y `snooze_reason`; vuelve a despertar en el lote siguiente.

**Qué lo protege** (en el código): `check` exige los campos, un hanzi por elemento y notas bien redactadas, y avisa si algo del desván ya está en el mazo (hay que borrarlo de allí); `close-batch` se niega a cerrar un lote con elementos despiertos sin pasar ni aplazar; `gaps` muestra cuántos esperan, por nivel, y el más antiguo; `lookup` busca también en el desván, así que antes de añadir algo se ve si ya esperaba con notas. El que aprende puede pedir que algo salga cuando quiera: «sácalo» en el review o en el chat.

**Qué no es**: no genera tarjetas, no cuenta en la cobertura y no se exporta a la web. Es público como el resto de `3-data/` (nada privado; las citas de libros, con el mismo criterio que en los comentarios).

## Capas y carpetas

| Capa | Orden | Contenido |
|---|---|---|
| `1-inbox/history/<lote>/` | cronológico, intocable | lo que el que aprende escribió, tal cual; versionado |
| `2-digests/summary-<lote>.md` | cronológico; temático por dentro | el log de cada lote, del agente; histórico, no se reescribe |
| `2-digests/state.md` | la foto de ahora | el estado vivo; se reescribe en cada lote |
| `3-data/<carpeta>/<tema>.yaml` | por tema y concepto, sin cronología | fuente de verdad; la cronología solo como `source.batch` y `added` |
| `4-notebook/` | temático, acumulado | todo lo aprendido por tema, generado desde `3-data/` en cada lote; nunca se edita |
| Anki | por nivel, por tema dentro de cada nivel + etiquetas | estudio |

Mapa completo y convenciones de nombres: `README.md`.

## Datos

Un archivo por tema en `3-data/lexicon/` (entradas), `3-data/sentences/` (frases) y `3-data/exercises/` (tarjetas); los temas y su orden, en `3-data/themes.yaml`. El tema de cada elemento es el archivo en que vive: moverlo de tema es moverlo de archivo, y los ejercicios van en el tema de su primer objetivo. Esquema de campos: `3-data/README.md`. `check` da error si un archivo no corresponde a ningún tema o si un tema está mal formado.

- **IDs** con prefijo de tipo (`w.` palabra, `e.` expresión, `c.` carácter o componente, `p.` pronunciación, `g.` grupo, `st.` estructura, `s.` frase, `x.` ejercicio). Nunca se reutilizan ni se cambian; no usar solo el hanzi. Corregir conserva el ID; cambiar lo que pregunta una tarjeta exige ID nuevo.
- **Una entrada por sentido y lectura** (行 háng / xíng). `standalone: yes | rare | no` es del sentido: si no se usa solo, `check` exige alguna palabra registrada que lo contenga.
- **Grupos** (`kind: group`): `basis: visual | homophone | soundalike | pattern | set | phonetic` (soundalike: se parecen al oído sin ser iguales, como 是 shì / 十 shí o 大家 / 大象; su tarjeta de contraste se oye y se elige) (set: serie de significado, como las partes del día o los verbos de querer; phonetic: caracteres que comparten la pieza que da el sonido, como 青 en 请 y 清), miembros con `cue` (rasgo distintivo). Máximo 4 en contraste. Toda tarjeta cuyo objetivo es miembro de un grupo muestra el grupo en el reverso con el objetivo marcado (si está en un set y en un pattern, basta el set). Se crean cuando el que aprende ya conoce un miembro o los ha confundido, nunca por adelantado. Tarjetas: `contrast` (una por miembro) y `derive` (de un miembro del patrón a otro).
- **Conexiones** (`connection: {kind, with, text}`): el recuadro de «Conexión» de un carácter (🔊 da el sonido, 🧩 da el significado, 👀 se parece pero no tiene que ver), escrito una vez en su entrada y heredado por las palabras que lo llevan; uno como mucho por tarjeta (`connection_for`). Qué pieza da el sonido o el significado sale de `sources/hanzi/` (`anki.py hanzi <caracteres>`), no de memoria.
- **Frases** segmentadas con `ref` a las entradas; una frase se guarda una vez y se reutiliza. Un segmento puede declarar `sandhi` cuando su pinyin escrito es el realizado (不 → bú).
- **Ejercicios** separan `targets` (lo evaluado), `context` (visible en la pregunta) y `reveal` (ejemplos al revelar). La cobertura se cuenta por `targets`, nunca buscando subcadenas.
- **Procedencia**: `source: {origin, batch, file, date}`; `added` en cada ejercicio.
- **Pinyin**: `check` lo contrasta con pypinyin; las discrepancias legítimas (tono neutro, erhua) llevan `accept_pinyin_mismatch` con motivo.

## Comentarios

| El comentario trata sobre… | Va en… | Se muestra… |
|---|---|---|
| una palabra, sentido o carácter | su entrada | en todas las tarjetas que la evalúan |
| un sonido, tono o regla general | una entrada `p.` de pronunciación | en los ejercicios que la referencian |
| una frase o situación | la frase | junto a esa frase |
| un truco para una pregunta concreta | el ejercicio | solo en su respuesta |

**Estatus de cada carácter**: todo carácter o componente que es objetivo de una tarjeta o miembro de un grupo se presenta como **palabra**, **ligada** (solo dentro de palabras; `standalone: no` o `rare`) o **componente** (`kind: component`: solo parte de otros caracteres). El reverso lo muestra solo, calculado de los datos. Los componentes llevan `use: context` (sin tarjetas; visibles en el diccionario) salvo que entren en un grupo de contraste. Si el mismo hanzi también es palabra suelta (口 «boca», 月 «luna; mes»), la entrada del componente lleva `as_word` y el reverso lo dice: «componente aquí; suelto también es palabra». Nunca se afirma que no es palabra algo que sí lo es. En las tarjetas de palabras, cuándo se menciona el estatus de uno de sus caracteres lo dice `docs/goal.md`.

`kind`: `mnemonic` (subjetivo; en la tarjeta, «Mnemotecnia», con el aviso de que es una imagen para recordar y no su origen), `teacher` (solo si consta que lo dijo la profesora; en la tarjeta, «En clase»), `linguistic` (verificado), `note` (apunte de origen sin precisar), `sound` (pista de pronunciación del que aprende, literal, como «xiEnshAng»; se muestra como «Cómo suena»).

**Redacción**: `text` es lo que se muestra (tarjetas, cuaderno, web) y va siempre bien escrito: frases completas en español, con mayúsculas y puntuación, sin símbolos de apunte (flechas, `+ intenso`, `w/`), traducido si se apuntó en inglés, sin cambiar lo que quería decir (se puede añadir un ejemplo o una precisión comprobada). Lo que escribió se conserva literalmente en `original`, que no sale de `3-data/`; si lo que pegó es copia literal de un libro, no lleva `original` (una paráfrasis sí) y `text` lo cuenta con otras palabras (ver «Repositorio y privacidad»). Si su apunte ya está bien escrito, se copia tal cual y no lleva `original`. El log, el review y cualquier otra salida citan siempre `text`; el apunte en bruto solo queda en `1-inbox/history/` y en `original`. `check` avisa de un `text` que empiece en minúscula, no termine en punto o lleve símbolos de apunte (salvo `sound`). Una mnemotecnia no se presenta como etimología. `private: true` por defecto y nada privado sale en ninguna salida; como el repositorio es público, lo privado ni siquiera se guarda en `3-data/`. Una observación nueva («先生 se pronuncia…») va a su hogar según esta tabla y aparece en todas las tarjetas afectadas.

## Cobertura: `use`, `plan` y `check`

Cada entrada declara **para qué la necesita el que aprende**:

| `use` | Significa | Marca |
|---|---|---|
| `say` | decirla (implica oírla y leerla) | ✅ |
| `hear` | entenderla al oírla (implica leerla) | ✅ |
| `read` | reconocerla escrita | 🟡 |
| `drop` | descartada con motivo; sin tarjetas; `lookup` la encuentra | ❌ |

Es una escalera, con **excepciones siempre que hagan falta**: una lista explícita (`use: [read]` para 入口, que se lee en carteles pero casi no se dice; `use: [hear]` para un nombre propio) con `use_reason`. `check` exige el motivo y no limita cuántas excepciones hay.

**Rol**: `content` (水, 商店, 高) o `function` (吗, 呢, 的, 都, 很, 什么, 在). No es frecuencia sino función: las piezas gramaticales se practican dentro de frases.

**Tarjetas exigidas** (una por tipo y objetivo; más es redundancia):

| | `read` | `hear` | `say` |
|---|---|---|---|
| palabra `content` | lectura | + escucha | + producción |
| palabra `function` | lectura | + escucha | + producción en frase (hueco) |
| frase o frase hecha | — | escucha | + decirla en voz alta con el audio |
| carácter o componente | componentes (o solo el contraste, si está en un grupo `visual`) | — | — |
| pronunciación `p.` | — | escucha | + voz alta |

Además, calculado del pinyin: tarjeta de tonos para toda entrada `hear` o `say` con tono neutro o sandhi (3+3, 不, 一). El erhua se detecta pero lo trata la pista de pronunciación. La producción suelta tecleada se reserva para el núcleo; el peso de la producción va a frases y frases hechas, que son lo más rentable para tonos en contexto y fluidez.

Nunca exigidas, escritas a mano cuando sirven: `nuance` (lo pide el que aprende) y `comprehension` (ver «Tarjetas»; cuántas, según `docs/goal.md`).

**Ósmosis**: toda palabra `say` o `context` aparece como contexto en al menos una frase; aviso si no. Las expresiones que ya son un enunciado completo (你好, 再见) no lo necesitan. Antes de pedir frases al que aprende, se buscan en sus apuntes de `1-inbox/history/`. Que una entrada reaparezca como contexto en muchas frases es deseable y no cuenta como redundancia.

**Señales para `use`** (orientan, no deciden): el nivel (ver «Niveles») y la frecuencia hablada. `check` avisa cuando `use` choca con el nivel (nivel 1 marcado `read`; nivel 7 marcado `say`) y pide motivo; las necesidades del que aprende según `docs/goal.md` justifican excepciones. Nunca se importa una lista entera.

**`plan`** lista, para todo el mazo, las tarjetas exigidas que faltan y los avisos de ósmosis y señales. **`check` estricto** convierte en error cualquier tarjeta exigida ausente. **`gaps`** informa del reparto por capacidad (lectura, escucha, producción, tonos, comprensión…), contando cada tarjeta solo por lo que practica.

## Lo que se queda: `stats`

`anki.py stats [--days N]` lee de Anki, por AnkiConnect, el registro de repasos de este mazo (y de ningún otro): repasos y porcentaje de «Otra vez» del periodo, por tipo de tarjeta, las entradas y frases que más se fallan (agrupadas por `targets`, con en qué tarjetas) y las tarjetas olvidadas `LEECH_LAPSES` veces o más. Solo lectura: sincroniza antes para que lleguen los repasos del móvil (`--no-sync` para no hacerlo), no abre Anki y no escribe nada. Los cambios manuales (reiniciar, reprogramar) no cuentan como repasos. El review lo resume en «Lo que más te cuesta» con una propuesta para cada caso (una frase nueva, un contraste, otra pista, bajar su `use`); lo que se acepte entra en el lote siguiente.

## Niveles (HSK)

El mazo se ordena por dificultad con los niveles del HSK 3.0 (la versión de 2021): del 1 al 6, y el 7 para los niveles 7, 8 y 9, que comparten lista de vocabulario. El HSK es la escala, no la meta (`docs/goal.md`), y lo que no está en la lista también lleva nivel.

**Nivel de cada elemento**

- **Palabras y expresiones**: si están en `sources/hsk/hsk3.tsv`, su nivel es el oficial y lo calcula `anki.py`; no se escribe a mano. Si no están (帅, 西班牙, 你好 como saludo), el agente escribe `level` y `level_reason` (por qué ese nivel: frecuencia, dificultad, a qué palabras oficiales se parece). `check` da error si una entrada no tiene nivel.
- **Caracteres y componentes**: el nivel de la palabra oficial más baja que los usa; si ninguna, estimado. Un carácter ligado (`standalone: no` o `rare`) toma el nivel de la palabra más básica del mazo que lo contiene, aunque la lista oficial le dé otro como palabra suelta: 入 es HSK 6 como verbo, pero se aprende en 入口, HSK 2 (`level_of`).
- **Pronunciación**: las reglas básicas (tonos, sandhi, iniciales) son nivel 1.
- **Frases**: el nivel más alto de sus palabras. Una frase nunca adelanta vocabulario de un nivel superior: los ejemplos automáticos del reverso solo toman frases de nivel igual o inferior al de la tarjeta (`examples_for`).
- **Ejercicios**: el nivel más alto de sus objetivos.

**En Anki**: el nivel es la primera división y el tema la segunda: `🐉 Chino práctico::HSK 1::02 Saludos y despedidas` (el 7, `HSK 7-9`). El nivel de una tarjeta es el de su objetivo más difícil (`exercise_level`). Las nuevas salen por nivel primero. Etiquetas `nivel::1` y, si es estimado, `nivel::estimado`. Cambiar el nivel de algo lo mueve de subdeck conservando el progreso, igual que al reorganizar temas.

**Cómo se estudia**: nivel a nivel. Se puede estudiar el mazo entero, porque las nuevas salen por nivel, o solo el subdeck del nivel actual (cuál, en `docs/owner.md`). Lo de clase que llega de un nivel superior entra en su nivel y espera; lo investigado por su cuenta que es de un nivel superior y está poco conectado espera en el desván.

**Nivel actual y cambio de nivel**: en cada lote se calcula la cobertura de cada nivel (palabras de la lista con `use` `hear` o `say` en el mazo, frente al total del nivel; `anki.py gaps`, `level_coverage`) y va al review. Un nivel se da por superado con al menos el 80 % de su vocabulario (`LEVEL_PASS`) y el juicio del agente sobre las estructuras de frase que ya se manejan (la lista mide vocabulario, no gramática). Al cruzarlo, el agente lo anuncia en el chat y en el review, con claridad. Lo que llegue después de un nivel ya superado se señala como hueco de ese nivel.

**Huecos y propuestas**: el review compara el mazo con el nivel actual (lista oficial y secuencias de curso) y propone qué falta, con el criterio de `docs/goal.md`. **[pendiente]** Las secuencias de curso (qué palabras y qué gramática trae cada lección) se extraen nivel a nivel de materiales que solo están en local (ver «Repositorio y privacidad»).

## Pronunciación: pista propia [pendiente]

Las listas de frecuencia ordenan palabras, no sonidos; la pronunciación necesita cobertura propia, calculada:

- **Parejas de tonos**: las combinaciones de dos sílabas (1-1 … 4-neutro), clasificadas automáticamente desde el pinyin; `check` exige escucha y producción de cada pareja con varias palabras.
- **Sonidos difíciles**: aspiración (b/p, d/t, g/k), j q x frente a zh ch sh r, ü, -n frente a -ng; pares mínimos desde el vocabulario del que aprende.
- **Sandhi, neutro y erhua**, detectados desde el pinyin.
- Se practican por separado el tono de cita de cada palabra y la melodía real de las frases: el sandhi y el neutro esconden el tono de cita.

## Tarjetas

- **Tipos**: `read` (hanzi → leerlo en voz alta, pinyin y significado; el audio del reverso sirve para comparar), `listen` (audio → pinyin o comprensión: una palabra oída se escribe, en pinyin o en hanzi, como dictado `x.dictation.`; una frase se entiende y se autoevalúa, porque el significado no se compara letra a letra), `produce` (español → chino), `cloze` (hueco en frase), `tones` (un dígito por sílaba: 什么 → `25`; desde audio o desde pinyin sin tonos; `check` reconstruye el pinyin y verifica), `speak` (voz alta y comparar), `contrast`, `derive`, `components`, `nuance` (matiz o confusión concreta que pide el que aprende: «¿qué aporta 公 en 公司 y en 公主?»; nunca exigida, sin audio), `pattern` (una estructura: elegir entre la frase buena y su calco erróneo; ver «Gramática»), `comprehension` (abajo). Una pregunta concreta por tarjeta.
- **Comprensión lectora** (`comprehension`, `x.comprehension.`): un texto corto hecho con frases del mazo (`targets`, en orden; al menos `COMPREHENSION_MIN` hanzi) y una pregunta sobre lo leído, en español (`question: {es}`) o en chino (`question: {sentence}`, una frase del mazo de nivel no superior al del texto). Delante, el texto como un párrafo en hanzi (`script: hanzi`) o con el pinyin encima (`script: both`), nunca solo pinyin, y debajo la pregunta plegada, que se abre al terminar de leer. Detrás, la respuesta (`answer: {meaning}`) y la pregunta y el texto frase a frase, con pinyin, traducción y audio. Autoevaluación. Nunca exigida; no cubre la escucha ni la lectura de sus frases. Como reutiliza frases del mazo, no pide audio nuevo. `check` (`comprehension_rules`) da error si el texto no son frases del mazo, si es demasiado corto, si falta la pregunta o la respuesta o si `script` no es `hanzi` o `both`.
- **Tecleadas frente a autoevaluación**: se teclea en tonos y producción del núcleo, el resto es autoevaluación (el que aprende estudia en el móvil; ver `docs/goal.md`). En las frases para decir, escribir es opcional (caja «escríbelo si quieres»). **Normalización**: vale pinyin (tildes o dígitos, `v` = `ü`) o hanzi; espacios, mayúsculas y puntuación dan igual; solo cuenta como fallo un error real de sílaba o tono.
- **Audio**: escucha, tonos y pronunciación lo llevan delante; lectura, producción y deducción, tras revelar; el contraste visual y los componentes no llevan (se deciden por la forma); el de homófonos sí. Frases de ejemplo, textos de comprensión y entradas `p.`, siempre.
- **AFI** (transcripción fonética del tono de cita) en el reverso de palabras y en `4-notebook/`, calculada del pinyin con dragonmapper al compilar; nunca se guarda en `3-data/`. No refleja el sandhi: eso lo explican las entradas `p.`. Las pistas propias del que aprende van como comentario `sound` y aparecen en tarjetas, cuaderno y log.
- **Tarjetas de tonos**: llevan el recordatorio de qué número es cada tono.
- **Trampas fonéticas**: reglas en `anki.py` (`PHONETIC_TRAPS`) detectan en el pinyin lo que un hispanohablante lee mal (x, q, j, r, zh/ch/sh, z/c, ü, i muda, e no española, -ian, -ui, -iu, -un, -ong, h, aspiración) y lo muestran solas en las tarjetas de escucha, voz alta y tonos, como mucho 3 por tarjeta. Una regla nueva se añade a la tabla, nunca como nota suelta en una palabra. Notas a mano solo para las pistas del que aprende (`sound`) y las entradas `p.`.
- **Pinyin** siempre visible en las soluciones. Colores solo para alinear hanzi y pinyin, nunca para marcar tonos. No se promete corregir el habla: `speak` es autoevaluación.

## Anki

- Mazo `🐉 Chino práctico`. **Nivel primero y tema dentro** (`🐉 Chino práctico::HSK 1::04 Presentarse`; ver «Niveles»), con los temas numerados por orden de aprendizaje a partir de `themes.yaml`. **Etiquetas** para lo que admite varios valores: `tema::`, `mes::`, `use::`, `skill::`, `type::` y `nivel::`. La estructura de temas se revisa en cada lote (ver «Reorganización»).
- **`push`**: compila, abre Anki si hace falta, importa por AnkiConnect (complemento `2055492159`) y sincroniza con AnkiWeb. Anki no mueve tarjetas de deck al reimportar: `push` las recoloca con AnkiConnect conservando el progreso (también las de este mazo que hayan acabado fuera de él, en el mazo por defecto o donde sea, salvo en mazos filtrados; las reconoce por su tipo de nota), y borra los subdecks propios que queden vacíos y no correspondan a ningún tema (renombrar un tema funciona así solo). Detecta notas del mazo cuyo ejercicio ya no existe y propone borrarlas, mostrando cuáles.
- **Orden de nuevas**: `push` fija la posición de cada nueva (`reorder_new`) y, en el preset, que Anki las recoja por esa posición y no las baraje (`NEW_GATHER_LOWEST_POSITION`, `NEW_SORT_NONE`; al azar mezclaría niveles). Las tarjetas de una misma entrada no se introducen el mismo día (Anki solo separa hermanas de una misma nota y aquí cada tarjeta es una nota); los básicos primero.
- **Límites**: nuevas y repasos al día como máximo (`NEW_PER_DAY`, `REVIEWS_PER_DAY` en `anki.py`; los valores de este mazo, en `docs/owner.md`), fijados por `push` en un preset propio, junto con los pasos de aprendizaje y reaprendizaje (`LEARN_STEPS`, `RELEARN_STEPS`, en minutos: lo nuevo y lo fallado vuelven en la misma sesión, no al día siguiente). A ritmo estable los repasos diarios son del orden de 5 a 8 veces las nuevas (proporcional, no geométrico: a unos 10 s por tarjeta, 20 nuevas son unos 25 a 30 minutos al día); `use` mantiene el total asumible hasta el nivel objetivo (`docs/goal.md`). Un cambio a mano en Anki se pierde en el siguiente `push`.
- **GUID** = `guid_for("apkg-chinese-structs", id del ejercicio)`; IDs de modelo fijos en `anki.py`. Reimportar actualiza sin duplicar y conserva el progreso (ver «Lotes disruptivos»).
- **Nunca se corrige dentro de Anki**: cada `push` sobrescribe desde `3-data/`.
- **`push --reset`** devuelve todo el mazo a nuevas con repasos y fallos a 0. Solo este mazo; el registro de repasos de Anki se conserva. Anki sigue contando las nuevas ya empezadas ese día, así que el reinicio se nota del todo al día siguiente. Con la fase de pruebas cerrada (`TESTING_PHASE`; ver `docs/owner.md`) se niega salvo `--force`.
- Los otros mazos de la colección son independientes (regla en `AGENTS.md`): nada de `anki.py` los mueve, borra, reconfigura ni cuenta.

## Audio

- Azure Speech por REST; voz, velocidades y silencio inicial en `anki.py` (`AZURE_VOICE`, `AZURE_RATE`, `AZURE_RATE_WORD` para palabras sueltas de hasta 3 hanzi, `AZURE_LEAD_MS`), con los valores y su motivo en `docs/owner.md` y `docs/decisions.md`. Caché por **texto chino exacto** en `3-data/audio/index.yaml`: editar consigna, significado o comentarios no regenera nada; cambiar el hanzi de una respuesta o frase sí (solo si estaba mal). Un texto se genera una vez y se reutiliza.
- El audio de una frase solo vale para esa frase exacta: pocas frases útiles y estables, reutilizadas como ejemplo y en textos de comprensión, mejor que variantes casi iguales.
- **Licencia**: solo el audio generado en un nivel de pago puede redistribuirse (`AZURE_TIER`, y `tier` en `index.yaml`); los MP3 se versionan. Al publicar, indicar que el audio es sintético (lo dice el README).
- Un polífono mal leído se corrige fijando la lectura con SSML (`<phoneme alphabet="sapi">`) cuando haga falta.

## Grabaciones de clase

El que aprende puede dejar en `1-inbox/` el audio de una clase (mp3, m4a, mp4…). No es un apunte: es contexto de cómo fue la clase.

- **Transcribir**: `.venv-audio\Scripts\python tools/class_audio.py transcribe 1-inbox/<grabación>` (entorno aparte: Whisper y sus modelos pesan demasiado para `.venv`; ver `docs/owner.md`). Tarda más o menos lo que dura la clase o algo menos. Escribe `private/class-audio/<nombre>/transcript.md`: primero lo que dijo la profesora en chino (con pinyin y, entre 【】, lo que no cubre el mazo), luego las palabras del mazo que usó, lo que no está en el mazo y la clase entera.
- **Quién habla**: por la huella de la voz, comparada con las voces guardadas en `private/class-audio/voices.json`, que cada grabación afina (la primera vez se siembran por el tono). Cuenta la voz de la profesora; lo del que aprende se transcribe mal porque está aprendiendo, así que sale marcado y fuera del resumen. Lo que la profesora dice en inglés, Whisper (forzado a chino) a veces lo traduce: se detecta y se marca «[inglés]».
- **Cómo se usa**: para saber qué se trabajó en clase, confirmar lo apuntado (sentido, lectura, frase exacta de la profesora) y señalar en el review lo que se enseñó y no se apuntó. Una transcripción automática no es fuente segura: lo que entre por ella se comprueba como un apunte transcrito de foto (⚠️ en el log y «Por verificar» si hay duda). Lo que consta que dijo la profesora puede ir como comentario `teacher`.
- **Privacidad**: la grabación y la transcripción llevan la voz y las palabras de la profesora y la clase entera; no se versionan nunca. `close-batch` mueve la grabación a `private/class-audio/<nombre>/`, junto a su transcripción (no a `1-inbox/history/`), y se niega a cerrar si está sin transcribir. Nada de la transcripción se copia tal cual a lo versionado; la profesora, siempre sin nombre.

## Repositorio y privacidad

- Repositorio `yago-mendoza/apkg-chinese-structs`, **público**: nada privado en `3-data/`, ninguna credencial. UTF-8 explícito.
- **Citas de libros en los apuntes**: si un apunte copia texto literal de un libro con derechos (citas largas, con su página), el archivo de `1-inbox/history/` guarda el apunte con esas citas retiradas y marcadas («[cita de un libro retirada]»), y el apunte íntegro se guarda en `private/` (fuera de git). Lo escrito con palabras propias se archiva tal cual. Solo se retira la copia literal (lo que va entre comillas o con su página): una explicación de la misma idea con otras palabras, otro orden u otro idioma se queda, sin nombrar el libro.
- Fuera de git: las grabaciones de clase y sus transcripciones (`private/class-audio/`), la caja negra (`private/blackbox.jsonl`), los apuntes pendientes de `1-inbox/` (sí se versionan su README y el review), `5-output/` salvo la exportación y el mazo compilado, y el entorno. `1-inbox/history/` se versiona: los apuntes no son privados. Antes de archivar un lote en `1-inbox/history/`, revisar que no haya datos sensibles (claves, correos, teléfonos).
- **Git**: `close-batch` hace el commit y la etiqueta del lote (en local); cualquier otro commit, cuando se pida; push a GitHub solo cuando se pida.
- Fuentes externas versionadas: `sources/`, cada una con su origen y su licencia en su `README.md`. Hoy, el vocabulario del HSK 3.0 de `drkameleon/complete-hsk-vocabulary` (MIT; solo nivel, frecuencia y pinyin, no sus glosas CC-CEDICT) y la descomposición de caracteres de `skishore/makemeahanzi` (`sources/hanzi/`, LGPL 3; se usan sus piezas y qué da el sonido o el significado, no sus glosas; lo que llega a las tarjetas son hechos redactados con palabras propias, así que el contenido sigue siendo CC BY). Dong Chinese no se descarga (su `robots.txt` pide que no la rastreen programas); SUBTLEX-CH, si hace falta, solo en local.
- Materiales solo locales: manuales de curso y libros de caracteres que no se pueden redistribuir. Viven fuera del repositorio; `private/README.md` (en `.gitignore`) dice dónde están y cómo se usan. Nada del repositorio depende de ellos, nada se copia de ellos y no se nombran en nada versionado: lo que aporten entra redactado con palabras propias y comprobado con fuentes abiertas.
- Licencia: MIT para el código, CC BY 4.0 para el contenido; cita obligatoria, uso comercial permitido. Lo que entre de terceros en el contenido tiene que ser compatible con CC BY; `sources/` conserva la licencia de cada fuente.
- **Exportación pública** (`anki.py export` → `5-output/dictionary.json`, versionado; `close-batch` la regenera antes del commit, así que cada etiqueta `lote-NNN` lleva la suya). Es el contrato con InfraPhysics: lista explícita de campos publicables (temas; entradas con pinyin, AFI, significado, `use`, nivel, `levelEstimated`, `onHskList`, `entryType` —word, charword, bound, component, expression, structure o pronunciation—, `connection`, grupos y comentarios públicos; frases), las tarjetas con lo que entrenan y enseñan (`targets`, `context` y `examples`, las frases del reverso) y tal como las muestra Anki (el mismo HTML de `card_fields`, con el audio como botón, y el mismo CSS del modelo en `cardCss`, para que la web no mantenga una copia de los estilos), el historial día a día sacado de git (tarjetas añadidas por nivel, editadas y retiradas; la propia exportación guarda hasta qué commit está calculado, `historyCache`, y la siguiente solo lee los commits nuevos) y el mazo compilado (`5-output/chino-practico.apkg`, que `export` genera y se versiona para poder descargarlo), `schemaVersion` y atribución CC BY; nunca comentarios privados ni el campo `original`. El audio va por ruta dentro del repositorio y se sirve con jsDelivr fijado a una versión: `https://cdn.jsdelivr.net/gh/yago-mendoza/apkg-chinese-structs@<versión>/<ruta>`. InfraPhysics la consume en `/side-quests/chinese`: al cargar, la página lee la exportación de `@main` en jsDelivr (con la copia incluida en su código como respaldo), y el workflow `publish` purga esa caché de jsDelivr tras cada push que cambie `5-output/`, así que la web se actualiza sola en un par de minutos. Un cambio incompatible del formato sube `EXPORT_SCHEMA`.

## Garantías: qué asegura el código y qué el criterio

Todo lo que se puede decidir con datos se decide con atributos y lo comprueba `check` (error: bloquea el lote; aviso: hay que resolverlo o justificarlo antes de cerrar). Lo que necesita criterio lo decide el agente, pero deja rastro escrito que se puede revisar. Una regla nueva sigue el orden de arriba (entrada en `docs/decisions.md`, regla aquí o en `docs/goal.md`) y, si se puede comprobar, entra en `quality_rules` (`anki.py`) con su prueba en `tests/`.

| Regla | Cómo se asegura |
|---|---|
| Tarjetas exigidas por `use`, redundancia, ósmosis | `check` (error / aviso) |
| Nivel de cada entrada | `check`: error si no hay nivel oficial ni `level` con `level_reason` |
| `use` frente al nivel | `check`: aviso si HSK 1 es solo lectura o HSK 7 es para decir, sin `use_reason` |
| Estatus del carácter (palabra, ligada, componente) | `check`: error si un carácter no declara `standalone` o un componente pide oírse o decirse, y si un componente cuyo hanzi es palabra (lista del HSK o mazo) no lleva `as_word`; el reverso lo muestra calculado |
| El pinyin por delante | `check`: error si la escucha o la producción de una palabra no piden escribir; `scaffold` genera dictado |
| Ejemplos sin vocabulario de un nivel superior | código (`examples_for`) y prueba |
| Frase de cada hueco | regla fija (`cloze_sentence`); `check` avisa de frases repetidas o de nivel superior |
| Frases completas | `check`: error si un trozo en chino no enlaza a una entrada |
| Notas bien redactadas | `check`: aviso (mayúscula, punto, sin símbolos de apunte) |
| Otros niveles marcados en las notas | `check`: aviso si una palabra de la lista de nivel superior, fuera del mazo, no lleva «[HSK n]» |
| Fuentes privadas | `check`: error si lo versionado nombra un término de `private/forbidden.txt` (lista local) |
| Audio completo, referencias, IDs, temas | `check` (error) |
| Qué entra y para qué (`use`), nivel estimado, tema, volumen del lote | criterio del agente con `docs/goal.md`; queda en `use_reason` y `level_reason` y en el log |
| Frases naturales, mnemotecnias, conexiones, series fonéticas | criterio del agente; se revisan en el review |
| Citas de libros | criterio: fuera la copia literal (en `original` y en el apunte archivado); la paráfrasis se queda, sin nombrar la fuente (ver «Repositorio y privacidad») |
| Grabaciones de clase fuera de git | `close-batch` las mueve a `private/` con su transcripción y no cierra si falta; prueba en `tests/` |
| Desván: nada se pierde ni se olvida | `check` (campos, un hanzi por elemento, aviso si ya está en el mazo); `attic_awake` decide qué despierta; `close-batch` no cierra con despiertos sin pasar ni `snooze` |
| Categoría gramatical | calculada de la lista del HSK (`pos_of`); `check`: error si falta, aviso si `pos` la contradice sin `pos_reason` |
| Estructuras bien formadas | `check` (`grammar_rules`): piezas fijas enlazadas y en orden en cada ejemplo; aviso si un hueco lo ocupa otra categoría |
| Conexiones entre hanzi | `check` (`connection_rules`): error si una conexión enlaza con un carácter que no está en el mazo; aviso si es de un nivel superior o si un carácter comparte la pieza que da el sonido con otro del mazo y ninguna nota lo dice (datos de `sources/hanzi/`); prueba en `tests/` |
| Un recuadro de conexión por tarjeta | código (`connection_for`): el de la entrada o, si no tiene, el de su primer carácter que lo tenga; prueba en `tests/` |
| Solo mandarín estándar | `check`: error si una forma con erhua (哪儿) no está descartada o si una frase usa algo descartado (`standard_rules`); prueba en `tests/` |
| Lo que suena igual, contrastado | `check`: aviso si dos palabras del mazo suenan igual sin tonos y no comparten grupo; los grupos `soundalike` y `homophone` exigen tarjeta de contraste con audio; prueba en `tests/` |
| Lo que se confunde aparece junto | código (`examples_for`): si el objetivo tiene pareja en un grupo de contraste o de serie, el último ejemplo del reverso es una frase de la pareja (de nivel no superior); prueba en `tests/` |
| Estructura frente a su calco, sin producción libre | `check`: error si una estructura que se practica no tiene `contrast` (frase buena, calco y porqué) o si el calco es igual a la buena; `scaffold` solo genera la tarjeta de elegir; prueba en `tests/` |
| Comprensión lectora bien hecha, nunca en pinyin solo | `check` (`comprehension_rules`): frases del mazo, texto mínimo, pregunta y respuesta, `script` `hanzi` o `both`; prueba en `tests/` |
| Mnemotecnia frente a origen | criterio al elegir `kind` (`mnemonic` o `linguistic`); la tarjeta lo rotula |
| Review con lo imprescindible arriba | `close-batch` (`review_rules`): «Sine qua non» primero, como mucho `SINE_QUA_NON_MAX` puntos, cada uno con enlace y línea «>»; ningún enlace roto; prueba en `tests/` |
| Estado al día y con fuentes | `close-batch` (`state_rules`): título con el lote, apartados, un enlace estable por punto y enlaces que existen (archivo y ancla); prueba en `tests/` |
| Fricciones apuntadas | `close-batch`: el log tiene «Fricciones del proceso»; prueba en `tests/` |
| Caja negra solo local | código (`blackbox`): solo escribe si existe `private/`; prueba en `tests/` |
| `stats` no toca nada | solo lectura y solo este mazo; prueba contra el AnkiConnect simulado |
| El progreso no se reinicia por descuido | código: `push --reset` se niega sin `--force` con la fase de pruebas cerrada; prueba contra el AnkiConnect simulado |

## Pruebas

`tests/test_anki.py` (unittest, sin dependencias nuevas): pinyin, tonos, sílabas y erhua, AFI, trampas fonéticas, velocidad del audio, tarjetas exigidas por `use`, ejemplos que respetan el sentido, `scaffold` completo, validez de los datos del repositorio, temas bien formados, nombres de lote, review, estado y enlaces, caja negra, retrospectiva, `stats` y la comparación de respuestas en JavaScript (con node, si está). `tests/test_anki_connect.py` prueba contra un AnkiConnect simulado, con mazos ajenos en la colección, que recolocar, podar, reiniciar, fijar límites y leer estadísticas no tocan nada fuera de este mazo y que la poda masiva se frena sin `--force`. Tras cambiar `anki.py`: `.\.venv\Scripts\python -m unittest discover -s tests`. La CI de GitHub (`.github/workflows/check.yml`) ejecuta `check` y las pruebas en cada push.

## Estado y fases

Las cifras del mazo (entradas, frases, tarjetas, audio pendiente, huecos) no se anotan aquí porque caducan: las da `anki.py gaps` en el momento; cómo va el que aprende, `2-digests/state.md`. Lo que queda por comprobar en uso real, en `docs/owner.md`.

1. Hecho: cobertura por `use`, subdecks por tema, etiquetas, recolocación, datos por tema, frases aparte, log y review, tarjeta de matiz.
2. Hecho: niveles del HSK 3.0 (nivel en cada elemento, subdecks y orden por nivel, ejemplos sin vocabulario superior, cobertura por nivel). **[pendiente]** Las secuencias de curso del nivel actual.
3. Hecho: `stats` (lo que se falla, leído de Anki), estado vivo, review con «Sine qua non», caja negra y retrospectiva, comprensión lectora.
4. **[pendiente]** Pista de pronunciación.

## Fuentes

- [genanki](https://github.com/kerrickstaley/genanki) · [Anki: importar paquetes](https://docs.ankiweb.net/importing/packaged-decks.html) · [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
- [pypinyin](https://github.com/mozillazg/python-pinyin) · [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) · [Make Me a Hanzi](https://github.com/skishore/makemeahanzi)
- [Dong: palabras de películas](https://www.dong-chinese.com/dictionary/topMovieWords), [componentes](https://www.dong-chinese.com/dictionary/topComponents), [orden de caracteres](https://www.dong-chinese.com/dictionary/dongChinese)
- [Azure Speech](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech) · [precios](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/) · [uso del audio según nivel (Q&A)](https://learn.microsoft.com/en-us/answers/questions/5805156/please-clarify-the-conflicting-information-regardi)

Condiciones y precios se vuelven a comprobar al implementar cada parte.
