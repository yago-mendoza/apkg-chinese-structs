# Chino práctico — mazo de Anki

Un sistema para convertir apuntes de clase de mandarín en un mazo de Anki con pinyin, tonos, audio y pronunciación. Dejas tus apuntes en bruto; un agente de código (LLM) los convierte en tarjetas siguiendo una especificación; `anki.py` comprueba el resultado, genera el audio y lo mete en Anki.

El repositorio trae como ejemplo real el mazo de Yago Mendoza, construido con sus apuntes. Se puede usar tal cual o vaciar para trabajar con los tuyos.

## Aprendizaje activo, no solo tarjetas generadas

Generar tarjetas es la parte fácil. Lo que hace útil este sistema es que el agente no solo produce: **devuelve trabajo al que aprende** y cierra el ciclo.

- **Deberes después de cada lote.** El agente deja en `1-inbox/` un `review-<lote>.md`: lo que falta (palabras que quieres decir y aún no aparecen en ninguna frase), lo que no entró y por qué, y lo que conviene comprobar en el cuaderno. Debajo de cada punto hay una línea `>` para escribir libremente; vuelve como entrada del siguiente lote. El agente pide frases reales en vez de inventarlas.
- **Filtrar, no acumular.** Lo que no entra se explica: 🟡 solo para reconocer, ❌ literario, arcaico o en desuso, para tacharlo en los apuntes a mano. Las glosas mal leídas se corrigen con ⚠️. Si un matiz te interesa, puede volver como tarjeta de matiz.
- **Entender lo que apuntaste.** Junto al review, un `summary-<lote>.md` cuenta qué entró al mazo y lo que conviene entender de tus apuntes: relaciones, mnemotecnias, correcciones.
- **Recordar, no releer.** Las tarjetas piden producir: escribir el pinyin o los hanzi, marcar los tonos con dígitos, decir frases en voz alta y compararlas con el audio. Cada palabra tiene las tarjetas que exige para qué la necesitas (leer, entender al oír, decir).
- **Contraste y contexto.** Las palabras que se confunden (他/她/它, 生/牛/午) o que forman serie (上午/中午/下午/晚上) aparecen juntas al dar la vuelta, y las palabras que quieres decir tienen que aparecer en frases.
- **Pronunciación explícita.** Transcripción fonética, trampas del pinyin para hispanohablantes y reglas de sandhi en las tarjetas donde toca pronunciar o reconocer de oído.
- **Reglas que no dependen del modelo.** Qué tarjetas faltan, qué sobra y qué falta por practicar lo calcula `anki.py` a partir de una especificación (`docs/design.md`). El modelo redacta; el código comprueba. Un modelo mejor mejora el mazo sin cambiar el sistema.

## Uso

1. Deja tus apuntes en bruto en `1-inbox/`: cualquier archivo, sin formato. Pon la fecha de lo apuntado, al principio o en cada parte si mezclas días.
2. Abre un agente de código en la carpeta y pídele «procesa el inbox». Edita el mazo, regenera la guía y te deja en `1-inbox/` el `summary` (qué entró) y el `review` (qué falta y qué no entró, para que escribas debajo de cada punto).
3. Sube el mazo a Anki:

```powershell
.\.venv\Scripts\python anki.py audio   # genera solo el audio que falta (Azure Speech)
.\.venv\Scripts\python anki.py push    # compila, abre Anki, importa, ajusta límites y orden, y sincroniza
```

No corrijas nada dentro de Anki: cada `push` sobrescribe las tarjetas con lo que hay en `4-data/`. Las correcciones se piden al agente.

## Cómo estudiar

- Estudia el mazo padre (**🐉 Chino práctico**): mezcla lo nuevo y lo antiguo de todos los temas.
- Colores de Anki: 🔵 nuevas · 🟠 aprendiendo (vuelven a los pocos minutos) · 🟢 repasos (lo aprendido otro día que toca recordar). «¡Felicidades!» es que no queda nada por hoy.
- Ritmo: `push` fija las nuevas y los repasos máximos al día (`NEW_PER_DAY` y `REVIEWS_PER_DAY` en `anki.py`). Los repasos se estabilizan en unas 5–8 veces las nuevas: con 30 nuevas, unos 200 repasos, unos 40 minutos.
- Respuestas escritas: pinyin con tildes o con números (`ni3 hao3`) o hanzi con un teclado chino; espacios, mayúsculas y puntuación dan igual. En las frases para decir en voz alta, escribir es opcional.
- Al dar la vuelta: pinyin, transcripción fonética [AFI], audio, trampas de pronunciación y la familia de la palabra si la tiene (la palabra de la tarjeta, marcada ▸).
- `5-guide/` reúne todo lo aprendido por temas; `3-digests/`, los summaries de lotes anteriores.
- En Anki, un subdeck por tema; el mes, el tema y el `use` también van como etiquetas, para sesiones filtradas.

## Usarlo con tus propios apuntes

