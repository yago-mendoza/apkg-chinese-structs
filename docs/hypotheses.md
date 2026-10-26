# Hipótesis de aprendizaje

Lo que creemos que ayuda a aprender a quien estudia con este mazo, cómo se comprueba y qué salió. Sirve para no repetir errores y para acumular lo que funciona.

**Qué va aquí y qué no**

- Va: una hipótesis sobre el aprendizaje (qué tarjeta, qué orden o qué forma de explicar le funciona), con fecha, de dónde sale, cómo se mide y su estado. Al cambiar de estado se añade la fecha y la prueba; lo anterior no se reescribe.
- No va: la regla que resulta (vive en `docs/goal.md` o `docs/design.md`, que enlazan aquí), por qué se decidió (`docs/decisions.md`), las fricciones del trabajo del agente (los logs y la retrospectiva) ni cifras sueltas sin una hipótesis detrás.

**Estados**: 🧪 en prueba · ✅ confirmada · ❌ descartada. Cada review trae «¿Funciona?» con las que ya se pueden juzgar; la retrospectiva las cierra (`docs/design.md`, «Retrospectiva»).

## En prueba

### 🧪 Lo de clase primero rinde más que ir nivel a nivel

- **Desde**: lote 011 (2026-10-16). **De dónde**: review 010, «lo que viene de clase debe aparecer lo antes posible, sin importar el HSK».
- **Cómo se mide**: en `anki.py stats`, el porcentaje de «Otra vez» en lo de clase frente al resto, y lo que diga en el review sobre si llega a clase con lo de la semana ya visto.
- **Regla**: `docs/goal.md`, «Qué entra y qué sale primero».
- **Lote 012 (2026-10-19)**: lo de clase sale por dos colas, la reciente (7 de cada 10) y la atrasada (3 de cada 10). Se mide igual, y además si lo de la semana le sale antes de la clase siguiente y si la cola de clase baja.

### 🧪 Menos tarjetas de oír, y más difíciles, no le quitan oído

- **Desde**: lote 011 (2026-10-16). **De dónde**: review 010, «las de oír deben ser desafíos» y «no puede haber tantas».
- **Cómo se mide**: el porcentaje de «Otra vez» en las de oír en las próximas semanas, frente al 24 % general del lote 010, y los ejercicios de escucha de los deberes.
- **Regla**: `docs/goal.md`, «Las de oír, retos».
- **Lote 012 (2026-10-19)**: fuera de lo de clase, las frases que se practican para decir ya no llevan tarjeta de oír (231 menos).

### 🧪 Ver el tono en color le ayuda a recordarlo

- **Desde**: 2026-10-16, entre los lotes 011 y 012. **De dónde**: le cuesta recordar el tono de cada palabra; lo propuso el agente y él lo pidió para todo el mazo.
- **Cómo se mide**: en `anki.py stats`, el «Otra vez» de las tarjetas de tonos y de decir en las próximas semanas, frente al 64 % de «Otra vez» al decir del lote 011, y lo que diga en el review.
- **Regla**: `docs/goal.md`, «Los tonos, también por color».

### 🧪 Construir (palabras y escena, con modelos detrás) enseña a hilar frases

- **Desde**: lote 010 (2026-10-11). **De dónde**: su propuesta en el chat.
- **Cómo se mide**: lo que diga cuando empiecen a salirle y las frases suyas que apunte en «Tus notas».
- **Regla**: `docs/goal.md`, «Cómo se practican las frases».

### 🧪 Contrastar sin rodeos lo que se confunde lo fija

- **Desde**: lote 003 (2026-10-01). **De dónde**: sus apuntes.
- **Cómo se mide**: `stats` sobre los contrastes que más falla. 他 / 她 / 它 sigue fallándose (4 de 7 en el lote 010): si no mejora, pasar a pareja para oír con su frase.
- **Lote 012 (2026-10-19)**: entran cinco parejas que solo separa el tono (还 / 嗨, 鱼 / 雨, 晚 / 完 / 万, 没 / 每, 六 / 留) y los contrastes que pidió (吧 / 呢, 休息 / 学习, 青 / 请, 讠 / 辶, 喝 / 渴, 真的 / 正在).
- **Regla**: `docs/goal.md`, «Lo que se confunde, contrastado sin rodeos».

