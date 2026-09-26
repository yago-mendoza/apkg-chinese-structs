# Diseño — chino práctico, pinyin y audio

Documento canónico para agentes. Reúne las decisiones; las propuestas pendientes se identifican expresamente. Para YAGO: `README.md`. Fuente: conversaciones de YAGO con Codex y Claude, desde el 2026-09-25.

## Funcionamiento de `anki.py` y de las tarjetas

- `push` usa el complemento AnkiConnect (código `2055492159`, instalado en `%APPDATA%\Anki2\addons21`). Abre Anki si no está abierto (ruta por defecto o `ANKI_EXE`). La sincronización requiere haber iniciado sesión en AnkiWeb una vez desde Anki; `--no-sync` la omite. Comprobado el 2026-09-25: reimportar no duplica notas. Falta comprobar que se conserva el historial después de repasar.

- `audio` necesita `AZURE_SPEECH_KEY` y `AZURE_SPEECH_REGION` como variables de entorno (ver `.env.example`). Voz por defecto `zh-CN-YunyangNeural`, a velocidad -30 % (elegida por YAGO escuchando muestras, 2026-09-26). `audio --dry-run` lista lo pendiente sin llamar a la API. Los MP3 se guardan en `3-data/audio/` con prefijo `acs_` y su procedencia en `3-data/audio/index.yaml`.
- `build` se niega a compilar si falta audio requerido. `build --allow-missing-audio` sirve solo para probar importación y visualización antes de tener audio.
- Tarjetas tecleadas: la respuesta se escribe en pinyin numérico (`he1`, `ni3 hao3`, `5` = neutro) y Anki la compara literalmente. Aceptar también `hē` con diacríticos queda pendiente: la comparación nativa de Anki no normaliza.
- Tarjetas de tonos (`type: tones`): la respuesta es un dígito por sílaba, sin espacios (什么 → `25`, 谢谢 → `45`). Dos variantes: escuchar el audio, o ver el pinyin sin tonos (`shen me`). `check` reconstruye el pinyin con pypinyin y comprueba que los dígitos equivalen a `answer.pinyin`. Útil para neutros y sandhi: 你好 se oye ní hǎo y se responde `33`.
- Tarjetas sin `typed` son de autoevaluación (escucha de comprensión, pronunciación).
- GUID de cada nota = `guid_for("apkg-chinese-structs", id del ejercicio)`; modelos con IDs fijos en `anki.py`. No cambiarlos.
- Mazo `🐉 Chino práctico`, con un subdeck por mes (`🐉 Chino práctico::2026-09`) según `added` de cada ejercicio. Anki deja cada tarjeta en el deck de su primera importación, así que el mes no se reasigna. Estudiar el mazo padre repasa todos los meses juntos.
- Redundancia: `check` avisa si dos ejercicios tienen el mismo tipo y los mismos `targets`. Que una entrada reaparezca como contexto o ejemplo en otro mes es deseable y no cuenta.
- Grupos (`kind: group` en `3-data/lexicon.yaml`): reúnen entradas que conviene estudiar juntas. `basis: visual` (se parecen: 大/太/天), `homophone` (mismo sonido) o `pattern` (misma pieza de formación: 上午/中午/下午, 作者/读者/记者). Cada miembro lleva `cue`: el rasgo que lo distingue o lo que aporta. Máximo 4 en grupos de contraste. Crear un grupo cuando YAGO ya conoce al menos uno de los miembros o los ha confundido, no por adelantado: estudiar a la vez cosas parecidas y desconocidas aumenta la confusión.
- Tarjetas de grupo: `contrast` (una por miembro: el anverso muestra el grupo en orden barajado estable y pregunta por uno) y `derive` (dado un miembro de un patrón, producir otro). El reverso muestra el grupo completo con sus rasgos.
- Varios sentidos de un hanzi: una entrada por sentido y una tarjeta por sentido dentro de una palabra (行 en 银行 → háng). No hacer tarjetas de «enumera todos los significados».
- `standalone: yes | rare | no` indica si **ese sentido** se usa solo como palabra (午 «mediodía»: no; aparece en 上午, 下午). Depende del sentido, no del hanzi: 生 «vida» casi no va solo, 生 «crudo» sí. El reverso lo indica con las palabras registradas que lo contienen; `check` y `gaps` avisan si no hay ninguna.
- Estado (2026-09-26): 108 entradas, 22 frases, 178 ejercicios, 108 audios, todo sacado de los apuntes de YAGO (el contenido inventado del piloto se retiró). Importado y sincronizado con AnkiWeb. Conservación del historial tras repasar, pendiente.
- Comentarios: `note` es un apunte literal de YAGO de origen sin precisar (se muestra como «Apunte»); `teacher` solo si consta que lo dijo la profesora.

