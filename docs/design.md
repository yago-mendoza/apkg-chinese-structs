# Diseño — chino práctico, pinyin y audio

Especificación canónica para agentes. Cada regla se dice una vez, aquí. Para YAGO: `README.md` (uso y mapa de carpetas). Las partes sin implementar llevan **[pendiente]** y su fase (ver «Estado y fases»).

## Objetivo

Mandarín cotidiano y de trabajo hasta un nivel equivalente a C1, con **mucho énfasis en fluidez y en pronunciación**. YAGO empezó en septiembre de 2026. Nada de vocabulario literario, arcaico o remoto; sí lo necesario para vivir en China, trabajar (es ingeniero) y hablar con algo de personalidad. YAGO estudia en ratos sueltos, casi siempre desde el móvil y siempre con auriculares: el audio está disponible en cualquier sesión.

## Principio

El modelo redacta; `anki.py` calcula y comprueba. Lo que puede calcularse (qué tarjetas faltan, qué sobra, qué audio falta) lo decide el código a partir de reglas escritas aquí, no el criterio del agente en cada sesión. El agente trabaja sobre la diferencia que el código le da (`plan`) y `check` verifica el resultado. `anki.py` no llama nunca a un LLM; compilar no regenera ejercicios.

## Glosario

- **Entrada**: un elemento del diccionario (`3-data/lexicon.yaml`): palabra, expresión, carácter, componente, pronunciación o grupo. Una por sentido.
- **Frase**: oración segmentada en `3-data/exercises.yaml`, reutilizable en varias tarjetas.
- **Ejercicio**: una pregunta concreta; en Anki, una nota con una tarjeta.
- **`use`**: para qué necesita YAGO una entrada o frase (`read`, `hear`, `say`, o excepción). Decide las tarjetas exigidas.
- **Rol**: `content` (palabra con significado propio) o `function` (pieza gramatical: se practica en frase).
- **Tema**: agrupación por asunto (`themes` en el diccionario); ordena el aprendizaje, la guía y los subdecks.
- **Grupo**: entradas que se estudian juntas por contraste (`visual`, `homophone`, `pattern`, `set`).
- **Ósmosis**: que una palabra aparezca como contexto en frases, además de en sus propias tarjetas.
- **Lote**: una entrega de apuntes de YAGO (`NNN-AAAA-MM-DD-tema`).
- **Digest**: resumen de un lote para YAGO, clasificado ✅ 🟡 ❌.
- **Gaps**: lo que falta tras un lote y necesita a YAGO (`1-inbox/gaps-<lote>.md`).
- **Guía**: todo lo aprendido por tema (`5-guide/`), generada.
- **Trampa fonética**: letra del pinyin que un hispanohablante lee mal; la detecta una regla.

## Flujo de un lote

Un lote es una entrega de apuntes. Se nombra `NNN-AAAA-MM-DD-tema` (número de orden de procesado, fecha, tema en palabras; nunca números de hoja). El lote solo sirve para llevar la cuenta de la procedencia: dentro del mazo cada cosa va donde le toca por tema y nivel, y un ajuste sobre algo antiguo corrige la entrada antigua.

1. YAGO deja archivos en `1-inbox/`, en cualquier formato y con cualquier nombre (o los pega en el chat y el agente los guarda allí tal cual). Todo archivo salvo `README.md` y `gaps-*.md` es apunte pendiente. Las fechas de los apuntes, si las hay, van a `source.date` de lo que salga de cada parte; si un archivo mezcla días, se respeta la fecha de cada parte.
2. El agente lee también `1-inbox/gaps-*.md` si existe: es parte del lote.
3. Para cada elemento: `lookup`; decide si es nuevo, corrige algo o amplía una entrada o grupo. Lo parecido a lo existente (forma, sonido, patrón) va a esa entrada, a `relations` o a un grupo, no a tarjetas sueltas.
4. Asigna `use` a cada entrada nueva (ver «Cobertura»), con motivo cuando se aparte de las señales de frecuencia.
5. Guarda los comentarios de YAGO literalmente y en su ámbito (ver «Comentarios»). Lo que parezca privado no va a `3-data/`: se pregunta.
6. Pregunta lo ambiguo (sentido, lectura, si ya lo sabe) en vez de adivinar. Las transcripciones de fotos hechas por LLM traen errores y `[¿?]`: se marcan con ⚠️ en el digest, nunca se dan por buenas.
7. `plan` → escribe exactamente las tarjetas que faltan → `check` sin errores ni avisos pendientes.
8. Escribe `4-digests/<lote>.md`, regenera `5-guide/` y el nuevo `1-inbox/gaps-<lote>.md`.
9. Mueve los apuntes y el `gaps-*.md` leído a `2-raw/<lote>/`. Cada apunte se archiva como `AAAA-MM-DD_<nombre original>`, con la fecha en que se apuntó (la que YAGO escribe dentro); si mezcla días, `mixto_<nombre original>` y la fecha de cada parte dentro; si no tiene fecha, `sin-fecha_<nombre original>` y se usa la de procesado en `source.date`. El `gaps` conserva su nombre. Sin subcarpetas por día: el prefijo ya ordena. Dos fechas distintas: la del lote (procesado) y la de cada apunte (cuándo se aprendió). `1-inbox/` queda vacío salvo su `README.md` y el nuevo `gaps`.
10. `audio`, `push`, y resumen a YAGO: añadido, cambiado, tarjetas antiguas tocadas y audio nuevo.

