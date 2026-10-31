<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 015-2026-10-31-volver-a-casa-y-para-entender

**Origen.**
- **Tus respuestas al review 014**: todas las líneas «>» en blanco. Lo que el review dejaba dicho «salvo que digas que no» entra: las 20 de HSK 1 por frecuencia y fijar la lectura de 哦 y 得 děi.
- **«Tus notas» del review 014**: unas 1.600 líneas. Tus tablas de 回家 por fases, 一样, 让 / 要我帮你, 知道 / 懂, 还是, 坐 / 做 / 作, 次 / 遍, 更多 / 多一点, 一个人 / 自己, 太, 最好, 听不见 / 听不懂; tus mnemotecnias (洗, 洗澡, 间, 习, 点, 店, 商, 懂, 一起); los contrastes que pedías; las tarjetas que señalabas por su código; y tres propuestas de sistema (los clasificadores con su recuadro, los recuadros de «Para entender» en las tarjetas, un repaso de calidad cada pocos lotes).
- **Materiales de clase**: la clase del 30, la primera de las de los viernes (diapositivas, deberes, el audio de sílabas), tus deberes hechos del 23 y del 30, y tres vídeos del curso.
- **En el chat**: «recuerda que los estilos deben aplicarse también en infraphysics».

En cifras: 245 tarjetas nuevas y 1 retirada (3693 en total); 50 entradas (29 palabras, 1 expresión, 3 caracteres, 1 componente, 12 grupos y 4 estructuras) y 90 frases.

## Cambios en el sistema

