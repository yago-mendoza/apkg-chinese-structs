# My Anki — chino práctico, pinyin y audio

Documento de diseño y traspaso, 2026-09-25. Fuente: conversación de YAGO con Codex y críticas de Claude aportadas por YAGO. El sistema todavía no está implementado. Este documento reúne las decisiones; las propuestas pendientes se identifican expresamente.

## Propósito y alcance

Aprender mandarín útil para la vida cotidiana desde un nivel inicial —YAGO lleva pocas clases—, con especial atención a leer pinyin, reconocer y producir tonos, escuchar y conversar. Nada de vocabulario literario ni frases raras para rellenar ejercicios. La frecuencia orienta; la utilidad real y las palabras de la profesora también cuentan.

YAGO aporta palabras, frases, dudas y comentarios por chat. El LLM mantiene un diccionario personal estructurado y redacta ejercicios a partir de él. Un programa consulta, comprueba y empaqueta lo guardado. El mismo conocimiento podrá alimentar una sección de diccionario y un mazo descargable en InfraPhysics.

Repositorio de trabajo: https://github.com/yago-mendoza/apkg-chinese-structs, clonado en `C:\Dev\apkg-chinese-structs`, fuera de Google Drive. Este diseño se trasladó desde Atrio con verificación SHA256. La implementación y la generación de audio siguen pendientes.

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

Dos archivos editables, mantenidos principalmente por el LLM:

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

Comandos propuestos, aún no implementados:

```text
python anki.py lookup 喝
python anki.py gaps
python anki.py check
python anki.py audio
python anki.py build
```

`lookup` busca por hanzi, pinyin o significado y devuelve las entradas relacionadas, ejercicios por tipo y papel de cada aparición. El agente debe consultarlo antes de añadir contenido. `gaps` resume cobertura; ambos se calculan desde los archivos, sin un índice manual duplicado.

Para palabras/expresiones activas, objetivo inicial flexible: lectura con recuperación de pinyin, escucha sin texto revelado y producción. Suele requerir aproximadamente tres ejercicios útiles, pero no es una cuota. Componentes y pronunciación tienen criterios propios. Disponer de audio en una respuesta no acredita práctica de escucha; repetir vocabulario en contexto tampoco acredita producción.

Mostrar también práctica específica de tonos, contextos distintos, audio pendiente y palabras de ejemplos aún no registradas. Estar registrado no significa estar aprendido: sin datos de repaso no inferir dominio ni velocidad. No imponer dos apariciones de contexto, porcentajes iguales de tipos ni notas personales obligatorias.

Errores que bloquean la salida final: IDs repetidos, referencias rotas, respuestas obligatorias ausentes o audio requerido faltante. Avisos editoriales: posible redundancia, pinyin discrepante con diccionario, sentido/registro dudoso, contexto demasiado difícil. El LLM revisa el significado de los avisos; no los ignora ni acepta automáticamente.

## Audio, compilación y actualización

Audio reproducible en todas las respuestas y ejemplos chinos. En ejercicios de escucha aparece antes de revelar; en lectura/producción, después, para no regalar la respuesta. Para un componente sin uso hablado independiente, usar su nombre y una palabra de ejemplo. Pronunciación: modelo de audio de la unidad o palabra que ilustra el fenómeno.

Propuesta inicial: ElevenLabs, con voz adecuada de mandarín seleccionada escuchando muestras. Confirmar la lectura en contexto de palabras ambiguas. Diccionarios y pypinyin ayudan a detectar discrepancias; no garantizan el audio ni seleccionan por sí solos el sentido.

Generar audio en un paso separado y conservarlo. Caché por texto, voz, modelo y ajustes relevantes, con nombre prefijado para evitar colisiones en Anki. Registrar procedencia y condiciones de uso. Recompilar no llama al LLM ni vuelve a pagar audios existentes.

Python en entorno virtual local, archivos abiertos con UTF-8 explícito y ejecución UTF-8 en Windows. Recursos previstos: genanki, lector/validador de YAML, API de ElevenLabs; CC-CEDICT y pypinyin como verificadores. Respetar licencias y atribuciones de recursos al exportar.

IDs estables de mazo/modelos/notas y campos/plantillas estables. El GUID de Anki deriva del ID permanente del ejercicio, no del texto mutable. Una corrección conserva identidad; sustituir el objetivo por otro ejercicio requiere identidad nueva. Retirar un ejercicio de la fuente no garantiza eliminarlo de Anki: documentar y probar esa operación aparte.

Desde el piloto: importar, repasar, editar contenido, reimportar y comprobar ausencia de duplicados y conservación del historial. Comprobar audio, pinyin escrito y visualización en el cliente real; no dar por validada una importación por el mero hecho de crear el `.apkg`.

## Frecuencia, dificultad y registro

Conservar separadamente los datos de Dong Chinese: rango de palabra en películas, orden del carácter y número de caracteres que contienen un componente. No mezclarlos en una puntuación. Bandas de frecuencia transparentes —top 500, 1.000, etc.— serían una presentación derivada; un dato ausente sigue desconocido.