**`1-inbox/gaps-<lote>.md`** es lo que falta tras el lote, con el porqué, para que YAGO lo estudie y lo traiga en el siguiente. Empieza con la línea `<!-- Documento editable: escribe encima, tacha, añade dudas. Todo lo que pongas aquí entra en el siguiente lote. -->`. Solo hay uno a la vez; el anterior se archiva con el lote que lo consume.

## Capas y carpetas

| Capa | Orden | Contenido |
|---|---|---|
| `2-raw/<lote>/` | cronológico, intocable | lo que YAGO escribió, tal cual; versionado |
| `4-digests/<lote>.md` | cronológico; temático por dentro | todo lo que aportó el lote, clasificado; histórico, no se reescribe |
| `3-data/` | por concepto, sin cronología | fuente de verdad; la cronología solo como `source.batch` y `added` |
| `5-guide/` | temático, acumulado | todo lo aprendido por tema, generado desde `3-data/` en cada lote; nunca se edita |
| Anki | por tema + etiquetas | estudio |

Mapa completo y convenciones de nombres: `README.md`.

## Datos

`3-data/lexicon.yaml` (entradas) y `3-data/exercises.yaml` (frases y ejercicios). Encabezados de cada archivo: esquema breve.

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

`kind`: `mnemonic` (subjetivo), `teacher` (solo si consta que lo dijo la profesora), `linguistic` (verificado), `note` (apunte literal de YAGO de origen sin precisar), `sound` (pista de pronunciación de YAGO, literal, como «xiEnshAng»; se muestra como «Cómo suena»). Literal siempre; una mnemotecnia no se presenta como etimología. `private: true` por defecto y nada privado sale en ninguna salida; como el repositorio es público, lo privado ni siquiera se guarda en `3-data/`. Una observación nueva de YAGO («先生 se pronuncia…») va a su hogar según esta tabla y aparece en todas las tarjetas afectadas.

## Cobertura: `use`, `plan` y `check`

Cada entrada declara **para qué la necesita YAGO**:

| `use` | Significa | Digest |
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

- **Tipos**: `read` (hanzi → pinyin y significado), `listen` (audio → pinyin o comprensión), `produce` (español → chino), `cloze` (hueco en frase), `tones` (un dígito por sílaba: 什么 → `25`; desde audio o desde pinyin sin tonos; `check` reconstruye el pinyin y verifica), `speak` (voz alta y comparar), `contrast`, `derive`, `components`. Una pregunta concreta por tarjeta.
- **Tecleadas frente a autoevaluación**: YAGO estudia desde el móvil; se teclea en tonos y producción del núcleo, el resto es autoevaluación. **Normalización**: la plantilla compara tras quitar espacios y mayúsculas, convertir tildes en dígitos y tratar `v` = `ü`, para que solo un error real de sílaba o tono cuente como fallo.
- **Audio**: escucha, tonos y pronunciación lo llevan delante; lectura, producción y deducción, tras revelar; el contraste visual y los componentes no llevan (se deciden por la forma); el de homófonos sí. Frases de ejemplo y entradas `p.`, siempre.
- **AFI** (transcripción fonética del tono de cita) en el reverso de palabras y en `5-guide/`, calculada del pinyin con dragonmapper al compilar; nunca se guarda en `3-data/`. No refleja el sandhi: eso lo explican las entradas `p.`. Las pistas propias de YAGO van como comentario `sound` y aparecen en tarjetas, guía y digest.
- **Tarjetas de tonos**: llevan el recordatorio de qué número es cada tono.
- **Trampas fonéticas**: reglas en `anki.py` (`PHONETIC_TRAPS`) detectan en el pinyin lo que un hispanohablante lee mal (x, q, j, r, zh/ch/sh, z/c, ü, i muda, e no española, -ian, -ui, -iu, -un, -ong, h, aspiración) y lo muestran solas en las tarjetas de escucha, voz alta y tonos, como mucho 3 por tarjeta. Una regla nueva se añade a la tabla, nunca como nota suelta en una palabra. Notas a mano solo para las pistas de YAGO (`sound`) y las entradas `p.`.
- **Pinyin** siempre visible en las soluciones. Colores solo para alinear hanzi y pinyin, nunca para marcar tonos. No se promete corregir el habla: `speak` es autoevaluación.

