<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 016-2026-11-06-improvisar-y-la-clase-del-6

**Origen.**
- **Tus respuestas al review 015**: todas las líneas «>» en blanco. Lo que el review dejaba dicho «salvo que digas que no» entra: las 20 de HSK 1 por frecuencia.
- **«Tus notas» del review 015**: unas 1.450 líneas. Lo nuevo: 地方 / 放, 纯正 / 地道, 好的 / 是的, 一下 / 一定 / 一点, animales por piezas, 进来 / 进去 / 出来 / 出去, tus frases corregidas por el asistente, 没问题 / 好问题, dos chuletas para improvisar y una de small talk, y lo que añadiste después de la clase (家, 回 / 来, 都怪你, 听不见 / 不听, 住 / 住在, 请稍等 / 等一下, 外面 / 面, los colores, y las tarjetas que señalabas por su código). Un bloque largo (las tablas de caracteres parecidos, 票, 门 / 们, 犬, 叟, la clase del 29 de septiembre) es una copia de tus notas del lote 002: ya está en el mazo y no se vuelve a meter.
- **La clase del 6 de noviembre**: la hoja en PDF que te dio la profesora (lectura en voz alta, 看词说句, preguntas sencillas, 跟读, 3+3 变调, dos diálogos guiados y los deberes), transcrita por el agente en tus notas, y tus apuntes de debajo (你能听懂我说的吗, 周末愉快, 多大年纪, 真年轻, 他现在在美国).
- **Mantenimiento y retrospectiva**: tocaba, cada cuatro lotes.

En cifras: 282 tarjetas nuevas y ninguna retirada (3975 en total); 57 entradas (40 palabras, 3 expresiones, 3 caracteres, 10 grupos y 1 estructura) y 91 frases.

## Cambios en el sistema