## Inbox: entrada por lotes

`1-inbox/*.txt` son apuntes en bruto de YAGO. Son locales y no se suben (`.gitignore`), porque el repositorio es público. Al procesarlos, el agente (Claude Code en la sesión; `anki.py` no llama a ningún LLM):

1. Lee todos los `.txt` pendientes (`gaps` los cuenta). Para cada término: `lookup`, y decide si es nuevo, corrige algo existente o amplía una entrada o grupo.
2. Algo parecido a lo existente (misma forma, mismo sonido, mismo patrón) se añade a esa entrada, a `relations` o a un grupo. No se crean tarjetas sueltas repetidas. Se aplican las reglas de grupos de «Funcionamiento».
3. Guarda los comentarios de YAGO literalmente, en su ámbito. No lleva al YAML lo que parezca privado, sino que pregunta. `source` lleva `origin: inbox`, `batch` (el lote), `file` y la fecha.
4. Equilibra según `gaps`: completa lectura/escucha/producción de lo activo antes de ampliar vocabulario, y no crea ejercicios de relleno.
5. Pregunta lo ambiguo en vez de adivinar (sentido, lectura, si ya lo sabe).
6. Escribe `4-digests/<lote>.md` (formato abajo).
7. `check` sin errores ni avisos pendientes; mueve los `.txt` a `2-raw/<lote>/` (lote = `NNN-AAAA-MM-DD-tema`, numerado por orden de procesado; el mismo nombre que su digest); resume a YAGO lo añadido, lo cambiado y el audio nuevo que se generará.

Digest del lote (`4-digests/`, para YAGO): todo el contenido del lote, no solo lo que entra al mazo, comprimido y agrupado por temas. Una línea por elemento: `汉字 pinyin · significado · pista (relación, mnemotecnia, pronunciación) · ejemplo`. Cada línea lleva una marca:

- ✅ aprender: cotidiano, vivir en China, trabajo, o expresivo para hablar con algo de personalidad.
- 🟡 reconocer: ayuda a leer o a entender; no hace falta producirlo.
- ❌ tachar: literario, arcaico, en desuso o remoto (YAGO lo tacha en sus apuntes).
- 🃏 si está en el mazo, ⚠️ si corrige algo de los apuntes.

Se organiza por temas, sin referencias a números de hoja ni de página de los apuntes. Al final: qué entró al mazo y qué ✅ queda pendiente. El digest es histórico: no se reescribe; lo pendiente se retoma en lotes siguientes.

No hay registro manual de fechas de edición por tarjeta: Git guarda qué cambió y cuándo, y Anki guarda el historial de repaso. `source.date` indica cuándo entró cada entrada.

## Estabilidad de las tarjetas y del audio

Una tarjeta creada se toca poco: su audio queda generado y no conviene regenerarlo sin motivo.

- El audio se guarda por **texto chino exacto** (`3-data/audio/index.yaml`). Editar consigna, significado, explicación o comentarios no lo regenera. Cambiar el hanzi de una respuesta o frase sí pide audio nuevo: hacerlo solo si estaba mal.
- Un mismo texto se sonoriza una vez y se reutiliza en todas las tarjetas.
- El audio de una frase solo vale para esa frase exacta (我是学生。 no sirve para 我是老师。). Preferir pocas frases útiles y estables, reutilizadas como ejemplo en varias tarjetas, antes que variantes casi iguales. Antes de crear una frase, buscar con `lookup` si ya hay una que sirva.
- El ID de ejercicio no cambia nunca, porque de él depende el progreso en Anki. Ampliar un grupo añade tarjetas nuevas y conserva las anteriores.
- Audio por tipo (`wants_audio` en `anki.py`): escucha, tonos y pronunciación lo necesitan; lectura, hueco, producción y deducción lo muestran tras revelar; el contraste visual (大/太/天) y los componentes no llevan, porque se deciden por la forma; el contraste de homófonos sí lleva. Las frases de ejemplo y las entradas de pronunciación siempre llevan.