- **«Para entender», en las tarjetas** (tu nota): un recuadro nuevo, 💡 «Para entender», con fondo propio, el primero bajo una línea que separa la respuesta, su contraste y los ejemplos de todo lo demás (lo de clase, tus mnemotecnias, las notas…). Las minilecciones de los reviews 011 a 014 pasan a la tarjeta de su palabra (la edad y 您多大年纪, 觉得 / 想, 左右, 再 / 在 / 又, 想, 会 / 能 / 可以, 去 / 回 / 到, 斤, 说得对, 这个 / 这里, 哪 + clasificador, 还 / 还是, 次 / 遍, 万…); la teoría de pronunciación sigue fuera, en tu cuaderno de papel. Desde ahora, cada «Para entender» del review se guarda también así.
- **Lo opcional, entre paréntesis** (tu nota): 我(今年)二十五岁, 他(是)一九九五年出生(的), 我跟你(一起)去. Más apagado; el audio dice la frase entera y, al escribirla, vale con ello o sin ello.
- **Los clasificadores, con su recuadro** (tu nota): 个, 本, 只, 岁, 斤… llevan un recuadro dentro de la línea en todas las frases.
- **Diálogos turno a turno** (tu nota de #66JRT): en su tarjeta de oír, cada persona suena aparte con su marca (🗣️ A, 🗣️ B) y detrás sale turno a turno con su traducción; como ejemplo en otras tarjetas suena entero, como te gustaba. Los 21 diálogos del mazo y los dos nuevos.
- **«Otras formas de decirlo» tiene que sonar distinto** (#VNYWX): 你猜她多大 / 你猜他多大 suenan igual; `check` avisa ahora de eso. Y la tarjeta del sonido de 洗 (#FSKB4) ya no mezcla la explicación con la respuesta: la respuesta es la sílaba, y en «Dónde sale» cada palabra trae una frase suya.
- **La lectura de 哦 ò y 得 děi, fijada**: una entrada puede llevar `tts` (pinyin SAPI) y todo audio que la contiene se genera con esa lectura. 9 audios regenerados.
- **Un repaso de calidad** (tu nota: «un contador interno…»): `anki.py audit` busca frases casi iguales, tarjetas del mismo tipo con los mismos objetivos, niveles escritos a mano y otras formas que suenan igual; lo repasa la retrospectiva cada cuatro lotes. Este lote se pasó entero (ver «Repaso de calidad»).
- **En la web**: las tarjetas de infraphysics.net usan el mismo HTML y CSS que Anki, así que el recuadro, la línea, los paréntesis, los clasificadores y los turnos salen igual; el cuaderno web pinta además los paréntesis y los clasificadores en sus frases y «Para entender» en la ficha de cada palabra. La web lee el mazo de GitHub en cuanto se sube (ya no de jsDelivr, que se negaba con un repositorio de más de 50 MB).
- Vive en `docs/goal.md` (rutina, «Cómo se practican las frases», «Cómo se le habla»), `docs/design.md` («Datos», «Comentarios», «Tarjetas», «Audio», «Retrospectiva», «Repositorio y privacidad», «Garantías»), `3-data/README.md`, `anki.py` y siete entradas del 2026-10-31 en `docs/decisions.md`; pruebas nuevas en `tests/` (`Lot015`).

## Material de clase

- **Diapositivas del 30**: lección 1-2 otra vez, con el repaso del principio (diez frases de dictado de animales: 猫和老鼠不是朋友, 老虎很大, 蛇是绿色的…), más pinyin (las finales con i, u y ü, el soplo b / p, d / t, z / c, g / k, el apóstrofo de 西安 frente a 先, y el erhua) y la frase sin verbo (他22岁, 今天8号, 现在10点10分). Entran siete frases del dictado para oír, las parejas para oír 鸡 / 七, 狗 / 口 y 西安 / 先, y la frase sin verbo como «Para entender» de 多大. El erhua no entra: solo mandarín estándar.
- **Deberes del 30**, resueltos: 你多大？ 我今年二十岁。 他1998年出生。 你属什么？ 我属马。 你猜他多大？ 他大概三十岁左右。 你今年几岁？ 请问您多大年纪？ 我觉得他四十岁左右。 他是2001年出生的，属蛇。 你觉得这只猫可爱吗？ 我是2000年出生的，属龙。 这只兔子真可爱。 Entran las que no estaban (大概, 兔子 y cinco frases). ⚠️ 这个孩子很年轻 (pregunta 6, la respuesta que esperaba la hoja) no es natural: 年轻 se dice de adultos jóvenes, no de un niño; no entra.
- **Tus deberes hechos**: los del 30, todo bien en la parte de elegir; los del 23, también (8. 你觉得他是谁 vale igual que 你猜他是谁). La página de oír (iniciales, finales y tonos de sílabas sueltas) no se puede corregir sin la hoja de la profesora: el audio de sílabas no se transcribe de forma fiable.
- **Vídeos del curso** (lecciones 1 a 3, unos 20 segundos cada uno): 早上好 / 早, 您叫什么名字 / 您是哪国人 / 我是英国人, y en una recepción 我找人 / 他叫什么名字 / 请稍等，他住在426房间. Entran 我找人 y el diálogo de la recepción, con tu nombre en lugar del del vídeo (los nombres de los ejercicios no entran).

## Tus respuestas al review 014

- **El reverso nuevo** y **哦 ò suelto**: sin respuesta. El reverso cambia otra vez (ver arriba); 哦 se genera ahora con la lectura fijada: vuelve a «Por verificar».
- **Las 20 de HSK 1 por frecuencia**: entran (ver «Palabras y frases nuevas»).
- **Fijar los polífonos**: hecho.

## Tus notas, en sus tarjetas

Antes de crear cada cosa, se buscó en el mazo (tu nota: «comprueba siempre que no esté ya creado»):

- **Ya existían, y te digo dónde**: «吃了，你呢» (la situación de «ya he comido, ¿y tú?»), el contraste 渴 / 喝, el matiz 次 / 遍, 听不见 / 听不懂 (matiz y situación), el grupo 坐 / 做, 再说一遍, y 门多萨, que se retiró en el lote 014 (en Anki ya no queda ninguna tarjeta; solo quedaba en la explicación en inglés de 我姓孟, corregida).
- **回家, por fases**: ocho frases para decir (我要回家了, 我在回家的路上, 我快到家了, 我还没到家, 我刚到家, 我已经到家了, 我还在家, 我刚回到家), la estructura 要…了 con su calco (我去回家 ✗) y un matiz 我到家了 / 我要回家了. Tu lógica de 了 y 要, en «Para entender»: 了 dice que algo ya cambió; con 要 delante, está a punto. Como avisabas, no todo es HSK 1: 刚 y 路上 son HSK 1–2; 等会儿, 这就, 正在, 当时, 待 y 本来 no entran (más arriba y poco conectados).
- **洗 y compañía**: 洗 entra (estaba en las 20), con tu imagen del aspersor, 先 como la pieza que le da el sonido («sin agua, 洗 es 先») y el contraste 喜 / 洗; tus mnemotecnias de 洗澡 (mucha agua), 洗手间 (lavar + manos + cuarto), 间 (un hueco: en el tiempo, entre paredes, el aseo) y 习. Los verbos separables (洗个澡, 吃了饭, 帮个忙) van como «Para entender» de la estructura 跟 + persona + 见面, con su calco (我明天见面他 ✗).
- **一样**: siete frases (我跟你一样高, 今天跟昨天一样冷, 我的房间跟你的一样大 —tu pregunta—, 我们不一样, 我也一样…), la estructura con su calco (我一样高跟你 ✗) y el grupo de las que suenan a yi: 一样 / 一定 / 一起 / 医生, con 我一定跟你一起去.
- **走吧, la trampa**: una de elegir, con 我们明天见面吧 en el bocadillo y 好啊，明天见！ como buena.
- **让 y 帮**: 要我帮你吗？ para decir, 你想让我帮你吗？ para oír, y el matiz 帮我 / 帮个忙 (帮忙我 ✗). Y en #… de 我来帮你, 我帮你吧 como otra forma de decirlo.
- **知道 / 懂**: un matiz y tu frase 我知道这个词，但是我不懂它的意思 (con 但是, como pedías). En #KN4P0, tu intuición entra en la respuesta: 明白了 es «ah, ya lo pillo»; 懂了, comprenderlo por dentro.
- **还是 y 但是**: 我还是想去, 外面还是很冷, tu 我休息了，但是我还是很累, dos huecos «¿但是 o 还是?» y su contraste de oído.
- **#X5FP1**: 我一定来 es «vengo seguro»; para «me encargo yo», 我来 + verbo o 我会处理的, que entra para decir (处理 es HSK 3, pero es de trabajo y lo pediste).
- **#NCMBN**: la tarjeta de decir «¿De qué país eres?» pide ahora las dos formas.
- **点, 店, 商**: tus imágenes (el reloj de madera de 点, 店 «un punto bajo techo», 商 «dos personas negociando en una casa») y la serie de 占: 点, 店 y 站, que entra. 品 no: no hay ninguna palabra suya en el mazo.
- **客 en 不客气** (#F946Y): «invitado»; 客人 [HSK 2], en la nota.
- **呢 y 吧**: en «Para entender» de 吧.
- **钅, 衤, 礻 y 车** (#Z3GQW): juntos en una familia con ejemplos de palabras que ya sabes (钱, 地铁, 裤子, 电视, 年轻), y el contraste 钅 / 车 (钱 / 轻).
- **己 / 已**: el contraste, y tu frase 我已经自己做好饭了，我们一起吃吧 («¡MUY BUEN EJEMPLO!»).
- **起 / 题** (对不起 / 问题), **书 / 出**, **超市 / 炒鸡**: parejas para oír; 我有一个问题 y 这个问题很难 para reforzar 问题.
- **更 / 能**: contraste de oído y tu 你能说得更慢一点吗？; 更多 / 多一点 (matiz), la estructura 多 + verbo + 一点 (你吃一点多吧 ✗) y 看看 / 看一下 (matiz: casi nada cambia).
- **一个人 / 自己**: 一个人 entra como expresión, con 我一个人住 y su matiz.
- **学习 / 学**: un matiz y su «Para entender»; 学 entra suelto (我想学游泳).
- **太, 最好, 我来**: 这个苹果太贵了，我不想买; el matiz 很忙 / 太忙了; 你最好今天去 / 你是最好的; 我来介绍一下, y en «Para entender» de 来 que 我来 no es «vengo a».
- **«我___去工作»**: una de elegir el orden (我早上八点去工作) y 我们上午十一点见, que de paso ayuda con 上午.
- **#VCEED** (saludar en una tienda): retirada, «por absurda».
- **#8HKQR**: no está repetida. Hay dos de elegir 是的: en el hotel (是的 frente a 好的 y 不客气) y en un taxi (frente a 对不起 y 好的). Misma respuesta, otra escena; se quedan las dos.
- **Tu examen pegado** (deberes del 23 corregidos por el asistente): coincide con lo que ya había; entran 他大概三十岁左右 y 这只兔子真可爱.
- **Las cards básicas con ejemplos cada vez más avanzados**: respondido en el chat y en «Para entender» del review.

## Palabras y frases nuevas

- **HSK 1 por frecuencia**: 下, 后, 起来, 站, 睡, 打球 (por 球), 唱歌 (por 歌; para oír: «cantar» ya es 唱), 包, 楼, 大学, 病, 汽车, 回到, 教, 洗, 肉, 班, 有的 y, por 外, 外面 (del desván). 第二 ya se dice con 第 + 二.
- **De tus notas**: 路上, 学, 作业, 一个人, 处理; 词 sube a decir.
- **De clase**: 老鼠, 老虎, 兔子, 白色, 绿色 (los colores y 老鼠 / 老虎, para oír) y 大概 (del desván).
- **Caracteres y piezas**: 喜 (el de 喜欢), 己, 已, 钅.
- **Grupos**: 喜 / 洗; 己 / 已; las piezas de la izquierda; 钅 / 车; 一样 / 一定 / 一起 / 医生; 但是 / 还是; 更 / 能; y los que solo separa el tono, que es lo que más fallas: 叫 / 教 / 脚, 水 / 睡, 半 / 班, 后 / 猴, 学 / 雪.
- **Estructuras**: 要…了, 跟 + persona + 见面, 跟 + persona + 一样 + adjetivo, 多 + verbo + 一点.
- **Tarjetas que creé por mi cuenta**: 9 matices, 3 de elegir, 2 huecos, 6 parejas para oír, 22 contrastes, 4 estructuras con su calco, 2 de construir (volviendo a casa, comparar pisos), 1 lectura y dos diálogos para oír.
- **HSK 1**: 361 de 506 (71,3 %).

## Del desván

- **外面** (por 外, de las 20) y **大概** (salió en los deberes del 30): entran.
- **Despiertan, pero esperan**: 灰色 (con 白色; los colores entraron solo para oír), 表演 y 明星 (con 唱歌, que es para oír).

## No entró, y por qué

- **El erhua de las diapositivas** (小孩儿, 饭馆儿): solo mandarín estándar.
- **De tus tablas**: 等会儿, 这就, 正在…的路上, 当时, 待一会儿, 本来, 很久没 (HSK 3 o más, o forma del norte); 赚 (HSK 4); 像…一样 (HSK 2, sin frase tuya; se queda en tu tabla); 同一个; 中国话 y 听话 (听话 es nivel 7 en la lista); 刚出生的小猫 (tú mismo dudabas); 动物.
- **De clase**: 这个孩子很年轻 (no es natural); los nombres de los ejercicios (白大龙, 迈克).
- **品**: ninguna palabra suya en el mazo.

## Reorganización

- **El tema «Cosas» pasaba de 60**: 病 va a «Describir» (es un estado) y 包 a «Compras».
- **Grupos nuevos**: los once de arriba; **ningún tema pasa del tope**.
- **El 还是 de un hueco** pasa a 我还是想去: tu frase con 但是 era de un nivel más que la palabra que se pregunta; tu frase se queda para decir.

## Repaso de calidad

`anki.py audit` sobre el mazo entero:
- **40 parejas de frases casi iguales**: casi todas son parejas buscadas (sí / no: 我知道 / 我不知道; 了 / 要…了: 我走了 / 我要走了). Ninguna es una tarjeta repetida.
- **18 grupos de tarjetas con el mismo tipo y objetivo**: las vocales para oír de palabras distintas, situaciones frente a sus tarjetas de elegir (otra pregunta), y matices distintos de una misma palabra. Ninguno se ve igual delante; se quedan.
- **Un nivel a mano** de algo de la lista: el componente 户, que toma el nivel de 窗户 [HSK 4], donde se ve; tiene su motivo y se queda.
- **Otras formas que suenan igual**: una (#VNYWX), corregida.

## Fricciones del proceso

- **El registro de materiales apuntaba a la carpeta antigua**: todos salían pendientes; se rehízo el registro con las rutas nuevas (con copia).
- **La herramienta de transcripción afina las voces guardadas** de la clase: para los vídeos del curso, con otras voces, se transcribió aparte, sin tocarlas.
- **`lookup` uno a uno es lento** (unos 20 s cada uno, carga el mazo entero) y se rompió a medias al editar `anki.py` mientras corría: las búsquedas se hicieron en un solo proceso.
- **Choques de ID**: 后, 睡 y 班 iban a usar `w.hou`, `w.shui` y `w.ban`, que ya eran 猴, 水 y 半; y 词 ya existía, para oír. El constructor del lote lo detectó antes de escribir.
- **Un archivo de tema sin frases** (`ocio`) cortó la primera escritura a medias: se deshizo y se repitió.
- **El color por tono pintaba las respuestas ocultas** con las que se compara lo escrito: invisible en Anki, pero rompía la exportación. Corregido y con prueba.
- **Finales de línea**: un script de edición pasó `anki.py` a CRLF; se devolvió a LF.
- **Una prueba daba por hecho que 学 no tenía palabra propia**: ahora la tiene, y deja de pedir su tarjeta de sonido, como debe; la prueba usa 们. Y una pasada de las pruebas falló al leer un YAML que se estaba editando a la vez: se repitió entera con los datos quietos (138 de 138).

## Seguimiento

**Nivel.**
- HSK 1: 361 de 506 (71,3 %; en el lote 014, 67,4 %). Te faltan 44 palabras para el 80 %.
- Ahora ya puedes contar dónde estás de camino a casa, comparar (igual de alto que tú), ofrecer ayuda (要我帮你吗？) y decir «sigo queriendo ir» (还是).

**Las clases.**
- La del 30, la primera de los viernes: lección 1-2 por cuarta vez, con más pinyin (el soplo, las finales con i, u y ü, el apóstrofo) y dictado de animales. Los vídeos del curso adelantan la lección 1-3: nacionalidad y buscar a alguien.
- Con una clase por semana, la lección 1-2 se alarga. El vocabulario de edad y zodiaco ya está entero en el mazo: conviene pedirle a la profesora pasar a la 1-3 y más conversación, que es lo que una clase a la semana da y el mazo no.

**Tu método.**
- **Constancia**: 28 de los últimos 30 días, unos 31 minutos por día (antes 26) y unas 14 nuevas al día.
- **En Anki**: 12 % de «Otra vez» y 88 % de retención (antes, 16 % y 86 %). Los tonos fallan un 10 % (40 repasos; antes, 34 %); leer, un 15 %, y decir, un 12 %.
- **Tus notas**: las que mejor rinden siguen siendo tus frases y tus confusiones con el código de la tarjeta. Las explicaciones largas del asistente rinden cuando marcas lo que te importa («!!!», «ES IMPORTANTE», «MUY BUEN EJEMPLO»): eso entró casi entero; el resto se quedó en recuadros 💡.

**Consejo.** Mira las tarjetas nuevas en el móvil unos días y fíjate en el recuadro 💡: si te sobra o te falta, dilo con el código de la tarjeta.

**Avisos.**
- Antes de estudiar, sincroniza el móvil: cambia el aspecto de muchas tarjetas.
- 哦 y 得 děi suenan ahora con su lectura fijada: escucha una y dime si está bien.
- El workflow `publish` del repositorio ya no sirve (purgaba jsDelivr); se quita cuando digas.
