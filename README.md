# Chino práctico — mazo de Anki

Un sistema para convertir apuntes de clase de mandarín en un mazo de Anki con pinyin, tonos, audio y pronunciación. Dejas tus apuntes en bruto; un agente de código (LLM) los convierte en tarjetas siguiendo una especificación; `anki.py` comprueba el resultado, genera el audio y lo mete en Anki.

El repositorio trae como ejemplo real el mazo de Yago Mendoza, construido con sus apuntes. Se puede usar tal cual o vaciar para trabajar con los tuyos.

## TL;DR

Solo haces dos cosas: dejar apuntes en `1-inbox/` y, cuando te apetezca, decirle al agente «procesa el inbox». Él los convierte en tarjetas, genera el audio y las mete en Anki. Estudias en Anki. Ya está. (Anki tiene que estar abierto cuando el agente sube las tarjetas; si estudias en el móvil, sincronizas y listo.)

**`1-inbox/`: donde escribes.** Apuntes tal como salen: notas del móvil, fotos pasadas a texto, listas a medias, dudas. Sin formato. Lo único que ayuda es poner la fecha en que apuntaste cada cosa. Aquí te deja también el agente el review del último lote: lo que le falta al mazo, lo que no entró y por qué, lo que conviene comprobar. Escribes debajo de cada punto lo que quieras y entra en el siguiente lote.

**`1-inbox/history/`: el historial del inbox.** Al procesar un lote, el agente archiva ahí todo lo que pasó por el inbox, tal cual, en una carpeta por lote: tus apuntes y el review que contestaste. No se lee ni se edita; sirve para volver al original.

**`2-digests/`: el log de cada lote.** El acta de lo que hizo el agente: qué entró, qué no y por qué, qué corrigió de tus apuntes y qué reorganizó. No se edita; es la memoria del sistema. Lo que admite tu opinión no está aquí, está en el review.

**Lotes.** Un lote es lo que haya en el inbox cuando pides procesarlo; la frecuencia la eliges tú. Lotes cortos te devuelven el review antes. Lotes grandes dejan ver más material junto al decidir temas y grupos. Todavía está por ver qué funciona mejor: si muchos lotes pequeños fijan una organización que luego no encaja, o si mucho texto de golpe organiza mejor. Por eso la estructura no se congela: en cada lote el agente revisa temas y grupos y reorganiza si hace falta, sin perder tu progreso.

**`3-data/`: la base de datos.** Todo lo que sabe el mazo, un archivo por tema: el léxico (palabras, expresiones, caracteres, reglas de pronunciación y grupos de cosas que se confunden), las frases, las tarjetas, la lista de temas y el audio generado. Solo la edita el agente.

**`4-notebook/`: la misma base, para leer.** Todo lo aprendido, por temas, con pinyin, significado, frases y notas. Es lo que abres para repasar o buscar algo sin Anki. Se regenera sola.

**`5-output/`: lo que sale.** El mazo compilado (`.apkg`) y el diccionario público (`dictionary.json`), que es lo que muestra infraphysics.net/corner/chinese.

**Por qué no se desincroniza nada.** `3-data/` es la única fuente: el cuaderno, el mazo y el diccionario se generan de ella, así que no pueden contradecirse. Antes de que un cambio llegue a Anki, `anki.py check` lo valida (formato, pinyin, IDs, tarjetas que faltan o sobran, audio). Al cerrar un lote se regenera todo, se hace commit y se etiqueta el lote: cualquier estado anterior se puede recuperar.

## Lo que no tienes que vigilar

- **Tarjetas repetidas o redundantes.** `check` detecta las que piden lo mismo y el agente las fusiona.
- **Palabras sueltas que nunca usas.** Toda palabra que quieres saber decir tiene que aparecer en alguna frase; si no hay ninguna, el review te la pide.
- **Errores en tus apuntes.** El agente corrige glosas y lecturas mal copiadas, lo marca ⚠️ en el log y te pregunta lo dudoso en el review.
- **Temas mal elegidos.** Se reorganizan en cualquier lote. Cada tarjeta tiene un ID fijo, así que moverla o corregirla no borra su historial en Anki.
- **Cuántas tarjetas hacer y de qué tipo.** Lo calcula `anki.py` según para qué quieres cada palabra (leerla, entenderla al oírla o decirla).
- **El audio.** Se genera solo para lo que falta y se guarda; no se paga dos veces.
- **Tus otros mazos de Anki.** El sistema solo toca el suyo.
- **Corregir cosas dentro de Anki.** No hace falta, y se perdería: díselo al agente y lo arregla en la fuente.
- **Qué estudiar hoy.** El mazo padre, que ya mezcla lo nuevo y lo viejo en orden.

## Aprendizaje activo, no solo tarjetas generadas

Generar tarjetas es la parte fácil. Lo que hace útil este sistema es que el agente no solo produce: **devuelve trabajo al que aprende** y cierra el ciclo.

