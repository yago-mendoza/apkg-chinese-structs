# 3-data

Fuente de verdad del mazo, mantenida por el agente. Un archivo por tema en cada carpeta; el tema de cada elemento es el archivo en que vive (no se escribe dentro). Criterios completos: `docs/design.md`.

| Ruta | Contenido |
|---|---|
| `themes.yaml` | Temas en orden de aprendizaje: `{id, title}`. Deciden los subdecks (`🐉 Chino práctico::HSK n::NN Título`), el orden de las nuevas y el cuaderno (`4-notebook/`). Títulos con coma, entre comillas. `keep: <motivo>` si se decide mantener un tema aunque `check` avise de su tamaño. |
| `lexicon/<tema>.yaml` | `entries`: el diccionario. |
| `sentences/<tema>.yaml` | `sentences`: frases, recursos en sí mismos y ejemplos reutilizables. |
| `exercises/<tema>.yaml` | `exercises`: cada ejercicio es una tarjeta de Anki. Va en el tema de su primer objetivo. |
| `attic.yaml` | `items`: el desván, lo que no entró y espera con su contexto (`docs/design.md`, «Desván»). Cada uno: `id` (`a.<nombre>`), `hanzi`, `pinyin`, `meaning: {es}`, `theme` (dónde iría), `links` (palabras que lo despiertan), `reason` (por qué no entró), `notes: [{text, original?}]`, `source: {batch, file, date}`; `level` y `level_reason` si no está en la lista del HSK; `snooze: <lote>` con `snooze_reason` para aplazarlo en un lote. Sin tarjetas. |
| `theory.yaml` | `terms`: los términos de teoría (pictograma, fonético-semántico, homófonos…), `{id, group, title: {es, en}, text: {es, en}}`. Se exportan al cuaderno web; no generan tarjetas. |
| `hanzi.yaml` | `characters`: por cada hanzi del mazo, `gloss: {es, en}`, `origin: {es, en}` (su porqué, redactado: empieza por «Pictograma:», «Ideograma:», «Ideograma compuesto:» o «Fonético-semántico:»), `traditional` si la forma simplificada esconde el dibujo, `memory: {es, en}` (una imagen para recordarlo desde su forma de hoy, que se rotula «Para recordarlo (no es su origen)»; obligatoria si el origen es discutido o el hanzi se usa solo por su sonido: `check` avisa, `needs_memory`), `confidence: high \| medium`; y solo si la fuente se equivoca, `type`, `phonetic: {char, pinyin}` o `semantic` con `override` (el porqué). `parts`: qué significa cada pieza, `{es, en}`. Se exporta como `characters`; no genera tarjetas. Ver `docs/goal.md`, «Cómo se explica un carácter». |
| `audio/` | MP3 generados por `anki.py audio` e `index.yaml` con su procedencia. No regenerar ni borrar. |

## Entradas (`lexicon/`)

- `id` permanente con prefijo: `w.` palabra, `e.` expresión, `c.` carácter o componente, `p.` pronunciación, `g.` grupo, `st.` estructura. Una entrada por sentido y lectura.
- `kind`: `word | expression | character | component | pronunciation | group | structure`.
- `pos` (palabras): categoría gramatical; se calcula de la lista del HSK y solo se escribe si no está en ella o si el sentido del mazo es otro (entonces con `pos_reason`). Valores: `pronombre | sustantivo | nombre-propio | verbo | adjetivo | adverbio | clasificador | numero | particula | conjuncion | preposicion | interrogativo | interjeccion | expresion`.
- `sense_level` (con su motivo, junto a `level` y `level_reason`): el sentido de la entrada no es el de la lista del HSK (王 apellido frente a 王 «rey»), así que manda su `level`. `accept_cards` (motivo): la entrada pasa el tope de tarjetas por palabra con razón.
- `use`: `read | hear | say` (escalera), o excepción con `use_reason`: lista (`[read]`, `[hear]`…), `context` (solo dentro de frases) o `drop` (descartada).
- `role` (palabras y expresiones): `content | function`.
- `hanzi`, `pinyin`, `meaning: {es, en}`; `standalone: yes | rare | no` (del sentido); `as_word: {es, pinyin?}` en un componente cuyo hanzi también es palabra suelta (口, 女, 月; `check` lo exige si está en la lista del HSK o en el mazo); `real_word: {hanzi?, pinyin?, es}` en todo componente: la palabra que se usa al hablar para ese sentido y por qué (目 → 眼睛); `relations`; `accept_pinyin_mismatch` con motivo si pypinyin discrepa con razón.
- Grupos: `basis: visual | homophone | soundalike | pattern | set | phonetic`, `members: [{ref, cue}]` (cue: rasgo distintivo; máximo 4 en contraste). Diagramas (`docs/design.md`, «Tarjetas»): `timeline: [{ref, from, to}]` (horas de 0 a 24), una franja del día; `scale: [{ref, label}]`, una escala de menos a más (pesos, intensidad, frecuencia); `aspect: [{ref, from, to, label}]` (de -3 a 3, con 0 en el momento en que se habla), un eje de tiempo. Cada elemento sale con su nombre debajo.
- Pronunciación: `title`, `explanation`, `audio_text` y su `audio_pinyin` (el pinyin tal como suena, que el reverso pone junto al ejemplo).
- Estructuras (`lexicon/estructuras.yaml`): `pattern` (`{S} + 很 + {Adj}`; huecos `{S} {N} {V} {Adj} {Num} {Nombre} {Lugar} {Tiempo} {Frase}`), `refs` (las entradas de las piezas fijas, en orden), `examples` (frases que la cumplen), `meaning: {es, en}`, `contrast: {right, wrong, why: {es, en}}` (frase buena del mazo, calco erróneo y porqué: de ahí sale su tarjeta). Sin `level`: es el de su pieza fija más difícil. Ver `docs/design.md`, «Gramática».
- `connection: {kind: sound | meaning | looks, with: [hanzi], text}`: el recuadro de «Conexión» del carácter (uno por entrada; lo heredan las palabras que lo llevan). `with`: caracteres que ya están en el mazo. Ver `docs/goal.md`, «Cómo se explica un carácter».
- `comments: [{kind, private, date, text, original}]` (`text` redactado para mostrar; `original`, lo que escribió YAGO, solo si difiere), con `kind`: `mnemonic | teacher | linguistic | character | note | sound | usage` (`character`: el análisis del carácter, aparte del uso; `usage`: cómo se dice de verdad, «Uso real»). `private: true` por defecto; el repositorio es público, así que lo privado no se guarda aquí.
- `source: {origin, batch, file, date}` (`origin`: `class` o `class-audio`, de clase; `inbox` o `review`, sus apuntes; `attic`, del desván; `gaps`, propuesta del agente por frecuencia); `with_class: <fecha>` si no es de clase pero va muy ligado a esa clase (sale con ella en Anki).

