# Diseño — chino práctico, pinyin y audio

Especificación canónica para agentes. Cada regla se dice una vez, aquí. Para YAGO: `README.md` (uso y mapa de carpetas). Las partes sin implementar llevan **[pendiente]** y su fase (ver «Estado y fases»).

## Objetivo

Mandarín cotidiano y de trabajo hasta un nivel equivalente a C1, con **mucho énfasis en fluidez y en pronunciación**. YAGO empezó en septiembre de 2026. Nada de vocabulario literario, arcaico o remoto; sí lo necesario para vivir en China, trabajar (es ingeniero) y hablar con algo de personalidad. YAGO estudia en ratos sueltos, casi siempre desde el móvil y siempre con auriculares: el audio está disponible en cualquier sesión.

## Principio

El modelo redacta; `anki.py` calcula y comprueba. Lo que puede calcularse (qué tarjetas faltan, qué sobra, qué audio falta) lo decide el código a partir de reglas escritas aquí, no el criterio del agente en cada sesión. El agente trabaja sobre la diferencia que el código le da (`plan`) y `check` verifica el resultado. `anki.py` no llama nunca a un LLM; compilar no regenera ejercicios.

## Glosario

- **Entrada**: un elemento del diccionario (`4-data/lexicon/`): palabra, expresión, carácter, componente, pronunciación o grupo. Una por sentido.
- **Frase**: oración segmentada (`4-data/sentences/`), reutilizable en varias tarjetas: recurso en sí (`say`) o ejemplo (`hear`).
- **Ejercicio**: una pregunta concreta; en Anki, una nota con una tarjeta.
- **`use`**: para qué necesita YAGO una entrada o frase (`read`, `hear`, `say`, o excepción). Decide las tarjetas exigidas.
- **Rol**: `content` (palabra con significado propio) o `function` (pieza gramatical: se practica en frase).
- **Tema**: agrupación por asunto (`4-data/themes.yaml`); es el archivo en que vive cada elemento y decide el subdeck, el orden de aprendizaje y el cuaderno.
- **Grupo**: entradas que se estudian juntas por contraste (`visual`, `homophone`, `pattern`, `set`).
- **Ósmosis**: que una palabra aparezca como contexto en frases, además de en sus propias tarjetas.
- **Lote**: una entrega de apuntes de YAGO (`NNN-AAAA-MM-DD-tema`).
- **Log** (`3-digests/summary-<lote>.md`): el acta de un lote, lo que el agente decidió y por qué. Se lee; no se reescribe.
- **Review** (`1-inbox/review-<lote>.md`): todo lo que admite la opinión de YAGO, con una línea «>» por punto; con sus respuestas entra en el siguiente lote.
- **Cuaderno**: todo lo aprendido por tema (`5-notebook/`), generado.
- **Trampa fonética**: letra del pinyin que un hispanohablante lee mal; la detecta una regla.

## Flujo de un lote

Un lote es una entrega de apuntes. Se nombra `NNN-AAAA-MM-DD-tema` (número de orden de procesado, fecha, tema en palabras; nunca números de hoja). El lote solo sirve para llevar la cuenta de la procedencia: dentro del mazo cada cosa va donde le toca por tema y nivel, y un ajuste sobre algo antiguo corrige la entrada antigua.