## Propósito y alcance

Aprender mandarín útil para la vida cotidiana desde un nivel inicial —YAGO lleva pocas clases—, con especial atención a leer pinyin, reconocer y producir tonos, escuchar y conversar. Nada de vocabulario literario ni frases raras para rellenar ejercicios. La frecuencia orienta; la utilidad real y las palabras de la profesora también cuentan.

YAGO aporta palabras, frases, dudas y comentarios por chat. El LLM mantiene un diccionario personal estructurado y redacta ejercicios a partir de él. Un programa consulta, comprueba y empaqueta lo guardado. El mismo conocimiento podrá alimentar una sección de diccionario y un mazo descargable en InfraPhysics.

Decisión vigente de YAGO (2026-09-25, sustituye a la de trabajar en Codespaces): el proyecto vive en este ordenador, fuera de Atrio, en `C:\Users\yagom\dev\apkg-chinese-structs`, con Python en un entorno virtual propio. Repositorio: https://github.com/yago-mendoza/apkg-chinese-structs. La generación de audio y la publicación siguen pendientes.

## Dónde vive cada nota

Evitar usar «nota» para tres cosas diferentes: una entrada del diccionario guarda conocimiento; un ejercicio plantea una pregunta; una nota de Anki es un registro técnico que produce tarjetas.

| El comentario trata sobre… | Hogar canónico | Cuándo se muestra |
|---|---|---|
| Una palabra, un sentido o un carácter: «esto me recuerda a…» | La entrada correspondiente en `lexicon.yaml` | En las respuestas que evalúen esa entrada |
| Un sonido, un tono o una regla general de pronunciación | Una entrada de pronunciación en el mismo `lexicon.yaml` | En ejercicios vinculados a esa dificultad |
| Una frase concreta, su pronunciación o una situación | El ejemplo/frase guardado en `exercises.yaml` | Junto a esa frase |
| Un truco para resolver una pregunta particular | El ejercicio correspondiente | Solo en su respuesta |

Una observación general sobre cómo pronunciar una sílaba no debe quedar enterrada en una palabra accidental. Se guarda una vez y se referencia. No crear un tercer archivo para pronunciación: es otro tipo de entrada del diccionario. No mostrar todos los comentarios en todas las tarjetas: primero la solución, después explicación breve y comentarios pertinentes.

Preservar literalmente los comentarios personales. Separar mnemotecnia subjetiva, observación de la profesora y explicación lingüística verificada. Una imagen mental útil no se presenta automáticamente como etimología. Los componentes, radicales y pictogramas tampoco son sinónimos.

## Pinyin y tonos: parte central del diseño

- Pinyin visible y legible en las soluciones; nunca retirarlo globalmente para «avanzar». En el anverso se muestra u oculta según qué se pregunte.
- Practicar por separado reconocer el símbolo de un tono, distinguirlo al oído y producirlo. Saber el significado no acredita esas habilidades.
- Empezar con palabras cotidianas cortas y sílabas conocidas; pasar a combinaciones de dos sílabas y frases breves. Precisión antes de rapidez, sin cronómetro obligatorio.
- Ejercicios específicos: escuchar y elegir/escribir el tono; completar los tonos de un pinyin ya dado; leer pinyin en voz alta antes de escuchar; distinguir dos audios; escribir pinyin completo desde hanzi o audio.
- Son variantes del repertorio, no nuevas infraestructuras. Cada ejercicio declara exactamente qué evalúa: lectura, escucha, producción y, cuando corresponda, discriminación de tonos o pronunciación.
- Incluir tono neutro y pronunciación contextual gradualmente. Distinguir la escritura de referencia del pinyin de una explicación de cómo se realiza en una frase; no alterar silenciosamente la respuesta para reflejar cambios fonéticos.
- Propuesta de entrada: aceptar tanto `he1` como `hē`, normalizando sin perder los tonos. Aceptar una respuesta sin tono solo cuando la consigna no lo evalúe. Verificar esta interacción en los clientes Anki usados por YAGO.
- Anki permite comparar una respuesta escrita, pero las traducciones abiertas admiten alternativas y la pronunciación oral requiere autoevaluación al escuchar el modelo. No prometer corrección automática del habla.
- Usar colores para alinear partes de hanzi/pinyin/traducción. No reutilizar simultáneamente esos mismos colores con otro significado para los tonos. Sus marcas deben seguir siendo claras sin depender del color.

