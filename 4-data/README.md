# 4-data

Fuente de verdad del mazo, mantenida por el agente. Un archivo por tema en cada carpeta; el tema de cada elemento es el archivo en que vive (no se escribe dentro). Criterios completos: `docs/design.md`.

| Ruta | Contenido |
|---|---|
| `themes.yaml` | Temas en orden de aprendizaje: `{id, title}`. Deciden los subdecks (`🐉 Chino práctico::NN Título`), el orden de las nuevas y `5-guide/`. Títulos con coma, entre comillas. `keep: <motivo>` si se decide mantener un tema aunque `check` avise de su tamaño. |
| `lexicon/<tema>.yaml` | `entries`: el diccionario. |
| `sentences/<tema>.yaml` | `sentences`: frases, recursos en sí mismos y ejemplos reutilizables. |
| `exercises/<tema>.yaml` | `exercises`: cada ejercicio es una tarjeta de Anki. Va en el tema de su primer objetivo. |
| `audio/` | MP3 generados por `anki.py audio` e `index.yaml` con su procedencia. No regenerar ni borrar. |

## Entradas (`lexicon/`)

- `id` permanente con prefijo: `w.` palabra, `e.` expresión, `c.` carácter o componente, `p.` pronunciación, `g.` grupo. Una entrada por sentido y lectura.
- `kind`: `word | expression | character | component | pronunciation | group`.
- `use`: `read | hear | say` (escalera), o excepción con `use_reason`: lista (`[read]`, `[hear]`…), `context` (solo dentro de frases) o `drop` (descartada).
- `role` (palabras y expresiones): `content | function`.
- `hanzi`, `pinyin`, `meaning: {es, en}`; `standalone: yes | rare | no` (del sentido); `relations`; `accept_pinyin_mismatch` con motivo si pypinyin discrepa con razón.
- Grupos: `basis: visual | homophone | pattern | set`, `members: [{ref, cue}]` (cue: rasgo distintivo; máximo 4 en contraste).
- Pronunciación: `title`, `explanation`, `audio_text`.
- `comments: [{kind, private, date, text}]`, con `kind`: `mnemonic | teacher | linguistic | note | sound`. `private: true` por defecto; el repositorio es público, así que lo privado no se guarda aquí.
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