1. YAGO deja archivos en `1-inbox/`, en cualquier formato y con cualquier nombre (o los pega en el chat y el agente los guarda allí tal cual). Todo archivo salvo `README.md` y `review-*.md` es apunte pendiente. Las fechas de los apuntes, si las hay, van a `source.date` de lo que salga de cada parte; si un archivo mezcla días, se respeta la fecha de cada parte.
2. El agente lee también el `review-*.md` del lote anterior: cada línea «>» con texto es una instrucción de YAGO (meter, descartar, matizar, corregir); vacía, no cambia nada. Si YAGO pide una tarjeta de matiz, es `type: nuance`.
3. Para cada elemento: `lookup`; decide si es nuevo, corrige algo o amplía una entrada o grupo. Lo parecido a lo existente (forma, sonido, patrón) va a esa entrada, a `relations` o a un grupo, no a tarjetas sueltas.
4. Asigna `use` a cada entrada nueva (ver «Cobertura»), con motivo cuando se aparte de las señales de frecuencia.
5. Guarda los comentarios de YAGO literalmente y en su ámbito (ver «Comentarios»). Lo que parezca privado no va a `4-data/`: se pregunta.
6. Pregunta lo ambiguo (sentido, lectura, si ya lo sabe) en vez de adivinar. Las transcripciones de fotos hechas por LLM traen errores y `[¿?]`: se marcan con ⚠️ en el log y van a «Por verificar» del review, nunca se dan por buenas.
7. `plan` → `scaffold --write` escribe las tarjetas estándar de lo que falta (siempre con el mismo formato) → el agente revisa sus consignas y redacta a mano lo que `scaffold` marca «a mano» → `check` sin errores ni avisos pendientes.
8. Escribe el log en `3-digests/summary-<lote>.md` y el review en `1-inbox/review-<lote>.md` (`plan --doc <lote>` lo empieza con «Falta»; el agente completa el resto).
9. Pone a cada apunte del inbox su prefijo de fecha y ejecuta `close-batch <lote>` (primero con `--dry-run`): mueve los apuntes y el review leído a `2-raw/<lote>/`, regenera el cuaderno, hace commit y pone la etiqueta `lote-NNN`; se niega si falta algo o `check` tiene errores. Cada apunte se archiva como `AAAA-MM-DD_<nombre original>`, con la fecha en que se apuntó (la que YAGO escribe dentro); si mezcla días, `mixto_<nombre original>` y la fecha de cada parte dentro; si no tiene fecha, `sin-fecha_<nombre original>` y se usa la de procesado en `source.date`. El review conserva su nombre. Sin subcarpetas por día: el prefijo ya ordena. Dos fechas distintas: la del lote (procesado) y la de cada apunte (cuándo se aprendió). `1-inbox/` queda con su `README.md` y el review nuevo.
10. `audio` y `push` antes del cierre; después, resumen a YAGO: añadido, cambiado, reorganizado, tarjetas antiguas tocadas y audio nuevo. Subir a GitHub (commit y etiqueta) cuando YAGO lo pida.

**Log y review**: dos documentos con dos autores. Ambos empiezan con un comentario que explica qué son (`LOG_HEADER` y `REVIEW_HEADER` en `anki.py`) y van **por temas, sin números de hoja ni de página**, una línea por elemento: `汉字 pinyin · significado · pista (relación, mnemotecnia, pronunciación) · ejemplo`.

- **Log** (`3-digests/`, del agente, lectura): el acta completa del lote: lo que entró (✅, 🃏 si tiene tarjeta), lo que no (🟡 solo reconocer, ❌ literario, arcaico o en desuso) con su motivo, las correcciones ⚠️ de glosas y las reorganizaciones.
- **Review** (`1-inbox/`, para YAGO, editable): solo lo que admite su opinión: «Falta» (palabras `say` sin frase, calculado), «✅ Entró, con matices para ahondar» (solo los que traen relación, mnemotecnia, registro o corrección), «Pendiente: ✅ sin tarjeta todavía», «No entró, y por qué», «Por verificar» y «Tus notas». Debajo de cada punto, una línea `  > `. Con las respuestas va a `2-raw/` del lote siguiente.

Histórico: un log no se reescribe. Si YAGO corrige algo después (por el chat o por el inbox), el cambio va a `4-data/` y el log recibe al final «Cambios posteriores» con la fecha. Que algo se repita en los apuntes de varios lotes es una señal: si está como `hear` y reaparece, se propone subirlo a `say` en el review.

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
- **`use`**: subir lo que se repite en los apuntes o YAGO pide decir; bajar lo que resulta que no usa.
- **Frases y entradas**: fusionar duplicados y separar sentidos que estaban mezclados (IDs nuevos para lo separado; los antiguos no se reutilizan).

Cómo: mover un elemento de tema es moverlo de archivo en `4-data/` (y sus ejercicios, al archivo del mismo tema); renombrar o reordenar temas es editar `themes.yaml`. `push` recoloca las tarjetas en Anki conservando el progreso y borra los subdecks que queden vacíos. Toda reorganización se cuenta en el log del lote, con qué se movió y por qué.

## Lotes disruptivos: qué protege y cómo se recupera

Un lote puede tocar mucho (reorganizar temas, corregir cientos de tarjetas). Lo que lo hace seguro:

- **La identidad de una tarjeta es el ID de su ejercicio**, no su texto, su tema ni su archivo. Moverla o corregirla conserva el progreso en Anki. Solo lo pierde si su ejercicio desaparece y se borra con `--prune`.
- **El audio va por texto chino exacto.** Reorganizar no toca audio; cambiar un hanzi pide audio nuevo (céntimos) y `check` bloquea hasta que exista. Los MP3 que dejan de usarse quedan sin estorbar.
- **`check` bloquea** referencias rotas, IDs repetidos entre archivos, tarjetas exigidas ausentes, pinyin que no cuadra y audio que falta. Y **compara con la última etiqueta `lote-NNN`**: avisa de ejercicios desaparecidos (tarjetas que quedarían huérfanas), de preguntas que cambian de respuesta o de tipo con el mismo ID (deben llevar ID nuevo) y de ejercicios archivados en un tema distinto al de su objetivo. El paso 7 del flujo exige resolver los avisos antes de subir.
- **Borrar en Anki nunca es automático**: `push --prune` lista las huérfanas y, si son más de `PRUNE_MAX`, se niega salvo `--force`.

Recuperación: el estado tras cada lote está en su etiqueta `lote-NNN`. Volver a él es restaurar `4-data/` desde la etiqueta y hacer `push`: el contenido y la colocación de las tarjetas vuelven; el progreso de las que sigan existiendo nunca se tocó. Lo único irrecuperable desde el repositorio son las notas borradas con `--prune`; para eso quedan las copias automáticas de Anki (Herramientas → Copias de seguridad).

Entradas que absorbe el inbox: texto en cualquier formato e imágenes (fotos de apuntes: el agente las lee). Audio o vídeo, no directamente: primero hay que transcribirlos.

## Capas y carpetas

| Capa | Orden | Contenido |
|---|---|---|
| `2-raw/<lote>/` | cronológico, intocable | lo que YAGO escribió, tal cual; versionado |
| `3-digests/summary-<lote>.md` | cronológico; temático por dentro | el log de cada lote, del agente; histórico, no se reescribe |
| `4-data/<carpeta>/<tema>.yaml` | por tema y concepto, sin cronología | fuente de verdad; la cronología solo como `source.batch` y `added` |
| `5-notebook/` | temático, acumulado | todo lo aprendido por tema, generado desde `4-data/` en cada lote; nunca se edita |
| Anki | por tema + etiquetas | estudio |

Mapa completo y convenciones de nombres: `README.md`.

## Datos

Un archivo por tema en `4-data/lexicon/` (entradas), `4-data/sentences/` (frases) y `4-data/exercises/` (tarjetas); los temas y su orden, en `4-data/themes.yaml`. El tema de cada elemento es el archivo en que vive: moverlo de tema es moverlo de archivo, y los ejercicios van en el tema de su primer objetivo. Esquema de campos: `4-data/README.md`. `check` da error si un archivo no corresponde a ningún tema o si un tema está mal formado.

- **IDs** con prefijo de tipo (`w.` palabra, `e.` expresión, `c.` carácter o componente, `p.` pronunciación, `g.` grupo, `s.` frase, `x.` ejercicio). Nunca se reutilizan ni se cambian; no usar solo el hanzi. Corregir conserva el ID; cambiar lo que pregunta una tarjeta exige ID nuevo.
- **Una entrada por sentido y lectura** (行 háng / xíng). `standalone: yes | rare | no` es del sentido: si no se usa solo, `check` exige alguna palabra registrada que lo contenga.
- **Grupos** (`kind: group`): `basis: visual | homophone | pattern | set` (set: serie de significado, como las partes del día), miembros con `cue` (rasgo distintivo). Máximo 4 en contraste. Toda tarjeta cuyo objetivo es miembro de un grupo muestra el grupo en el reverso con el objetivo marcado (si está en un set y en un pattern, basta el set). Se crean cuando YAGO ya conoce un miembro o los ha confundido, nunca por adelantado. Tarjetas: `contrast` (una por miembro) y `derive` (de un miembro del patrón a otro).
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

`kind`: `mnemonic` (subjetivo), `teacher` (solo si consta que lo dijo la profesora), `linguistic` (verificado), `note` (apunte literal de YAGO de origen sin precisar), `sound` (pista de pronunciación de YAGO, literal, como «xiEnshAng»; se muestra como «Cómo suena»). Literal siempre; una mnemotecnia no se presenta como etimología. `private: true` por defecto y nada privado sale en ninguna salida; como el repositorio es público, lo privado ni siquiera se guarda en `4-data/`. Una observación nueva de YAGO («先生 se pronuncia…») va a su hogar según esta tabla y aparece en todas las tarjetas afectadas.

## Cobertura: `use`, `plan` y `check`

