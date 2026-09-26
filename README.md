# Chino práctico — mazo de Anki

Mazo personal de mandarín cotidiano: pinyin, tonos y audio. YAGO aporta apuntes; un agente (LLM) los convierte en tarjetas; `anki.py` las comprueba, genera el audio y las mete en Anki.

## Uso diario

1. Dejar apuntes en bruto en `1-inbox/`: un `.txt` por lote, sin formato.
2. Pedir al agente «procesa el inbox». Edita el mazo, escribe un resumen del lote en `4-digests/` y dice qué ha cambiado.
3. Subir a Anki:

```powershell
.\.venv\Scripts\python anki.py audio   # genera solo el audio que falta (Azure Speech)
.\.venv\Scripts\python anki.py push    # compila, abre Anki, importa, ajusta límites y orden, y sincroniza
```

No se corrige nada dentro de Anki: cada `push` sobrescribe las tarjetas con lo que hay en `3-data/`. Las correcciones se dicen al agente.

## Cómo estudiar

- Pulsar el mazo padre **🐉 Chino práctico**: mezcla lo nuevo y lo antiguo de todos los temas.
- Colores de Anki: 🔵 nuevas (hoy, como mucho 30) · 🟠 aprendiendo (vuelven a los pocos minutos) · 🟢 repasos (lo aprendido otro día que toca recordar). «¡Felicidades!» es que no queda nada por hoy.
- Ritmo: 30 nuevas y 300 repasos como máximo al día. Los repasos se estabilizan en unas 5–8 veces las nuevas: con 30, unos 200 al día, unos 40 minutos. Lo fija `push`; para cambiarlo, pedirlo al agente.
- Respuestas escritas: pinyin con tildes o con números (`ni3 hao3`) o hanzi con el teclado chino; espacios, mayúsculas y puntuación dan igual. En las frases para decir en voz alta, escribir es opcional.
- Al dar la vuelta: pinyin, transcripción fonética [AFI], audio, trampas de pronunciación y la familia de la palabra si la tiene (la palabra de la tarjeta, marcada ▸).
- Tras cada lote, `1-inbox/gaps-<lote>.md` dice qué falta (por ejemplo, frases para palabras que quieres decir). Se edita ahí mismo y entra en el siguiente lote.
- `5-guide/` reúne todo lo aprendido por temas; `4-digests/`, lo que aportó cada lote y qué tachar de los apuntes.

## Qué hay en cada sitio

| Ruta | Para quién | Qué es |
|---|---|---|
| `1-inbox/` | YAGO escribe, el agente lee | Apuntes en bruto pendientes de procesar, y `gaps-<lote>.md`: lo que falta tras el último lote, editable. |
| `2-raw/` | Archivo | Apuntes ya procesados, tal cual, en una carpeta por lote (`2-raw/001-2026-09-25-primeras-clases/`). No se suben a GitHub. |
| `3-data/` | Agente mantiene | Fuente de verdad del mazo. |
| `3-data/lexicon.yaml` | Agente | Diccionario: palabras, caracteres, pronunciación, grupos. |
| `3-data/exercises.yaml` | Agente | Frases y ejercicios (cada ejercicio es una tarjeta). |
| `3-data/audio/` | `anki.py` | MP3 generados e `index.yaml` con su procedencia. No regenerar ni borrar. |
| `4-digests/` | YAGO lee | Un resumen por lote: todo lo de los apuntes, comprimido y clasificado en ✅ aprender, 🟡 reconocer y ❌ tachar. No se edita. |
| `5-guide/` | YAGO lee | Todo lo aprendido, un archivo por tema, generado desde `3-data/` en cada lote. No se edita. |
| `6-output/` | YAGO saca | Lo que se genera: `chino-practico.apkg` y, en el futuro, la exportación para InfraPhysics. Se regenera; no editar. |
| `README.md` | YAGO | Esta página: uso y mapa del repositorio. |
| `AGENTS.md` | Agente | Reglas de trabajo. Lo primero que lee cualquier agente. |
| `docs/design.md` | Agente | Diseño canónico: criterios, tipos de tarjeta, decisiones. |
| `anki.py` | Herramienta | Consulta, validación, audio, compilación e importación. No llama a ningún LLM. |
| `.env.example` | Referencia | Variables de entorno necesarias (sin valores). |

## Convenciones

- Carpetas y archivos en inglés, en minúsculas, con guiones: `3-data/`, `docs/design.md`.
- Las carpetas del flujo llevan el número de su paso: `1-inbox` → `2-raw` → `3-data` → `4-digests` → `5-guide` → `6-output`. Lo que no es flujo (`docs/`, `anki.py`) va sin número.
- Toda documentación de carpeta se llama `README.md`; las reglas para agentes, `AGENTS.md`.
- Contenido y documentación en español.
- Lotes: `NNN-AAAA-MM-DD-tema` (número de orden de procesado, fecha y tema en palabras: `001-2026-09-25-primeras-clases`). Ese nombre lo comparten la carpeta `2-raw/<lote>/` y el digest `4-digests/<lote>.md`. Nunca números de hoja, ni en el nombre ni en el contenido: el digest se organiza por temas.
- Apuntes del inbox: `AAAA-MM-DD-tema.txt` (por ejemplo, `2026-09-25-clase-1.txt`); cualquier nombre sirve.
- IDs del diccionario y ejercicios con prefijo de tipo: `w.` palabra, `e.` expresión, `c.` carácter, `p.` pronunciación, `g.` grupo, `s.` frase, `x.` ejercicio. Nunca cambian.

## Configuración (una vez)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

- Audio: `AZURE_SPEECH_KEY` y `AZURE_SPEECH_REGION` como variables de entorno del usuario (ver `.env.example`).
- Anki desktop con el complemento AnkiConnect (`2055492159`) y sesión iniciada en AnkiWeb para sincronizar.

Otros comandos, sobre todo para el agente: `anki.py lookup <término>`, `plan` (qué tarjetas faltan), `gaps` (reparto del mazo), `check`, `guide`, `build`.