- **Deberes después de cada lote.** El agente deja en `1-inbox/` un `review-<lote>.md`: lo que falta (palabras que quieres decir y aún no aparecen en ninguna frase), lo que no entró y por qué, y lo que conviene comprobar en el cuaderno. Debajo de cada punto hay una línea `>` para escribir libremente; vuelve como entrada del siguiente lote. El agente pide frases reales en vez de inventarlas.
- **Filtrar, no acumular.** Lo que no entra se explica: 🟡 solo para reconocer, ❌ literario, arcaico o en desuso, para tacharlo en los apuntes a mano. Las glosas mal leídas se corrigen con ⚠️. Si un matiz te interesa, puede volver como tarjeta de matiz.
- **Entender lo que apuntaste.** Cada lote deja un log en `2-digests/`: qué entró, qué no y por qué, correcciones y reorganizaciones. Lo que admite tu opinión (incluidos los matices de lo que sí entró) está en el review.
- **Recordar, no releer.** Las tarjetas piden producir: escribir el pinyin o los hanzi, marcar los tonos con dígitos, decir frases en voz alta y compararlas con el audio. Cada palabra tiene las tarjetas que exige para qué la necesitas (leer, entender al oír, decir).
- **Contraste y contexto.** Las palabras que se confunden (他/她/它, 生/牛/午) o que forman serie (上午/中午/下午/晚上) aparecen juntas al dar la vuelta, y las palabras que quieres decir tienen que aparecer en frases.
- **Pronunciación explícita.** Transcripción fonética, trampas del pinyin para hispanohablantes y reglas de sandhi en las tarjetas donde toca pronunciar o reconocer de oído.
- **Reglas que no dependen del modelo.** Qué tarjetas faltan, qué sobra y qué falta por practicar lo calcula `anki.py` a partir de una especificación (`docs/design.md`). El modelo redacta; el código comprueba. Un modelo mejor mejora el mazo sin cambiar el sistema.

## Uso

1. Deja tus apuntes en bruto en `1-inbox/`: cualquier archivo, sin formato. Pon la fecha de lo apuntado, al principio o en cada parte si mezclas días.
2. Abre un agente de código en la carpeta y pídele «procesa el inbox». Edita el mazo, regenera el cuaderno, deja el log del lote en `2-digests/` y te deja en `1-inbox/` el `review`, para que escribas debajo de cada punto.
3. Pide que lo suba a Anki (con Anki abierto), o hazlo tú:

```powershell
.\.venv\Scripts\python anki.py audio   # genera solo el audio que falta (Azure Speech)
.\.venv\Scripts\python anki.py push    # compila, abre Anki, importa, ajusta límites y orden, y sincroniza
```

No corrijas nada dentro de Anki: cada `push` sobrescribe las tarjetas con lo que hay en `3-data/`. Las correcciones se piden al agente.

## Cómo estudiar

- Estudia el mazo padre (**🐉 Chino práctico**): mezcla lo nuevo y lo antiguo de todos los temas.
- Colores de Anki: 🔵 nuevas · 🟠 aprendiendo (vuelven a los pocos minutos) · 🟢 repasos (lo aprendido otro día que toca recordar). «¡Felicidades!» es que no queda nada por hoy.
- Ritmo: `push` fija las nuevas y los repasos máximos al día (`NEW_PER_DAY` y `REVIEWS_PER_DAY` en `anki.py`). Los repasos se estabilizan en unas 5–8 veces las nuevas: con 30 nuevas, unos 200 repasos, unos 40 minutos.
- Respuestas escritas: pinyin con tildes o con números (`ni3 hao3`) o hanzi con un teclado chino; espacios, mayúsculas y puntuación dan igual. En las frases para decir en voz alta, escribir es opcional.
- Al dar la vuelta: pinyin, transcripción fonética [AFI], audio, trampas de pronunciación y la familia de la palabra si la tiene (la palabra de la tarjeta, marcada ▸).
- `4-notebook/` reúne todo lo aprendido por temas; `2-digests/`, el log de cada lote.
- En Anki, un subdeck por tema; el mes, el tema y el `use` también van como etiquetas, para sesiones filtradas.

## Usarlo con tus propios apuntes

1. Copia el repositorio (fork o clon).
2. Vacía el contenido y conserva la estructura:
   - `1-inbox/history/`, `2-digests/`, `4-notebook/`, `3-data/audio/` y el review de `1-inbox/`: borra su contenido (deja los `README.md`; `4-notebook/` se regenera sola).
   - `3-data/lexicon/`, `3-data/sentences/` y `3-data/exercises/`: borra los archivos.
   - `3-data/themes.yaml`: ajusta los temas a tu gusto.