Frecuencia no equivale a coloquialidad ni dificultad personal. El filtro editorial es chino cotidiano y práctico. Una necesidad concreta de YAGO puede justificar una palabra menos frecuente. No importar automáticamente todo un ranking.

Las primeras páginas de las tres listas se comprobaron durante el diseño; la extracción completa, paginación y condiciones de reutilización siguen pendientes. Obtener una copia fechada cuando se implemente esta parte, sin hacer de la extracción un requisito para las primeras tarjetas.

## Repositorio, privacidad e InfraPhysics

Repositorio propio creado por YAGO y clonado fuera de Drive en `C:\Dev\apkg-chinese-structs`. Recomendación: mantenerlo privado si va a alojar comentarios privados; no se ha verificado su visibilidad. No introducir comentarios privados ni credenciales antes de resolverlo. Git aporta recuperación del código y contenido; YAGO no necesita mantener un ritual de commits. Git local, alojamiento en GitHub y publicación de resultados son decisiones separadas.

Este diseño es la documentación canónica del proyecto; Atrio conserva una referencia al destino. La copia original se verificó antes de sustituirla por esa referencia.

Propuesta mínima en el nuevo repositorio:

```text
README.md          uso y criterios de este documento, adaptados al sistema real
AGENTS.md          procedimiento breve del agente, sin duplicar el README
lexicon.yaml       conocimiento y comentarios
exercises.yaml     preguntas y vínculos
anki.py            consulta, validación y compilación; dividir cuando haga falta
media/             audio persistente
dist/              salidas generadas
```

Versionar código y YAML. Conservar y respaldar MP3: Git puede servir al principio para una colección pequeña y estable; revisar tamaño y frecuencia de cambios antes de adoptarlo como almacén permanente. Excluir secretos, entorno virtual y compilados. Estar en `.gitignore` no elimina un archivo ya registrado ni protege copias publicadas anteriormente.

Comentarios privados: permanecer en la fuente privada. Exportación pública por lista explícita de campos permitidos, tanto en JSON como en tarjetas/HTML/audio del mazo. Una marca `private` no oculta nada si se publica el archivo fuente. Para el piloto, los comentarios privados quedan fuera de todas las salidas; un eventual mazo personal con ellos sería un modo separado y nunca el publicable.

Salida web futura: `dictionary.json` con versión de esquema, ejemplos y comentarios publicables; MP3 referenciados mediante rutas portables; `.apkg` con esos audios incluidos. La web consume una exportación, no otra copia editable del diccionario. No necesita decidirse ahora su framework.

GitHub Releases es una opción de distribución, no una obligación semanal. IMPORTANTE: las releases de un repositorio privado no son descargas públicas. Para una web pública se necesitan artefactos publicados en un destino público o una importación autenticada desde el servidor/build que sirva solo el resultado permitido. Nunca incluir credenciales en el navegador. Elegir ese destino al implementar la publicación.

GitHub permite enlaces `releases/latest/download/<archivo>` para los assets. Un enlace latest no actualiza por sí solo el diccionario ya compilado en la web. Para builds reproducibles, consumir una versión fijada y actualizarla cuando se publique; el enlace de descarga del mazo puede apuntar a latest en el destino público adecuado.

El plan gratuito de ElevenLabs limita el contenido a uso no comercial y requiere atribución al compartir. La condición afecta también a MP3 empaquetados dentro del `.apkg`. Revisar plan, voz y términos antes de producción masiva destinada a publicar; pagar posteriormente no cambia las condiciones de los audios generados gratis.

## Secuencia de construcción

1. Completado: crear y clonar el repositorio; trasladar este diseño con verificación.
2. Preparar unas cinco entradas cotidianas y un concepto de pronunciación relevante, con pocos ejercicios de lectura, escucha, tonos y producción. Incluir comentarios en sus hogares correctos y audio desde el piloto.
3. Implementar consulta, validación y compilación mínimas; comprobar importación, repaso y reimportación real.
4. Automatizar audio con caché y comparación con diccionarios; ampliar ejercicios según necesidades observadas.
5. Añadir exportación pública y rankings. Publicar e integrar InfraPhysics solo cuando haya contenido listo y un destino decidido.

Antes de producir contenido: concretar con el material de clase simplificado/tradicional, variedad de mandarín y clientes Anki usados. No bloquean este diseño. Visibilidad del repositorio, voz/plan de audio y destino público permanecen pendientes.

## Fuentes de comprobación

- [genanki](https://github.com/kerrickstaley/genanki): generación del paquete e identidades.
- [Anki: importar paquetes](https://docs.ankiweb.net/importing/packaged-decks.html): comportamiento de actualización.
- [pypinyin](https://github.com/mozillazg/python-pinyin): herramienta de contraste de lecturas.
- [Dong: palabras de películas](https://www.dong-chinese.com/dictionary/topMovieWords), [componentes](https://www.dong-chinese.com/dictionary/topComponents), [orden de caracteres](https://www.dong-chinese.com/dictionary/dongChinese).
- [GitHub: enlaces a releases](https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases).
- [ElevenLabs: publicación de contenido](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform).

Las fuentes web se consultaron durante la conversación del 25 de septiembre de 2026; condiciones comerciales y compatibilidad se volverán a comprobar al implementar las partes correspondientes.