## Contenido y ejercicios

Dos archivos en `3-data/`, mantenidos por el agente:

| Archivo | Contenido |
|---|---|
| `lexicon.yaml` | ID permanente; tipo —palabra, expresión, carácter, componente o pronunciación—; escritura, lectura y sentido cuando proceda; registro; fuente y fecha; comentarios; relaciones; referencias de frecuencia |
| `exercises.yaml` | ID permanente; tipo de pregunta; objetivo y capacidades evaluadas; consigna; respuesta y alternativas; frase segmentada, pinyin y traducción; explicación; comentarios particulares; referencias de audio |

No usar solo el hanzi como ID: una escritura puede tener distintos sentidos y lecturas. Las correcciones conservan el ID. Las entradas de pronunciación o componentes no necesitan fingir que son palabras independientes.

Cada ejercicio distingue objetivos evaluados, vocabulario de contexto en la pregunta y vocabulario que solo aparece al revelar ejemplos. Segmentar las frases con referencias a las entradas para alinear colores y contar apariciones. No deducir cobertura solo buscando subcadenas: un carácter dentro de una palabra no equivale a evaluar su significado aislado.

Las frases reutilizadas se guardan una sola vez y se referencian; no hace falta un archivo independiente de ejemplos al empezar. Idioma de apoyo español o inglés, indicado en cada ejercicio; evitar alternancias arbitrarias dentro de una misma explicación.

### Repertorio acordado

1. Hanzi → escribir pinyin y recordar significado.
2. Completar una frase con pinyin.
3. Escuchar → reconocer, transcribir pinyin o responder una pregunta de comprensión.
4. Chino → significado en español o inglés.
5. Intención/español/inglés → producir chino, principalmente en pinyin.
6. Reconocer componentes y caracteres, vinculados a ejemplos útiles.
7. Contrastar usos, sonidos, tonos o palabras que se confunden.
8. Pinyin → significado sin depender del hanzi.
9. Construir, ordenar o corregir una frase.
10. Pronunciar en voz alta y comparar con audio.

Diez tipos de pregunta no implican diez tarjetas por palabra ni diez plantillas técnicas. Compartir presentación y usar comportamientos específicos solo cuando hagan falta. Primer piloto: lectura con pinyin, escucha y producción con hueco, incorporando práctica explícita de tonos. Añadir las demás modalidades conforme el contenido las justifique.

Una pregunta concreta por tarjeta. No convertir todos sus ejemplos y explicaciones en objetivos adicionales. Contextos cotidianos: pedir, responder, comprar, comer, desplazarse, presentarse y hablar con gente. Los componentes se estudian como apoyo a palabras útiles, no como un catálogo histórico obligatorio.

## Consulta y salud del mazo

`lookup` busca por hanzi, pinyin o significado y devuelve las entradas relacionadas, ejercicios por tipo y papel de cada aparición. El agente debe consultarlo antes de añadir contenido. `gaps` resume cobertura; ambos se calculan desde los archivos, sin un índice manual duplicado.

Para palabras/expresiones activas, objetivo inicial flexible: lectura con recuperación de pinyin, escucha sin texto revelado y producción. Suele requerir aproximadamente tres ejercicios útiles, pero no es una cuota. Componentes y pronunciación tienen criterios propios. Disponer de audio en una respuesta no acredita práctica de escucha; repetir vocabulario en contexto tampoco acredita producción.

Mostrar también práctica específica de tonos, contextos distintos, audio pendiente y palabras de ejemplos aún no registradas. Estar registrado no significa estar aprendido: sin datos de repaso no inferir dominio ni velocidad. No imponer dos apariciones de contexto, porcentajes iguales de tipos ni notas personales obligatorias.

Errores que bloquean la salida final: IDs repetidos, referencias rotas, respuestas obligatorias ausentes o audio requerido faltante. Avisos editoriales: posible redundancia, pinyin discrepante con diccionario, sentido/registro dudoso, contexto demasiado difícil. El LLM revisa el significado de los avisos; no los ignora ni acepta automáticamente.

## Audio, compilación y actualización