### 🧪 Sus propias mnemotecnias, en todas partes, le ayudan a recordar

- **Desde**: lote 012 (2026-10-19). **De dónde**: lo pidió en el chat del 16 y en el review 011 («la parte de mnemotecnia debería ser más clara», «en las frases, el bloquecito de cada mnemotecnia»).
- **Cómo se mide**: el «Otra vez» de las palabras con mnemotecnia propia frente a las que no la tienen, y lo que diga en el review.
- **Regla**: `docs/design.md`, «Tarjetas» (reverso).

### 🧪 Un dibujo explica mejor que una nota lo que se reparte en el tiempo

- **Desde**: lote 012 (2026-10-19). **De dónde**: review 011, «¿no podrías currarte mini diagramas que ayuden a entender?», con 早上 y 上午.
- **Cómo se mide**: si deja de confundir 早上 y 上午 en `stats` y lo que diga de la franja.
- **Lote 014 (2026-10-26)**: le gusta el diagrama de 早上 y pide el nombre debajo de cada barra; y que haya diagramas siempre que aclaren algo. Se amplía a escalas (pesos, intensidad, frecuencia) y al eje de tiempo de 要…了, 了, 过, 在 y 已经. Se mide igual: los fallos de 了 / 过 / 要…了 y de los pesos en `stats`, y lo que diga.
- **Regla**: `docs/design.md`, «Tarjetas» (diagramas); `docs/goal.md`, «Diagramas sin cortarse».

### 🧪 Una pregunta por tarjeta: sin anversos iguales, no parece que las tarjetas se repitan

- **Desde**: lote 014 (2026-10-26). **De dónde**: su nota del review 013 («no dejan de repetírseme las mismas aunque les dé +21 d») y la revisión de Anki: no había notas duplicadas, pero sí anversos iguales y muchas tarjetas de una misma sílaba (妈 / 吗 / 马) en días seguidos.
- **Cómo se mide**: si deja de notar repeticiones; que `check` no avise de anversos iguales; y en `stats`, el «Otra vez» de las tarjetas fusionadas frente al de antes.
- **Regla**: `docs/design.md`, «Tarjetas» (una pregunta, una respuesta) y «Anki» (orden de nuevas).

## Confirmadas

### ✅ Cada tarjeta, una sola cosa con respuesta corta

- **Desde**: lote 009 (2026-10-10). Las tarjetas de «¿cuándo cada uno?» con seis opciones y un párrafo detrás no se podían puntuar: las pasaba sin saberlas. Partidas en situaciones y huecos, dejó de pedir que se borraran. **Regla**: `docs/goal.md`, «Una respuesta que se puede puntuar».

### ✅ Oír las dos sílabas en la misma tarjeta, no una sola

- **Desde**: lote 009 (2026-10-10). Con una sola sílaba no tenía con qué comparar y las pasaba con «fácil»; con las dos sonando juntas, sí distingue. **Regla**: `docs/goal.md`, «Oír las dos y elegir».

### ✅ Elegir entre opciones con letra, para lo que se decide por la situación

- **Desde**: lote 010 (2026-10-11). Lo pidió él tras las preguntas de repaso del chat. **Regla**: `docs/goal.md`, «Elegir entre opciones».

## Descartadas

### ❌ La teoría de pronunciación en tarjetas ayuda a pronunciar

- **Del lote 005 al 010**. Las preguntas de regla y las explicaciones de los reversos no le ayudaban: la teoría la estudia en un cuaderno de papel y del mazo solo quiere oír. Se quitaron en el lote 010. **Ver**: `docs/decisions.md`, 2026-10-11.

### ❌ Una tarjeta de oír es un reto si la frase es larga

- **Lote 011, el mismo día**. Sus ejemplos de buenas escuchas (您贵姓？, 他二十二岁。) son cortos: lo que hace buena una escucha es que mezcle vocabulario y no sea una fórmula hecha. **Ver**: `docs/decisions.md`, 2026-10-16.

### ❌ Leer en voz alta con el pinyin delante

- **Del lote 001 al 009**. Ya imita cada audio del mazo; con el pinyin delante no aporta. **Ver**: `docs/decisions.md`, 2026-10-10.