1. Copia el repositorio (fork o clon).
2. Vacía el contenido y conserva la estructura:
   - `2-raw/`, `3-digests/`, `5-guide/`, `4-data/audio/` y el summary y el review de `1-inbox/`: borra su contenido (deja los `README.md`; `5-guide/` se regenera sola).
   - `4-data/lexicon/`, `4-data/sentences/` y `4-data/exercises/`: borra los archivos.
   - `4-data/themes.yaml`: ajusta los temas a tu gusto.
3. En `anki.py`, cambia `DECK_NAME` y `GUID_NAMESPACE` si en tu Anki ya tienes este mazo, para que no se mezclen.
4. Adapta a ti la sección «Objetivo» de `docs/design.md` (nivel, idioma de apoyo, para qué estudias) y sustituye `docs/owner.md` por tus propias notas. Las trampas fonéticas están pensadas para hispanohablantes.
5. Configura Azure Speech y Anki (ver «Configuración») y deja tu primer lote en `1-inbox/`.
6. Pide a tu agente «procesa el inbox». `AGENTS.md` y `docs/design.md` le dicen todo lo que necesita.

## Qué hay en cada sitio

| Ruta | Qué es |
|---|---|
| `1-inbox/` | Apuntes en bruto pendientes (no se versionan) y lo que deja el agente tras cada lote: `summary-<lote>.md` (qué entró) y `review-<lote>.md` (qué falta y qué no entró; editable). |
| `2-raw/` | Apuntes ya procesados, tal cual, en una carpeta por lote. |
| `3-digests/` | Los summaries de lotes anteriores: histórico. No se edita. |
| `4-data/` | Fuente de verdad del mazo, mantenida por el agente, un archivo por tema: `lexicon/` (diccionario), `sentences/` (frases), `exercises/` (tarjetas), `themes.yaml` (temas y orden) y `audio/`. Esquema en su `README.md`. |
| `5-guide/` | Todo lo aprendido, un archivo por tema, generado desde `4-data/`. No se edita. |
| `6-output/` | Lo que se genera (`chino-practico.apkg`). No se versiona. |
| `AGENTS.md` | Reglas para cualquier agente. Lo primero que lee. |
| `docs/design.md` | Especificación completa: cobertura, tipos de tarjeta, audio, decisiones. |
| `docs/owner.md` | Notas del dueño de este mazo: su configuración y sus decisiones. |
| `anki.py` | Consulta, validación, cobertura, audio, compilación e importación. No llama a ningún LLM. |

## Convenciones

- Carpetas y archivos en inglés, en minúsculas, con guiones. Las carpetas del flujo llevan el número de su paso: `1-inbox` → `2-raw` → `3-digests` → `4-data` → `5-guide` → `6-output`. Lo que no es flujo (`docs/`, `anki.py`) va sin número.
- Toda documentación de carpeta se llama `README.md`; las reglas para agentes, `AGENTS.md`. Contenido y documentación en español.
- Lotes: `NNN-AAAA-MM-DD-tema` (número de orden de procesado, fecha de procesado y tema en palabras: `001-2026-09-25-primeras-clases`). Dentro, cada apunte lleva como prefijo la fecha en que se apuntó (`2026-10-03_notas-bus.txt`, o `mixto_…` si mezcla días); lo pone el agente al archivar. Ese nombre lo comparten la carpeta `2-raw/<lote>/` y el digest `3-digests/<lote>.md`. Nunca números de hoja: el digest se organiza por temas.
- IDs del diccionario y de los ejercicios con prefijo de tipo: `w.` palabra, `e.` expresión, `c.` carácter, `p.` pronunciación, `g.` grupo, `s.` frase, `x.` ejercicio. Nunca cambian.

## Configuración (una vez)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

- Audio: un recurso Azure AI Speech en nivel de pago (S0; céntimos por lote) y `AZURE_SPEECH_KEY` y `AZURE_SPEECH_REGION` como variables de entorno (ver `.env.example`). El nivel gratuito sirve para uso propio, pero su audio no se puede distribuir.
- Anki desktop con el complemento AnkiConnect (`2055492159`) y sesión iniciada en AnkiWeb para sincronizar con el móvil.

Otros comandos, sobre todo para el agente: `anki.py lookup <término>`, `plan` (qué tarjetas faltan), `gaps` (reparto del mazo), `check`, `guide`, `build`. Opciones de `push`: `--prune` borra del mazo las tarjetas cuyo ejercicio ya no existe (antes las lista; si son muchas, exige además `--force`); `--reset` devuelve todo el mazo a nuevas, sin progreso (para fases de pruebas).

**El audio es sintético**, generado con Azure AI Speech (voz `zh-CN-YunyangNeural`).

## Licencia y cita

- **Código** (`anki.py`): [MIT](LICENSE).
- **Contenido** (apuntes, datos, digests, guía, audio y documentación): [CC BY 4.0](LICENSE-CONTENT). Se puede usar para cualquier fin, también comercial, **citando al autor**.

Forma de citar: *Yago Mendoza, «apkg-chinese-structs», https://github.com/yago-mendoza/apkg-chinese-structs, CC BY 4.0.*