3. En `anki.py`, cambia `DECK_NAME` y `GUID_NAMESPACE` si en tu Anki ya tienes este mazo, para que no se mezclen.
4. Adapta a ti la sección «Objetivo» de `docs/design.md` (nivel, idioma de apoyo, para qué estudias) y sustituye `docs/owner.md` por tus propias notas. Las trampas fonéticas están pensadas para hispanohablantes.
5. Configura Azure Speech y Anki (ver «Configuración») y deja tu primer lote en `1-inbox/`.
6. Pide a tu agente «procesa el inbox». `AGENTS.md` y `docs/design.md` le dicen todo lo que necesita.

## Qué más hay

- `AGENTS.md`: reglas para cualquier agente; lo primero que lee.
- `docs/design.md`: la especificación completa (cobertura, tipos de tarjeta, audio, decisiones).
- `docs/owner.md`: la configuración y las decisiones del dueño de este mazo.
- `anki.py`: consulta, validación, cobertura, audio, compilación e importación. No llama a ningún LLM.
- `sources/`: listas externas de consulta (hoy, el vocabulario del HSK 3.0), cada una con su origen y su licencia.

## Listas de frecuencia y HSK

El agente decide qué entra y cuánto se practica sobre todo por tus apuntes y tus necesidades. Dos tipos de lista externa sirven de señal, nunca de fuente: la frecuencia hablada (palabras más usadas en subtítulos de películas, de Dong Chinese) dice qué es núcleo y qué es raro, y los niveles del HSK 3.0 (lista de `drkameleon/complete-hsk-vocabulary`, MIT) sirven para ver huecos y saber en qué nivel estás. No se importa ninguna lista entera: una palabra solo entra cuando aparece en tus apuntes o cuando el review te la propone y la aceptas.

Estado: la lista del HSK 3.0 ya está en `sources/hsk/` (con su licencia), pero `anki.py` aún no la usa (fase 4 de `docs/design.md`). La de Dong Chinese no se descarga: su web pide que no la rastreen programas.

## Convenciones

- Carpetas y archivos en inglés, en minúsculas, con guiones. Las carpetas del flujo llevan el número de su paso: `1-inbox` (con su historial en `history/`) → `2-digests` → `3-data` → `4-notebook` → `5-output`. Lo que no es flujo (`docs/`, `anki.py`) va sin número.
- Toda documentación de carpeta se llama `README.md`; las reglas para agentes, `AGENTS.md`. Contenido y documentación en español.
- Lotes: `NNN-AAAA-MM-DD-tema` (número de orden de procesado, fecha de procesado y tema en palabras: `001-2026-09-25-primeras-clases`). Dentro, cada apunte lleva como prefijo la fecha en que se apuntó (`2026-10-03_notas-bus.txt`, o `mixto_…` si mezcla días); lo pone el agente al archivar. Ese nombre lo comparten la carpeta `1-inbox/history/<lote>/`, el log `2-digests/summary-<lote>.md` y el review `review-<lote>.md`. Nunca números de hoja: log y review se organizan por temas.
- IDs del diccionario y de los ejercicios con prefijo de tipo: `w.` palabra, `e.` expresión, `c.` carácter, `p.` pronunciación, `g.` grupo, `s.` frase, `x.` ejercicio. Nunca cambian.

## Configuración (una vez)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

- Audio: un recurso Azure AI Speech en nivel de pago (S0; céntimos por lote) y `AZURE_SPEECH_KEY` y `AZURE_SPEECH_REGION` como variables de entorno (ver `.env.example`). El nivel gratuito sirve para uso propio, pero su audio no se puede distribuir.
- Anki desktop con el complemento AnkiConnect (`2055492159`) y sesión iniciada en AnkiWeb para sincronizar con el móvil.

Otros comandos, sobre todo para el agente: `anki.py lookup <término>`, `plan` (qué tarjetas faltan), `scaffold` (las escribe con formato estándar), `gaps` (reparto del mazo), `check`, `notebook`, `build`, `close-batch <lote>` (archiva el lote, commit y etiqueta), `export` (el diccionario público `5-output/dictionary.json`, que usa infraphysics.net/corner/chinese). Pruebas: `.\.venv\Scripts\python -m unittest discover -s tests`. Opciones de `push`: `--prune` borra del mazo las tarjetas cuyo ejercicio ya no existe (antes las lista; si son muchas, exige además `--force`); `--reset` devuelve todo el mazo a nuevas, sin progreso (para fases de pruebas).

**El audio es sintético**, generado con Azure AI Speech (voz `zh-CN-YunyangNeural`).

## Licencia y cita

- **Código** (`anki.py`): [MIT](LICENSE).
- **Contenido** (apuntes, datos, digests, cuaderno, audio y documentación): [CC BY 4.0](LICENSE-CONTENT). Se puede usar para cualquier fin, también comercial, **citando al autor**.

Forma de citar: *Yago Mendoza, «apkg-chinese-structs», https://github.com/yago-mendoza/apkg-chinese-structs, CC BY 4.0.*