Cada entrada declara **para qué la necesita YAGO**:

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
| carácter o componente | componentes, si está en una palabra que se estudia | — | — |
| pronunciación `p.` | — | escucha | + voz alta |

Además, calculado del pinyin: tarjeta de tonos para toda entrada `hear` o `say` con tono neutro o sandhi (3+3, 不, 一). El erhua se detecta pero lo trata la pista de pronunciación. La producción suelta tecleada se reserva para el núcleo; el peso de la producción va a frases y frases hechas, que son lo más rentable para tonos en contexto y fluidez.

**Ósmosis**: toda palabra `say` o `context` aparece como contexto en al menos una frase; aviso si no. Las expresiones que ya son un enunciado completo (你好, 再见) no lo necesitan. Antes de pedir frases a YAGO, se buscan en sus apuntes de `2-raw/`. Que una entrada reaparezca como contexto en muchas frases es deseable y no cuenta como redundancia.

**Señales de prioridad** (orientan, no deciden): frecuencia hablada (subtítulos de cine: Dong Chinese o SUBTLEX-CH) para qué es núcleo, y bandas del HSK 3.0 como control de huecos hacia C1. `check` avisa cuando `use` choca con ellas (banda 1 marcada `read`; banda 7–9 marcada `say`) y pide motivo. Las necesidades de YAGO (工程师, 买单) justifican excepciones. Nunca se importa un ranking entero. [pendiente, fase 4]

**`plan`** lista, para todo el mazo, las tarjetas exigidas que faltan y los avisos de ósmosis y señales. **`check` estricto** convierte en error cualquier tarjeta exigida ausente. **`gaps`** informa del reparto por capacidad (lectura, escucha, producción, tonos), contando cada tarjeta solo por lo que practica.

## Pronunciación: pista propia [pendiente, fase 3]

Las listas de frecuencia ordenan palabras, no sonidos; la pronunciación necesita cobertura propia, calculada:

- **Parejas de tonos**: las combinaciones de dos sílabas (1-1 … 4-neutro), clasificadas automáticamente desde el pinyin; `check` exige escucha y producción de cada pareja con varias palabras.
- **Sonidos difíciles**: aspiración (b/p, d/t, g/k), j q x frente a zh ch sh r, ü, -n frente a -ng; pares mínimos desde el vocabulario de YAGO.
- **Sandhi, neutro y erhua**, detectados desde el pinyin.
- Se practican por separado el tono de cita de cada palabra y la melodía real de las frases: el sandhi y el neutro esconden el tono de cita.

## Tarjetas

- **Tipos**: `read` (hanzi → pinyin y significado), `listen` (audio → pinyin o comprensión), `produce` (español → chino), `cloze` (hueco en frase), `tones` (un dígito por sílaba: 什么 → `25`; desde audio o desde pinyin sin tonos; `check` reconstruye el pinyin y verifica), `speak` (voz alta y comparar), `contrast`, `derive`, `components`, `nuance` (matiz o confusión concreta que YAGO pide desde el review: «¿qué aporta 公 en 公司 y en 公主?»; nunca exigida, sin audio). Una pregunta concreta por tarjeta.
- **Tecleadas frente a autoevaluación**: YAGO estudia desde el móvil; se teclea en tonos y producción del núcleo, el resto es autoevaluación. En las frases para decir, escribir es opcional (caja «escríbelo si quieres»). **Normalización**: vale pinyin (tildes o dígitos, `v` = `ü`) o hanzi; espacios, mayúsculas y puntuación dan igual; solo cuenta como fallo un error real de sílaba o tono.
- **Audio**: escucha, tonos y pronunciación lo llevan delante; lectura, producción y deducción, tras revelar; el contraste visual y los componentes no llevan (se deciden por la forma); el de homófonos sí. Frases de ejemplo y entradas `p.`, siempre.
- **AFI** (transcripción fonética del tono de cita) en el reverso de palabras y en `5-notebook/`, calculada del pinyin con dragonmapper al compilar; nunca se guarda en `4-data/`. No refleja el sandhi: eso lo explican las entradas `p.`. Las pistas propias de YAGO van como comentario `sound` y aparecen en tarjetas, cuaderno y log.
- **Tarjetas de tonos**: llevan el recordatorio de qué número es cada tono.
- **Trampas fonéticas**: reglas en `anki.py` (`PHONETIC_TRAPS`) detectan en el pinyin lo que un hispanohablante lee mal (x, q, j, r, zh/ch/sh, z/c, ü, i muda, e no española, -ian, -ui, -iu, -un, -ong, h, aspiración) y lo muestran solas en las tarjetas de escucha, voz alta y tonos, como mucho 3 por tarjeta. Una regla nueva se añade a la tabla, nunca como nota suelta en una palabra. Notas a mano solo para las pistas de YAGO (`sound`) y las entradas `p.`.
- **Pinyin** siempre visible en las soluciones. Colores solo para alinear hanzi y pinyin, nunca para marcar tonos. No se promete corregir el habla: `speak` es autoevaluación.