- **En un contraste, cada opción con su frase** (#912EZ, tu nota: «ejemplos acordes, no de una sola»): en la tarjeta de contraste de 进 / 近 / 今 / 斤 solo 进 traía frase. Ahora, en su propia tarjeta de contraste, cada opción lleva una frase en su fila; si es una pieza que no se usa sola (今, 近), una de una palabra que la lleva (今年, 最近). Nunca de un nivel superior ni con la respuesta dentro. Vive en `docs/design.md` («Integración de lo nuevo», «Garantías»), `anki.py` (`member_examples`) y `docs/decisions.md` (2026-11-06).
- **`lookup` con varias búsquedas a la vez** (`anki.py lookup 来到 行 #912EZ`): cargar el mazo es lo lento, y era la fricción que más se repetía en la retrospectiva.
- **El registro de estudio vuelve a llegar a la web**: al mover el proyecto a `dev/Cockpit`, `anki.py` buscaba la web en una carpeta que ya no existía y no mandaba tu registro (`stats` lo avisó). Ahora la encuentra donde está.
- **La hipótesis del tono en color, confirmada** (ver «Retrospectiva»).
- Pruebas nuevas en `tests/` (`Lot016`).

## Material de clase

- **La clase del 6** (hoja de la profesora, en PDF): 
  - **Leer en voz alta**: 我是工程师 (marcó 是 shì frente a 师 shī, con los cuatro tonos), 我不喝茶, 你明天去北京吗？, 这个多少钱？. Entran 你明天去北京吗？ y la pareja para oír 师 shī / 是 shì; lo demás ya estaba.
  - **看词说句**, resuelto: 我明天去医院。, 我不喝咖啡。 (le faltaba el verbo: 喝), 你跟我一起去吗？. Entran las tres; 医院 sube a decir.
  - **Preguntas sencillas**: 你每天几点起床？ (la más marcada), 你喜欢吃什么？, 你学中文多久了？ entran; 你叫什么名字？ y 你是哪国人？ ya estaban. Entra 起床 y una respuesta modelo, 我每天七点起床。.
  - **跟读**: 明天我不去公司，我在家工作。, para decir y para oír.
  - **3+3 变调**: 你好, 很好, 可以, 水果 ya tienen su tarjeta de tonos. La regla no va a las tarjetas (la estudias en tu cuaderno); en el mazo, solo oír.
  - **Diálogos guiados**: dos tarjetas de construir con su escena (presentarte el primer día de trabajo; proponer un plan a un amigo, con 去, 明天, 一起 y 不), con tres modelos cada una. De lo que escribió la profesora: 室友 (compañero de piso) y 那你太惨了！ entran para decir; 游泳 sube a decir; 三十三 ya se dice.
  - **Deberes**: 老板 entra para decir (así se llama al dueño de una tienda), con 老板好！; 广场 y 雨伞, para oír; 一起走, en 我们一起走吧。. 了解 (HSK 4) y 舞蹈 (HSK 6, registro culto: se dice 跳舞) van al desván: salieron solo para leer en voz alta. El shadowing con la grabación no se puede preparar sin la grabación.
- **Tus apuntes de debajo**, que parecen de la misma clase (⚠️ en «Por verificar»): 你能听懂我说的吗？ y 周末愉快！ (expresión) entran; 他现在在美国。 entra y 美国 sube a decir; 多大年纪, 您高寿 y 你真年轻！ ya estaban.
- La hoja no está aún en la carpeta de materiales: falta saber de qué profesora es (ver «Sine qua non»).

## Tus respuestas al review 015

- **El recuadro 💡** y **哦 / 得 děi**: sin respuesta. Se quedan como estaban; el 💡 vuelve a preguntarse.
- **Las 20 de HSK 1 por frecuencia**: entran (ver «Palabras y frases nuevas»).
- **Los colores para decir**: sin respuesta, pero en tus notas pides «una tarjeta con todos los colores, con el 色 una sola vez al final»: entran 红色, 黑色 y 颜色 (este, para decir: 你喜欢什么颜色？), y los cuatro colores forman un grupo que sale junto en cada tarjeta de color: «红 hóng, 白 bái, 黑 hēi, 绿 lǜ, y luego 色». Los colores siguen siendo para oír, así que 灰色 vuelve a esperar.

## Tus notas, en sus tarjetas

Antes de crear cada cosa, se buscó en el mazo:

- **Ya existían, y te digo dónde**: las tarjetas de leer 喜欢 (#HP3Q3) y 见面 (#DFT3B); 你真年轻！; 你的家 en 中国是一个很大的国家 y 你是哪个国家的人？; 或者 / 还是 (su matiz); 怎么说呢 y 让我想一下; 真的吗 y 太好了.
- **地方 / 放**: «place» en inglés son dos cosas; va como 💡 en 地方.
- **好的 / 是的** («más ejemplos»): dos de elegir nuevas (te proponen quedar a las siete: 好的; te preguntan si el móvil es tuyo: 是的) y un 💡 en 是的.
- **一下 / 一定 / 一点** («NECESITO CARD DE CONTRASTE»): tres huecos «¿一下, 一定 o 一点?», uno por uso, y un 💡; tu frase 我一下就看到一点 no es natural y no entra. Tu imagen del dispensador de jabón, como mnemotecnia de 一点.
- **进来 / 进去 / 出来 / 出去** («CARD»): un matiz y el grupo 出来 / 出去 crece a los cuatro.
- **Animales por piezas**: 熊猫 lleva su nota (oso + gato); 长颈鹿, 袋鼠, 河马 y 火鸡, al desván con su composición.
- **纯正 / 地道 / 纯血**: 地道 (HSK 7) al desván, con la nota de los tres; 纯血 suena racial y no se usa para la nacionalidad.
- **Tus frases corregidas**: entran 对，我还在学习中文。, 对，但是我还不太会说中文。, 我很想去中国，但是我没有钱。, 我还没买机票。, 我有朋友，但是他们不在这里。 (con un 💡 de 在 / 还: tú escribiste 不还), 我觉得不是。 y 我常常说中文，感觉很好。 (感觉 entra; 尝尝 «probar» suena casi igual: nota en 常常).
- **没问题 / 好问题**: un matiz, 好问题！ para decir y un 💡 en 问题 («pregunta» y «problema»).
- **Para improvisar** («cosas avanzadas… en el fondo»): entran como lo demás que no es de clase, después de lo de clase. 是吗 (expresión), 我也是！, 然后呢？, 我先回家，然后去超市。, 你觉得呢？, 我不知道怎么说。, 比如 (我喜欢中国的食物，比如牛肉。), 因为 + 也 y 但是 + 我觉得 en dos frases y en una de construir («¿por qué estudias chino?»), 还有什么？, 你经常去吗？, 可能是这样。, el diálogo 你周末做什么了？没做什么，在家休息。, 行吗？, 好不好？, 都行。, y tu respuesta improvisada entera como monólogo para oír. 让我想想 no: ya está 让我想一下.
- **恭喜 / 喜欢 / 公斤**: tu frase 恭喜你买到了两公斤你喜欢的苹果！, para oír, y el grupo de los tres gōng (工, 公, 恭), que solo separa la palabra en que salen.
- **#YJJ2T**: un matiz 我听不见 / 我不听; y 我看不到你。 para decir.
- **#QARKP**: la frase 我自己来 pedía «Ya lo hago yo», donde 自己 sobra; ahora pide «Ya lo hago yo solo (no hace falta que me ayudes)», que es lo que añade 自己.
- **#ZC8HA**: 你 entre paréntesis, (你)要我帮你吗？, y 要不要我帮你？ como otra forma de decirlo (y para oír). **#44CPS**: su reverso dice ahora las formas cortas.
- **#AXB56 y 住**: un 💡 en 住 (住 + tiempo, 住在 + sitio) con 我住三天。 y 我在北京住两天。; el diálogo de la recepción no cambia (426房间 se entiende; 426号房间 es más corriente).
- **请稍等 / 等一下吧**: un matiz y 等一下吧，他马上来。.
- **外面 / 外国** («¿constan como cards lo bastante independientes?»): sí, cada una tiene las suyas (decir 外面 #YCRSS, decir 外国 #CHSF5); y lo de 面 («pensaba que era cara»), como nota en 外面 y en 见面. Entra 外语.
- **家 y sus palabras**: una nota en 家 (大家, 国家, 回家, 家人, 家里); entran 家人 (你的家人都好吗？, 我爱我的家人。), 你家在哪里？ (tu 哪儿 pasa a 哪里: solo mandarín estándar) y 大家都喜欢喝茶。.
- **回 / 来** («Me debe quedar claro este contraste !!!!»): un matiz 你什么时候回家？ / 你什么时候回来？, la estructura 回 + sitio con su calco (你什么时候回来西班牙？ ✗), 我想回西班牙。 y un 💡 en 回.
- **都怪你 / 这都是你的错**: 这都是你的错。 entra (HSK 1); 怪 (HSK 4), al desván con la nota de reproche. 我知道原因。 y 原因 entran (el 因 de 因为).
- **人多**: 周末人很多。 para decir; 平日 (nivel 7) no.
- **商场 / 超市**: un matiz.
- **找** («mnemotecnia importante»): la tuya, el 我 roto.
- **巾 en 帮 y 帅**: tu imagen (el país que se une y cada uno aporta un paño) como mnemotecnia de 帮, y una nota de cómo está hecho: 邦 da el sonido; al hablar, «país» es 国家.
- **还是 «todavía»**: 他还是住在北京。 (oír) y 他住在北京还是上海？ (decir), con un matiz.
- **一起** (我们一起去吧 es lo que más fallas al decir: 7 de 10): un 💡 de dónde va 一起.
- **给** (4 de 4): 我给你打电话。.
- **#9JDK4** («prefiero 我想学多一点中文»): se oye, sobre todo en el sur, y se entiende; lo de siempre es 多学一点. Va como nota en su estructura; la tarjeta no cambia.

## Palabras y frases nuevas

- **HSK 1 por frecuencia**: 着 (oír), 地 (oír), 行, 得到 (oír), 男人, 女人, 身上, 干, 动, 重, 飞, 她们, 来到 (oír), 差, 家里, 记, 病人 (oír), 课, con 上课 y 下课 (oír); 正在 sube a decir. 起 entra con 起床: suelto casi no se usa.
- **De clase**: 起床, 室友, 惨, 老板, 广场 (oír), 雨伞 (oír), 周末, 周末愉快, 那 «entonces» (solo dentro de 那你太惨了); suben a decir 医院, 游泳 y 美国.
- **De tus notas**: 家人, 原因, 感觉, 然后, 比如, 经常, 可能, 外语, 颜色, 红色 (oír), 黑色 (oír), 对了, 是吗, 上海.
- **Grupos**: los tres de (的 / 地 / 得), los tres gōng (工 / 公 / 恭), los colores, y los que solo separa el tono: 姓 / 行, 懂 / 动, 重 / 钟, 茶 / 差, 这 / 着; 他们 / 她们; 克, 课, 渴 y 棵; 记 entra en 几 / 鸡; 进来 y 进去 entran en 出来 / 出去.
- **Estructura**: 回 + sitio.
- **Tarjetas que creé por mi cuenta**: 7 matices, 2 de elegir, 3 huecos de 一下 / 一定 / 一点, 1 pareja para oír (师 / 是), 18 contrastes, 3 de construir, 1 estructura con su calco y un monólogo y un diálogo para oír.
- **HSK 1**: 384 de 506 (75,9 %).

## Del desván

- Nada despierta. **灰色** vuelve a esperar: llegaron 红色, 黑色 y el grupo de los colores, pero los colores siguen siendo para oír.

## No entró, y por qué

- **Al desván**: 地道 (HSK 7), 了解 (HSK 4) y 舞蹈 (HSK 6; se dice 跳舞), 怪 (HSK 4), y 长颈鹿, 袋鼠, 河马, 火鸡 (fuera de la lista; sin frase).
- **Fuera**: 纯血 (racial), 平日 (nivel 7, escrito), 我一下就看到一点 (no es natural), 让我想想 (ya está 让我想一下), y las frases de la chuleta que repetían otras del mazo (我觉得中文很难, 我想明年去中国, 我每天都学习中文, 今天有点忙…).
- **El bloque copiado del lote 002**: ya procesado entonces.

## Reorganización

- **Tres temas pasaban de 60 entradas** (Describir 68, Momentos del día 64, Cosas y actividades 64):
  - **Tema nuevo, «Colores»**: 颜色, 红色, 白色, 黑色, 绿色 y su grupo.
  - A **Lugares**: 回家, 回到, 进来, 进去, 出来, 出去 y su grupo (moverse).
  - A **Personas**: 病人 y 身上. A **Entender**: 感觉. A **Estructuras**: 地, 着 y el grupo de los tres de. A **Números**: 差 (la hora). A **Casa**: 起床. A **Ocio**: 周末.
  - Ninguno pasa ya del tope; las tarjetas cambian de subdeck sin perder su progreso.

## Repaso de calidad

`anki.py audit` sobre el mazo entero:
- **51 parejas de frases casi iguales** (40 en el lote 015): parejas buscadas, como antes (sí / no, con y sin 了, 我有 / 我没有…). Ninguna es una tarjeta repetida.
- **8 grupos de tarjetas del mismo tipo y objetivo**: matices distintos de una misma palabra (我还不懂 / 我还是不懂 frente a 他今年还是学生; 明白 / 懂 frente a 听不懂 / 不明白; 也 / 都 frente a 都 / 什么都; la posición de 了 frente al 了 de cambio) y situaciones frente a sus tarjetas de elegir. Ninguno se ve igual delante; se quedan.
- **Un nivel a mano** de algo de la lista: 户, como en el lote 015.
- **Otras formas que suenan igual**: ninguna.

## Retrospectiva

**Hipótesis** (`docs/hypotheses.md`):
- **Ver el tono en color**: ✅ confirmada. Las tarjetas de tonos fallan un 9 % (4 de 46; 34 % en el lote 014, 44 % en el 013), y decir, un 16 % (64 % en el lote 011).
- **Las demás siguen en prueba**, con su dato de este lote: oír falla un 6 % (21 de 336); los contrastes, un 5 % (4 de 87); construir, 0 de 18 y sin comentario tuyo; 上午 sigue en 4 de 18; nadie ha vuelto a notar tarjetas repetidas; y lo de clase primero no se puede medir aún con `stats`, que no separa lo de clase.

**Fricciones de los lotes 013 a 016** (`anki.py retro`): lo que más se repite es (1) `lookup` uno a uno, lento (arreglado: varias búsquedas, una carga); (2) los scripts de escritura de datos que rompen el YAML o los finales de línea; (3) las pruebas, de más de 20 minutos. Del (2), este lote suma dos casos nuevos (ver abajo). No propongo cambiar reglas: lo de (2) es cuidado del agente, y las pruebas, de momento, se dejan correr en segundo plano mientras se escribe.

## Fricciones del proceso

- **El registro de estudio no llegaba a la web**: el proyecto se movió a `dev/Cockpit` y `anki.py` buscaba la web al lado. `stats` lo avisó; arreglado.
- **El constructor del lote** escribió dos comentarios detrás de unos campos que van después de `comments` (en 一点): el YAML no cargaba. Y los hanzi nuevos cayeron en la sección `parts` de `hanzi.yaml`, al final del archivo, en vez de en `characters`. Los dos se arreglaron a mano antes del primer `check`.
- **Choques de ID**: 行 y 课 iban a usar `w.xing` y `w.ke`, que ya eran 姓 y 棵. Se vio antes de escribir.
- **Dos frases eran iguales a su expresión** (是吗 y 周末愉快): habrían dado dos tarjetas con la misma pregunta. Se quitaron las frases.
- **El grupo de los tres de** pedía una pista sin «de»: la comprobación de pistas lee la palabra española «de» como si repitiera el pinyin. Se redactó sin ella.

## Seguimiento

**Nivel.**
- HSK 1: 384 de 506 (75,9 %; en el lote 015, 71,3 %). Te faltan 21 palabras para el 80 %.
- Ya puedes presentarte el primer día de un trabajo (你好，我叫孟逸辰，我是工程师。认识你很高兴，你是做什么工作的？), proponer un plan (你明天有时间吗？我们一起去游泳吧！), reaccionar (是吗？, 我也是！, 那你太惨了！) y alargar una respuesta (因为…，也…; 我觉得…，但是…).

**Las clases.**
- La del 6: lectura en voz alta, frases con palabras dadas, preguntas sencillas, el 3+3 y dos diálogos guiados. Es justo lo que convenía (conversación y pronunciación, más que vocabulario nuevo), y casi todo ya estaba en el mazo.
- Lo que más marcó: 是 / 师 y los tonos, 你每天几点起床？ y 你学中文多久了？.

**Tu método.**
- **Constancia**: 28 de los últimos 30 días; unos 26 minutos al día (antes 31) y 10 nuevas al día (antes 14).
- **En Anki**: 11 % de «Otra vez» y 88 % de retención. Los tonos, un 9 %; decir, un 16 %.
- **Tus notas**: siguen rindiendo tus frases, tus contrastes con «!!!» y los códigos de tarjeta. Las chuletas largas del asistente, mejor que vengan con tu marca de lo que te importa: así sé qué meter primero.

**Consejo.** La de construir del primer día de trabajo y la de proponer un plan son los diálogos de la clase del 6: hazlas en voz alta antes de la próxima clase, y apunta en «Tus notas» las frases tuyas que te dejen dudas.

**Avisos.**
- Este lote aplica por primera vez el orden de nuevas con el complemento propio: lo de clase sale primero de verdad. Sincroniza el móvil antes de estudiar.
- La cola de nuevas de tu nivel son unos 70 días: entra más de lo que estudias. No frena nada, pero estudiar 30 nuevas al día (abres unas 10) la acortaría.