## Anki

- Mazo `🐉 Chino práctico`. **Subdecks por tema**, numerados por orden de aprendizaje (`🐉 Chino práctico::02 Presentarse`), decididos por el agente [pendiente, fase 2; hoy hay un subdeck por mes, `::2026-09`]. **Etiquetas** para lo que admite varios valores: `nivel::`, `mes::`, `use::`, `skill::`, `type::`. Estudiar el mazo padre lo mezcla todo (lo nuevo y lo antiguo, cuando Anki lo decide), que es como YAGO quiere estudiar; los temas organizan, no separan el estudio. En cada lote el agente revisa si la estructura de temas sigue sirviendo y la reorganiza si hace falta.
- **`push`**: compila, abre Anki si hace falta, importa por AnkiConnect (complemento `2055492159`) y sincroniza con AnkiWeb. Anki no mueve tarjetas de deck al reimportar: `push` las recoloca con AnkiConnect conservando el progreso [pendiente, fase 2]. Detecta notas del mazo cuyo ejercicio ya no existe y propone borrarlas, mostrando cuáles.
- **Orden de nuevas**: las tarjetas de una misma entrada no se introducen el mismo día (Anki solo separa hermanas de una misma nota y aquí cada tarjeta es una nota); los básicos primero.
- **Límites**: 30 nuevas al día y 300 repasos como máximo (elegido por YAGO el 2026-09-26: 15 se le quedaba corto), fijados por `push` en un preset propio. A ritmo estable los repasos diarios son del orden de 5 a 8 veces las nuevas (proporcional, no geométrico: a unos 10 s por tarjeta, 30 nuevas son unos 40 minutos al día); `use` mantiene el total asumible hacia C1. Cambiarlo es cambiar `NEW_PER_DAY` en `anki.py`: un cambio a mano en Anki se pierde en el siguiente `push`.
- **GUID** = `guid_for("apkg-chinese-structs", id del ejercicio)`; IDs de modelo fijos en `anki.py`. Reimportar actualiza sin duplicar (comprobado el 2026-09-25); la conservación del historial tras repasar está por comprobar.
- **Nunca se corrige dentro de Anki**: cada `push` sobrescribe desde `3-data/`.
- **Fase de pruebas** (hasta que YAGO dé el sistema por estable): `push --reset` devuelve todo el mazo a nuevas con repasos y fallos a 0, a petición de YAGO. Solo este mazo; el registro de repasos de Anki se conserva. Anki sigue contando las nuevas ya empezadas ese día, así que el reinicio se nota del todo al día siguiente. Cuando el sistema sea estable, no se reinicia: el progreso se conserva.
- Los otros mazos de la colección de YAGO son independientes (regla en `AGENTS.md`).

## Audio

- Azure Speech por REST, voz `zh-CN-YunyangNeural` (clara y estable, elegida por YAGO), velocidad -30 % en frases y -40 % en palabras sueltas (hasta 3 hanzi), con 200 ms de silencio inicial porque algunos reproductores cortan el primer instante (上午 se oía «shòu»). Caché por **texto chino exacto** en `3-data/audio/index.yaml`: editar consigna, significado o comentarios no regenera nada; cambiar el hanzi de una respuesta o frase sí (solo si estaba mal). Un texto se genera una vez y se reutiliza.
- El audio de una frase solo vale para esa frase exacta: pocas frases útiles y estables, reutilizadas como ejemplo, mejor que variantes casi iguales.
- **Licencia**: según los Product Terms de Microsoft (citados en su Q&A), solo el nivel de pago da derecho de uso del audio generado. El recurso está en **S0** desde el 2026-09-27 y todo el audio se regeneró ahí (`tier: S0` en `index.yaml`); los MP3 se versionan. Al publicar, indicar que el audio es sintético (lo dice el README).
- Voces HD descartadas por ahora: más naturales pero menos estables para fijar tonos; se reconsiderarán para frases de escucha largas.
- Un polífono mal leído se corrige fijando la lectura con SSML (`<phoneme alphabet="sapi">`) cuando haga falta.