## Anki

- Mazo `🐉 Chino práctico`. **Subdecks por tema**, numerados por orden de aprendizaje (`🐉 Chino práctico::04 Presentarse`), a partir de `themes.yaml` (decisión de YAGO: por fechas, cada subdeck sería un poco de todo). **Etiquetas** para lo que admite varios valores: `tema::`, `mes::`, `use::`, `skill::`, `type::` (y `nivel::` cuando haya niveles). Estudiar el mazo padre lo mezcla todo (lo nuevo y lo antiguo, cuando Anki lo decide), que es como YAGO quiere estudiar; los temas organizan, no separan el estudio. La estructura de temas se revisa en cada lote (ver «Reorganización»).
- **`push`**: compila, abre Anki si hace falta, importa por AnkiConnect (complemento `2055492159`) y sincroniza con AnkiWeb. Anki no mueve tarjetas de deck al reimportar: `push` las recoloca con AnkiConnect conservando el progreso, y borra los subdecks propios que queden vacíos y no correspondan a ningún tema (renombrar un tema funciona así solo). Detecta notas del mazo cuyo ejercicio ya no existe y propone borrarlas, mostrando cuáles.
- **Orden de nuevas**: las tarjetas de una misma entrada no se introducen el mismo día (Anki solo separa hermanas de una misma nota y aquí cada tarjeta es una nota); los básicos primero.
- **Límites**: 30 nuevas al día y 300 repasos como máximo (elegido por YAGO el 2026-09-26: 15 se le quedaba corto), fijados por `push` en un preset propio. A ritmo estable los repasos diarios son del orden de 5 a 8 veces las nuevas (proporcional, no geométrico: a unos 10 s por tarjeta, 30 nuevas son unos 40 minutos al día); `use` mantiene el total asumible hacia C1. Cambiarlo es cambiar `NEW_PER_DAY` en `anki.py`: un cambio a mano en Anki se pierde en el siguiente `push`.
- **GUID** = `guid_for("apkg-chinese-structs", id del ejercicio)`; IDs de modelo fijos en `anki.py`. Reimportar actualiza sin duplicar (comprobado el 2026-09-25); la conservación del historial tras repasar está por comprobar.
- **Nunca se corrige dentro de Anki**: cada `push` sobrescribe desde `4-data/`.
- **Fase de pruebas** (hasta que YAGO dé el sistema por estable): `push --reset` devuelve todo el mazo a nuevas con repasos y fallos a 0, a petición de YAGO. Solo este mazo; el registro de repasos de Anki se conserva. Anki sigue contando las nuevas ya empezadas ese día, así que el reinicio se nota del todo al día siguiente. Cuando el sistema sea estable, no se reinicia: el progreso se conserva.
- Los otros mazos de la colección de YAGO son independientes (regla en `AGENTS.md`).

## Audio

- Azure Speech por REST, voz `zh-CN-YunyangNeural` (clara y estable, elegida por YAGO), velocidad -30 % en frases y -40 % en palabras sueltas (hasta 3 hanzi), con 200 ms de silencio inicial porque algunos reproductores cortan el primer instante (上午 se oía «shòu»). Caché por **texto chino exacto** en `4-data/audio/index.yaml`: editar consigna, significado o comentarios no regenera nada; cambiar el hanzi de una respuesta o frase sí (solo si estaba mal). Un texto se genera una vez y se reutiliza.
- El audio de una frase solo vale para esa frase exacta: pocas frases útiles y estables, reutilizadas como ejemplo, mejor que variantes casi iguales.
- **Licencia**: según los Product Terms de Microsoft (citados en su Q&A), solo el nivel de pago da derecho de uso del audio generado. El recurso está en **S0** desde el 2026-09-27 y todo el audio se regeneró ahí (`tier: S0` en `index.yaml`); los MP3 se versionan. Al publicar, indicar que el audio es sintético (lo dice el README).
- Voces HD descartadas por ahora: más naturales pero menos estables para fijar tonos; se reconsiderarán para frases de escucha largas.
- Un polífono mal leído se corrige fijando la lectura con SSML (`<phoneme alphabet="sapi">`) cuando haga falta.