Audio reproducible en las respuestas y ejemplos chinos, salvo los tipos que se deciden por la forma (ver «Estabilidad de las tarjetas y del audio»). En ejercicios de escucha aparece antes de revelar; en lectura/producción, después, para no regalar la respuesta. Para un componente sin uso hablado independiente, usar su nombre y una palabra de ejemplo. Pronunciación: modelo de audio de la unidad o palabra que ilustra el fenómeno.

Decisión de YAGO (2026-09-25): Azure Speech, voces neuronales nativas `zh-CN`, nivel gratuito F0. Se eligió frente a ElevenLabs por la precisión de tonos, el nivel gratuito y la posibilidad de fijar la lectura en pinyin con SSML (`<phoneme alphabet="sapi">`) si un audio lee mal un polífono; implementarlo cuando haga falta. Confirmar la lectura en contexto de palabras ambiguas. Diccionarios y pypinyin ayudan a detectar discrepancias; no garantizan el audio ni seleccionan por sí solos el sentido.

Generar audio en un paso separado y conservarlo. Caché por texto, voz, modelo y ajustes relevantes, con nombre prefijado para evitar colisiones en Anki. Registrar procedencia y condiciones de uso. Recompilar no llama al LLM ni vuelve a pagar audios existentes.

Python en el entorno virtual `.venv` del proyecto; archivos abiertos con UTF-8 explícito. Dependencias fijadas en `requirements.txt`: genanki, PyYAML y pypinyin. Azure Speech se llama por HTTP (REST) sin SDK. CC-CEDICT sigue pendiente como segundo verificador. Respetar licencias y atribuciones de recursos al exportar.

IDs estables de mazo/modelos/notas y campos/plantillas estables. El GUID de Anki deriva del ID permanente del ejercicio, no del texto mutable. Una corrección conserva identidad; sustituir el objetivo por otro ejercicio requiere identidad nueva. Retirar un ejercicio de la fuente no garantiza eliminarlo de Anki: documentar y probar esa operación aparte.

Desde el piloto: importar, repasar, editar contenido, reimportar y comprobar ausencia de duplicados y conservación del historial. Comprobar audio, pinyin escrito y visualización en el cliente real; no dar por validada una importación por el mero hecho de crear el `.apkg`.

## Frecuencia, dificultad y registro

Conservar separadamente los datos de Dong Chinese: rango de palabra en películas, orden del carácter y número de caracteres que contienen un componente. No mezclarlos en una puntuación. Bandas de frecuencia transparentes —top 500, 1.000, etc.— serían una presentación derivada; un dato ausente sigue desconocido.

Frecuencia no equivale a coloquialidad ni dificultad personal. El filtro editorial es chino cotidiano y práctico. Una necesidad concreta de YAGO puede justificar una palabra menos frecuente. No importar automáticamente todo un ranking.

Las primeras páginas de las tres listas se comprobaron durante el diseño; la extracción completa, paginación y condiciones de reutilización siguen pendientes. Obtener una copia fechada cuando se implemente esta parte, sin hacer de la extracción un requisito para las primeras tarjetas.

## Repositorio, privacidad e InfraPhysics

Repositorio propio creado por YAGO: `yago-mendoza/apkg-chinese-structs`, trabajado en local en `C:\Users\yagom\dev\apkg-chinese-structs`. Visibilidad comprobada el 2026-09-25: **público**. Mientras lo sea, no introducir comentarios privados en `3-data/` ni credenciales; hacerlo privado o decidir otra ubicación antes. Git aporta recuperación del código y contenido; YAGO no necesita mantener un ritual de commits. Git local, alojamiento en GitHub y publicación de resultados son decisiones separadas.

Este documento es el diseño vigente; Atrio conserva solo una nota breve que señala este repositorio (`🐉/my_anki/README.md`).

Estructura de carpetas y convenciones de nombres: `README.md`. Versionar código, YAML y MP3 (`3-data/audio/`): Git puede servir al principio para una colección pequeña y estable; revisar tamaño y frecuencia de cambios antes de adoptarlo como almacén permanente. Excluir secretos, entorno virtual y compilados. Estar en `.gitignore` no elimina un archivo ya registrado ni protege copias publicadas anteriormente.

