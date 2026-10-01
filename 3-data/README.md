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
| `audio/` | MP3 generados por `anki.py audio` e `index.yaml` con su procedencia. No regenerar ni borrar. |

## Entradas (`lexicon/`)

- `id` permanente con prefijo: `w.` palabra, `e.` expresión, `c.` carácter o componente, `p.` pronunciación, `g.` grupo, `st.` estructura. Una entrada por sentido y lectura.
- `kind`: `word | expression | character | component | pronunciation | group | structure`.
- `pos` (palabras): categoría gramatical; se calcula de la lista del HSK y solo se escribe si no está en ella o si el sentido del mazo es otro (entonces con `pos_reason`). Valores: `pronombre | sustantivo | nombre-propio | verbo | adjetivo | adverbio | clasificador | numero | particula | conjuncion | preposicion | interrogativo | interjeccion | expresion`.
- `use`: `read | hear | say` (escalera), o excepción con `use_reason`: lista (`[read]`, `[hear]`…), `context` (solo dentro de frases) o `drop` (descartada).
- `role` (palabras y expresiones): `content | function`.
- `hanzi`, `pinyin`, `meaning: {es, en}`; `standalone: yes | rare | no` (del sentido); `as_word: {es, pinyin?}` en un componente cuyo hanzi también es palabra suelta (口, 女, 月; `check` lo exige si está en la lista del HSK o en el mazo); `relations`; `accept_pinyin_mismatch` con motivo si pypinyin discrepa con razón.
- Grupos: `basis: visual | homophone | pattern | set`, `members: [{ref, cue}]` (cue: rasgo distintivo; máximo 4 en contraste).
- Pronunciación: `title`, `explanation`, `audio_text`.
- Estructuras (`lexicon/estructuras.yaml`): `pattern` (`{S} + 很 + {Adj}`; huecos `{S} {N} {V} {Adj} {Num} {Nombre} {Lugar}`), `refs` (las entradas de las piezas fijas, en orden), `examples` (frases que la cumplen), `meaning: {es, en}`, `contrast: {right, wrong, why: {es, en}}` (frase buena del mazo, calco erróneo y porqué: de ahí sale su tarjeta). Sin `level`: es el de su pieza fija más difícil. Ver `docs/design.md`, «Gramática».
- `comments: [{kind, private, date, text, original}]` (`text` redactado para mostrar; `original`, lo que escribió YAGO, solo si difiere), con `kind`: `mnemonic | teacher | linguistic | note | sound`. `private: true` por defecto; el repositorio es público, así que lo privado no se guarda aquí.
- `source: {origin, batch, file, date}`.

## Frases (`sentences/`)

- `id` con prefijo `s.`; `use: say` (frase modelo, se practica diciéndola) o `hear` (de ejemplo, se practica escuchándola).
- `segments: [{text, ref, pinyin, sandhi}]`: cada trozo enlaza a su entrada; `sandhi` si el pinyin escrito es el realizado (不 → bú).
- `translation: {es, en}`; `source`.

## Ejercicios (`exercises/`)

- `id` con prefijo `x.`, permanente: de él depende el progreso en Anki. Si cambia lo que pregunta, ID nuevo.
- `type`: `read | listen | tones | cloze | produce | speak | contrast | derive | components | nuance`.
- `targets` (lo que se evalúa), `context` (visible en la pregunta), `reveal` (frase fijada a mano para el reverso; sin él, se eligen solas entre las que contienen el objetivo), `refs` (entradas de pronunciación).
- `prompt: {text, hanzi, pinyin, audio}`; `answer: {typed, hanzi, pinyin, meaning}`. `typed`: pinyin numérico (`ni3 hao3`) o, en tonos, un dígito por sílaba (`'25'`). Sin `typed`, autoevaluación.
- `added`: fecha de creación (etiqueta `mes::` en Anki). No se cambia.