## Frases (`sentences/`)

- `id` con prefijo `s.`; `use: say` (frase modelo, se practica diciéndola) o `hear` (de ejemplo, se practica escuchándola). `kind: formula | example`: fórmula que se usa tal cual en una situación, o ejemplo que enseña una palabra o estructura (`docs/design.md`, «Datos»). `listen: true | false` con `listen_reason` decide a mano la tarjeta de oír.
- `segments: [{text, ref, pinyin, sandhi}]`: cada trozo enlaza a su entrada; `sandhi` si el pinyin escrito es el realizado (不 → bú).
- `translation: {es, en}`; `source`.

## Ejercicios (`exercises/`)

- `id` con prefijo `x.`, permanente: de él depende el progreso en Anki. Si cambia lo que pregunta, ID nuevo.
- `type`: `read | listen | tones | cloze | produce | speak | contrast | derive | components | nuance | pattern | comprehension | charsound | compose` (`charsound`: un hanzi suelto y su sílaba; lo escribe `scaffold`).
- Comprensión lectora (`type: comprehension`, `x.comprehension.`): `targets` son las frases del texto, en orden (al menos 12 hanzi); `script: hanzi` (solo hanzi; el pinyin, al girar) o `both` (pinyin encima), nunca pinyin solo; `question: {es}` o `{sentence: s.…}` (en chino, una frase del mazo); `answer: {meaning}`. Ver `docs/design.md`, «Tarjetas».
- Huecos (`type: cloze`): `sentence` y `gap` (la palabra que se tapa) o `gap_after` (un sitio vacío detrás de esa palabra: la trampa en que no va nada).
- `targets` (lo que se evalúa), `context` (visible en la pregunta), `reveal` (frase fijada a mano para el reverso; sin él, se eligen solas entre las que contienen el objetivo), `refs` (entradas de pronunciación).
- `prompt: {text, hanzi, pinyin, audio, said, said_es}` (`said`: el chino que te dicen en la escena, en su bocadillo; `said_es`, su traducción si no es una frase ni una entrada del mazo); `answer: {typed, accept, hanzi, pinyin, meaning}`. `typed`: pinyin numérico (`ni3 hao3`) o, en tonos, un dígito por sílaba (`'25'`); `accept`: otras respuestas tecleadas que también valen (`['wang4']`). Sin `typed`, autoevaluación. En un matiz, `prompt.no_audio`: los trozos de la consigna que no suenan delante (los calcos que se comparan, como 我是高兴). `same_prompt_ok` (motivo): dos tarjetas comparten anverso con razón (si no, `check` avisa).
- `added`: fecha de creación (etiqueta `mes::` en Anki). No se cambia.
- `accept_pinyin_mismatch` con motivo, como en las entradas, si la respuesta lleva tono neutro o sandhi que pypinyin no da.
- Construir (`type: compose`, `x.compose.`): `prompt: {text}` es la escena; `words` (de 3 a 6 entradas del mazo) el material; `targets`, las frases modelo (al menos dos). Ver `docs/design.md`, «Tarjetas».
- Elegir: cualquier tarjeta puede llevar `prompt.options` (de 2 a 5 textos) y `answer.choice` (la letra de la buena, `a`–`e`).
- Prefijos a mano: `x.situation.` (escena → respuesta en voz alta, `type: speak`; con `sentence` si la respuesta es una frase del mazo), `x.pair.<a>-<b>` (`type: listen`, `pair: [{hanzi, pinyin, meaning}, …]` en el orden en que suenan: oír las dos y decir cuál es cuál) y `x.vowels.` (`type: listen`: oír y completar las vocales). En una tarjeta de decir una frase, `also: [s.…]`: otras frases igual de buenas. Ver `docs/design.md`, «Tarjetas».