Comentarios privados: permanecer en la fuente privada. Exportación pública por lista explícita de campos permitidos, tanto en JSON como en tarjetas/HTML/audio del mazo. Una marca `private` no oculta nada si se publica el archivo fuente. Para el piloto, los comentarios privados quedan fuera de todas las salidas; un eventual mazo personal con ellos sería un modo separado y nunca el publicable.

Salida web futura, en `5-output/`: `dictionary.json` con versión de esquema, ejemplos y comentarios publicables; MP3 referenciados mediante rutas portables; `.apkg` con esos audios incluidos. La web consume una exportación, no otra copia editable del diccionario. No necesita decidirse ahora su framework.

GitHub Releases es una opción de distribución, no una obligación semanal. IMPORTANTE: las releases de un repositorio privado no son descargas públicas. Para una web pública se necesitan artefactos publicados en un destino público o una importación autenticada desde el servidor/build que sirva solo el resultado permitido. Nunca incluir credenciales en el navegador. Elegir ese destino al implementar la publicación.

GitHub permite enlaces `releases/latest/download/<archivo>` para los assets. Un enlace latest no actualiza por sí solo el diccionario ya compilado en la web. Para builds reproducibles, consumir una versión fijada y actualizarla cuando se publique; el enlace de descarga del mazo puede apuntar a latest en el destino público adecuado.

Audio de Azure Speech: revisar los términos de Microsoft sobre distribución de audio sintético antes de publicar el mazo.

## Secuencia de construcción

1. ~~Trasladar el diseño al repositorio.~~ Hecho en local el 2026-09-25.
2. Preparar unas cinco entradas cotidianas y un concepto de pronunciación relevante, con pocos ejercicios de lectura, escucha, tonos y producción. Hecho, con audio.
3. Implementar consulta, validación, compilación e importación (`push`). Hecho; falta comprobar el historial tras repasar.
4. Audio con caché (Azure). Hecho. Pendiente: comparación con diccionarios; ampliar ejercicios desde `1-inbox/`.
5. Añadir exportación pública y rankings. Publicar e integrar InfraPhysics solo cuando haya contenido listo y un destino decidido.

Antes de producir contenido: concretar con el material de clase simplificado/tradicional, variedad de mandarín y clientes Anki usados. No bloquean este diseño. Visibilidad del repositorio y destino público permanecen pendientes.

## Fuentes de comprobación

- [genanki](https://github.com/kerrickstaley/genanki): generación del paquete e identidades.
- [Anki: importar paquetes](https://docs.ankiweb.net/importing/packaged-decks.html): comportamiento de actualización.
- [pypinyin](https://github.com/mozillazg/python-pinyin): herramienta de contraste de lecturas.
- [Dong: palabras de películas](https://www.dong-chinese.com/dictionary/topMovieWords), [componentes](https://www.dong-chinese.com/dictionary/topComponents), [orden de caracteres](https://www.dong-chinese.com/dictionary/dongChinese).
- [GitHub: enlaces a releases](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases).
- [Azure Speech: texto a voz](https://learn.microsoft.com/azure/ai-services/speech-service/text-to-speech).

Las fuentes web se consultaron durante la conversación del 25 de septiembre de 2026; condiciones comerciales y compatibilidad se volverán a comprobar al implementar las partes correspondientes.

## Siguiente paso

1. Procesar los primeros apuntes de YAGO desde `1-inbox/` y simplificar este documento con lo aprendido.
2. Iniciar sesión en AnkiWeb desde Anki para que `push` sincronice.
3. Repasar unos días, editar un ejercicio, recompilar, reimportar y comprobar que no hay duplicados y se conserva el historial.
4. Decidir la visibilidad del repositorio antes de guardar comentarios privados.

No elegir una licencia de publicación automáticamente. LICENSE sigue siendo una decisión pendiente si se publica código/contenido con permisos de reutilización.

### Instrucción de arranque para el siguiente agente

> Lee `AGENTS.md` y este documento completo. Trabajamos en local en `C:\Users\yagom\dev\apkg-chinese-structs`, con `.venv`. Conserva chino cotidiano, pinyin y tonos como prioridades. Antes de añadir contenido, ejecuta `lookup` y `gaps`; después, `check`. No empieces por rankings, publicaciones o una arquitectura extensa. Distingue lo comprobado automáticamente de lo que requiere probarse en el cliente Anki.