## Digest del lote

`4-digests/<lote>.md`, para YAGO: todo el contenido del lote, no solo lo que entra al mazo, comprimido y **por temas, sin números de hoja ni de página**. Una línea por elemento: `汉字 pinyin · significado · pista (relación, mnemotecnia, pronunciación) · ejemplo`, con su marca ✅ 🟡 ❌ (derivada de `use`), 🃏 si está en el mazo y ⚠️ si corrige algo de los apuntes (glosas, transcripción). Al final: qué entró y qué ✅ queda pendiente. Histórico: no se reescribe. Si YAGO corrige algo de un digest (por el chat o por el inbox), el cambio se aplica en `3-data/` y el digest recibe al final una sección «Correcciones posteriores» con la fecha y lo que cambió; lo anterior no se toca.

## Repositorio y privacidad

- Repositorio `yago-mendoza/apkg-chinese-structs`, **público**: nada privado en `3-data/`, ninguna credencial. Local en `C:\Users\yagom\dev\apkg-chinese-structs`, Python en `.venv`, UTF-8 explícito.
- Fuera de git: `1-inbox/` (salvo su README), `6-output/` y el entorno. `2-raw/` se versiona (decisión de YAGO, 2026-09-27): los apuntes no son privados. Antes de archivar un lote en `2-raw/`, revisar que no haya datos sensibles (claves, correos, teléfonos).
- Commits cuando YAGO lo pida; push a GitHub solo cuando lo pida.
- Fuentes externas: HSK 3.0 de `drkameleon/complete-hsk-vocabulary` (MIT; se puede versionar con su aviso de licencia; solo nivel y pinyin, no sus glosas CC-CEDICT). Dong Chinese y SUBTLEX-CH: condiciones sin aclarar, solo en local. No elegir licencia de publicación por YAGO.
- Licencia (elegida por YAGO, 2026-09-27): MIT para el código, CC BY 4.0 para el contenido; cita obligatoria, uso comercial permitido. Lo que entre de terceros tiene que ser compatible con CC BY.
- Futuro (sin fecha): exportación `dictionary.json` para InfraPhysics desde `3-data/`, por lista explícita de campos publicables.

## Estado y fases

Las cifras del mazo (entradas, frases, tarjetas, audio pendiente, huecos) no se anotan aquí porque caducan: las da `anki.py gaps` en el momento.

Por comprobar en uso real: que el cliente móvil de YAGO conserva lo escrito entre anverso y reverso (si no, las tarjetas escritas quedan como autoevaluación) y que el historial de repaso se conserva al reimportar.

1. ~~Fase 1~~ hecha.
2. Subdecks temáticos, etiquetas y recolocación en `push`.
3. Pista de pronunciación.
4. HSK 3.0 y frecuencia hablada como señales.
5. `stats`: leer fallos de Anki por AnkiConnect y convertir las tarjetas problemáticas en huecos del siguiente lote.


## Fuentes

- [genanki](https://github.com/kerrickstaley/genanki) · [Anki: importar paquetes](https://docs.ankiweb.net/importing/packaged-decks.html) · [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
- [pypinyin](https://github.com/mozillazg/python-pinyin) · [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary)
- [Dong: palabras de películas](https://www.dong-chinese.com/dictionary/topMovieWords), [componentes](https://www.dong-chinese.com/dictionary/topComponents), [orden de caracteres](https://www.dong-chinese.com/dictionary/dongChinese)
- [Azure Speech](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech) · [precios](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/) · [uso del audio según nivel (Q&A)](https://learn.microsoft.com/en-us/answers/questions/5805156/please-clarify-the-conflicting-information-regardi)

Consultadas entre el 25 y el 26 de septiembre de 2026; condiciones y precios se vuelven a comprobar al implementar cada parte.