## Repositorio y privacidad

- Repositorio `yago-mendoza/apkg-chinese-structs`, **público**: nada privado en `4-data/`, ninguna credencial. Local en `C:\Users\yagom\dev\apkg-chinese-structs`, Python en `.venv`, UTF-8 explícito.
- Fuera de git: los apuntes pendientes de `1-inbox/` (sí se versionan su README y el review), `6-output/` y el entorno. `2-raw/` se versiona (decisión de YAGO, 2026-09-27): los apuntes no son privados. Antes de archivar un lote en `2-raw/`, revisar que no haya datos sensibles (claves, correos, teléfonos).
- Commits cuando YAGO lo pida; push a GitHub solo cuando lo pida.
- Fuentes externas: HSK 3.0 de `drkameleon/complete-hsk-vocabulary` (MIT; se puede versionar con su aviso de licencia; solo nivel y pinyin, no sus glosas CC-CEDICT). Dong Chinese y SUBTLEX-CH: condiciones sin aclarar, solo en local.
- Licencia (elegida por YAGO, 2026-09-27): MIT para el código, CC BY 4.0 para el contenido; cita obligatoria, uso comercial permitido. Lo que entre de terceros tiene que ser compatible con CC BY.
- **Exportación pública** (`anki.py export` → `6-output/dictionary.json`, versionado; `close-batch` la regenera antes del commit, así que cada etiqueta `lote-NNN` lleva la suya). Es el contrato con InfraPhysics: lista explícita de campos publicables (temas, entradas con pinyin, AFI, significado, `use`, grupos y comentarios públicos, frases y grupos), `schemaVersion` y atribución CC BY; nunca comentarios privados ni ejercicios. El audio va por ruta dentro del repositorio y se sirve con jsDelivr fijado a una versión: `https://cdn.jsdelivr.net/gh/yago-mendoza/apkg-chinese-structs@<versión>/<ruta>`. InfraPhysics la consume en `/corner/chinese` con un script que descarga una versión fijada; actualizar la web es cambiar esa versión. Un cambio incompatible del formato sube `EXPORT_SCHEMA`.

## Pruebas

`tests/test_anki.py` (unittest, sin dependencias nuevas): pinyin, tonos, sílabas y erhua, AFI, trampas fonéticas, velocidad del audio, tarjetas exigidas por `use`, ejemplos que respetan el sentido, `scaffold` completo, validez de los datos del repositorio, temas bien formados, nombres de lote y la comparación de respuestas en JavaScript (con node, si está). Tras cambiar `anki.py`: `.\.venv\Scripts\python -m unittest discover -s tests`.

## Estado y fases

Las cifras del mazo (entradas, frases, tarjetas, audio pendiente, huecos) no se anotan aquí porque caducan: las da `anki.py gaps` en el momento.

Por comprobar en uso real: que el cliente móvil de YAGO conserva lo escrito entre anverso y reverso (si no, las tarjetas escritas quedan como autoevaluación) y que el historial de repaso se conserva al reimportar.

1. ~~Fase 1~~ hecha.
2. ~~Fase 2~~ hecha: subdecks por tema, etiquetas, recolocación, datos por tema, frases aparte, log y review, tarjeta de matiz.
3. Pista de pronunciación.
4. HSK 3.0 y frecuencia hablada como señales.
5. `stats`: leer fallos de Anki por AnkiConnect y convertir las tarjetas problemáticas en huecos del siguiente lote.


## Fuentes

- [genanki](https://github.com/kerrickstaley/genanki) · [Anki: importar paquetes](https://docs.ankiweb.net/importing/packaged-decks.html) · [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
- [pypinyin](https://github.com/mozillazg/python-pinyin) · [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary)
- [Dong: palabras de películas](https://www.dong-chinese.com/dictionary/topMovieWords), [componentes](https://www.dong-chinese.com/dictionary/topComponents), [orden de caracteres](https://www.dong-chinese.com/dictionary/dongChinese)
- [Azure Speech](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech) · [precios](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/) · [uso del audio según nivel (Q&A)](https://learn.microsoft.com/en-us/answers/questions/5805156/please-clarify-the-conflicting-information-regardi)

Consultadas entre el 25 y el 26 de septiembre de 2026; condiciones y precios se vuelven a comprobar al implementar cada parte.
