<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 013-2026-10-23-pagar-opinar-y-contrastes

**Origen.**
- **Tus respuestas al review 012**: «sí, sí y sí» a las tres dudas de la tabla de fórmulas y ejemplos; el resto, en blanco.
- **«Tus notas» del review 012**: unas 1000 líneas, del 19 al 23. Tus mnemotecnias, confusiones que notas al estudiar, contrastes que pedías, comentarios sobre cómo se ven las tarjetas, tu nombre chino y muchas consultas pegadas de un asistente (有 «hay», 一点 y 有点, 得 tras el verbo, 先, 开, 意思, 常, los kilos).
- **Tu apunte del 21** (`contexto-antes-que-la-tarjeta.md`): que una tarjeta no salga antes que su contexto.
- **Materiales de clase pendientes**: las diapositivas y los deberes de la clase del 23, el audio de sílabas de esos deberes y tus deberes corregidos del 8, el 13 y el 15, con la hoja de respuestas del 8.
- **En el chat, al empezar**: el inbox completo y el móvil sincronizado.

En cifras: 321 tarjetas nuevas y 13 retiradas (las de tu nombre antiguo); 41 entradas (40 palabras y un carácter), 3 estructuras, 12 grupos nuevos y 3 ampliados, y 104 frases nuevas (3 retiradas, las del nombre).

## Cambios en el sistema

- **Fórmula o ejemplo, aplicado**: las 638 frases llevan su `kind`, y las 63 fórmulas que estaban fuera de su situación se mueven a ella con sus 88 tarjetas. Al hacerlo, las frases dejaron de exigir tarjetas: el código las reconocía por no tener `kind`. Ahora se reconocen por sus segmentos (`is_sentence`), con su prueba. Vive en `anki.py` (`is_sentence`).
- **El contexto que se ve, antes que la tarjeta** (tu apunte del 21): una tarjeta no sale antes que las palabras que enseña escritas (la consigna, el material de construir, el contexto de huecos, matices, contrastes, estructuras y comprensión). Al mezclar, espera a que salga la palabra si está en el mismo tramo; si está en otro, la primera tarjeta de la palabra se adelanta. Las palabras que solo suenan o que hay que decir en una frase no cuentan. Antes, 73 tarjetas nuevas enseñaban escrita una palabra que aún no había salido; ahora, ninguna, y la mezcla por tipo no cambia. Vive en `docs/goal.md` («Siempre mezclado»), `docs/design.md` («Anki») y `anki.py` (`shown_context`, `interleave_streams`, `context_first`).
- **Lo que te dicen, en un bocadillo**: un campo `said` en la consigna. Delante, 💬 con el hanzi y el pinyin grandes, y su audio; debajo, 💬 «…», tu turno. Detrás, lo que te dijeron, traducido. Las 15 tarjetas donde alguien decía algo (8 situaciones, 3 de elegir, 3 de dar la razón o contestar y una de no poder) pasan a él. Vive en `docs/design.md` («Tarjetas»).
- **El chino de matices y contrastes, grande**: uno debajo de otro, con una línea solo para «/» entre medio; en la consigna del matiz queda la pregunta.
- **«Uso real»**: un tipo de comentario (`usage`) con su recuadro, para cómo se dice de verdad (机票 frente a 飞机票, 吃饭了吗 como saludo).
- **La trampa del hueco vacío** (`gap_after`): un sitio vacío detrás de una palabra, con «(nada)» entre las opciones.
- **Compras se divide**: «Compras» (tiendas, precios, pesos, entradas) y «Comida y bebida» (33 entradas, 38 frases y 134 tarjetas). Cambian de subdeck una vez y conservan su progreso.
- **Web**: el cuaderno de InfraPhysics ponía «ni3 hao3» de ejemplo en la caja de escribir, que es justo la respuesta de la tarjeta de 你好. Ahora dice «pinyin con el número de cada tono, o hanzi» (en la plantilla de InfraPhysics, sin subir).
- `docs/decisions.md`, seis entradas del 2026-10-23; pruebas nuevas en `tests/` para el contexto, el hueco vacío, el bocadillo, los matices, los contrastes y «Uso real».

## Tus respuestas al review 012

- **Fórmula o ejemplo** («sí, sí y sí»): aplicado, ver arriba. No corregiste ninguna fila: la tabla entra tal cual.
- **Las 10 tarjetas de oír con repasos**: sin respuesta, se quedan.
- **El banquillo**: sin respuesta, no se monta; vuelve al review.

## Tus notas, en sus tarjetas

- **Tus mnemotecnias**, con tu texto en `original`: 错 cuò (el arma de asta sobre la rejilla de un lote defectuoso; se queda también la del concurso), 到 dào (dos velas), 岛 dǎo (la montaña con un pájaro encima), 鸡 jī (la mano que agarra un pájaro), 本 běn (el estandarte de la biblioteca), 趣 qù (correr a coger algo), 取 qǔ (la mano y la oreja), 意 yì y 思 sī, 同意 tóngyì, 常 cháng (los señores con rulos), 公 gōng (el gong), 哥哥 gēge (los archivadores), 弟弟 dìdi (los niños disfrazados de dragón), 可以 kěyǐ (el plato y el camarero; el ojo de sapo) y 开 kāi (el monigote que echa a andar).
- **到 no es «salir»**: escribiste «dào es salir afuera». Es «llegar»; salir es 出. Va como nota en 到, y 我们到岛上了 junta 到 y 岛 en una frase, como querías.
- **有 «hay»** («IMPORTANTE»): nota en 有; estructura «sitio + 有 + cosa» con su calco (商店是水吗 ✗); matiz 这里有… / 我有…; frases 这里有很多人 y 这里有两斤左右的苹果. Tu 我觉得有两斤苹果左右 lleva 左右 en mal sitio: va detrás de la cantidad, 两斤左右的苹果.
- **Los kilos**: 我要三斤苹果; 我要一个斤苹果 ✗ como calco de la estructura «número + 斤 + cosa»; 苹果多少钱一斤 y 一斤苹果多少钱 se dan por buenas la una a la otra; tonos de 一斤, 一个, 一块, 一千, 一万, 一年, 第一 y 十一; y seis frases de números para oír (precios, la hora, la fecha, la población de Pekín).
- **一点 y 有点, 少, 很多, 多少**: dos matices (贵一点 / 有点贵; 钱很少 / 一点钱), 有点 para decir (HSK 2, sin el 儿), notas en 一点 y frases (给我一点水, 我想吃一点, 今天有点冷, 有点贵, 这个贵一点, 我的钱很少).
- **觉得 para opinar**: 不错 y 一般 para decir; 我觉得不错, 我觉得可以, 我觉得不太好, 我觉得一般, 我不太喜欢; un diálogo; y el matiz de 这个你怎么样 ✗.
- **得 tras el verbo**: estructura «verbo + 得 + 不 + adjetivo» con tu 你说不是对 ✗; frases 你说得不对, 你做得很好, 她唱得很好; matices 说得不好 / 说得不对 y 这个不对 / 你说得不对.
- **Lo que confundes**: 你 / 欢 por la forma, 多 / 都 y 朋友 / 苹果 al oído (con su pareja para oír), 五 / 午 (suenan igual), 很 / 跟 (comparten 艮), 开 / 进 (井), 去 / 取 (我去取钱), 国 en 中国 (un matiz), 走 / 坐 y 早 / 走 (parejas), y cinco huecos de 坐 / 做 con escena, en los que la escena engaña (坐飞机 parece «hacer», es «ir en»). 牛 / 午 ya tenía su contraste. Para 家 jiā, una imagen de sonido propuesta por el agente.
- **La trampa** (大家都＿忙): cuatro huecos con «(nada)» entre las opciones; tres son nada y uno es 是 (她不是老师), para que no se conteste siempre lo mismo. Y las frases de 是 con nombres y sin 是 con adjetivos que pedías.
- **先, 常, 开, 走, 取**: 你先说吧, 我先看看, 我先问一下, 我先回家, 你先走吧; 常 para decir, con el matiz 常 / 常常 y 不常; 开始 y 打开 para decir, notas en 开, el matiz 开门 / 进门 y el de 我今天有个会 / 我今天要开会; 走路; 取 con 取钱. Y el matiz 出去 / 走 / 离开 que pedías.
- **意思**: 这是什么意思？, 我不明白你的意思。, 很有意思！ y la nota de 你是什么意思 (puede sonar desafiante).
- **你还好吗**: la traducción pide ahora el matiz («¿Estás bien? (preguntado con preocupación)»).
- **明天来 / 明天再来**: un matiz.
- **El 哪个 de 你来自哪个国家**: un matiz (哪个国家 / 哪本书) y 我从西班牙来, con 从 para decir.
- **飞机票**: «Uso real» en 机票.
- **La tarjeta de 我们下午见吧 sin traducir**: con el bocadillo, detrás sale lo que te dijeron.
- **Tu nombre**: 孟逸辰 Mèng Yìchén en lugar de 雅戈 y 门多萨. Ver «Cambios en el sistema» y `docs/decisions.md`.
- **El artículo de InfraPhysics** (aprender de lado lo que propone el modelo; sistema y método a la vez): fuera del lote, en el repositorio de InfraPhysics.

## Palabras y frases nuevas

- **De tus notas**: 同意 (del desván), 不错, 一般, 有点, 取, 常, 开始 (HSK 3, de las más frecuentes), 打开, 从, 走路, 付钱 (pagar, que faltaba desde el lote 010) y, del desván, 扫码; 鸟 para oír.
- **De la clase del 23**: el dictado del principio (你猜他多大了？…, 这个杯子多少钱？…三十五元, 你觉得今天的天气怎么样？…不冷不热, 你的朋友是哪年出生的？…属猪) para oír; el diálogo para completar (爸，妈，我来介绍一下…, 你真年轻！, 谢谢阿姨！, 你父母多大年纪了？, 我爸爸五十二岁…, 哦，你属什么？, 我属龙，今年二十四岁); 爸 y 妈 al llamarlos, 一定 y 哦; y de la lista de pinyin zh / ch / sh / r, 知识, 上车 y 超市 para oír.
- **Deberes del 23, resueltos**: 他今年二十岁, 我今年二十五岁, 我一九九六年出生, 我在北京出生 (vale también 我出生在北京), 你猜他是谁？, 他二十岁左右, 这是我的狗, 我很喜欢这只小猫, 你觉得这只狗可爱吗？ Los animales del zodiaco y las demás elecciones ya estaban en el mazo.
- **HSK 1 por frecuencia** (propuesta del agente): 上, 小, 事, 新, 话, 看到, 车, 找到, 老, 放, 送, 笑, 远, 坏, 唱, 风, 爸, 妈, 听到 y 别的, cada una con su frase.
- **Construir**: tres escenas (pagar en el súper, las fotos de un viaje, conocer a los padres de un compañero).
- **Monólogos y diálogos para oír**: en el súper, pagar con el código, el signo del zodiaco, opinar y tu presentación con tu nombre nuevo.
- **Fichas de hanzi**: 21 caracteres nuevos; 辰 y 市, de origen discutido, solo con su imagen.

## Contrastes nuevos

- **Por la forma**: 你 / 欢, 开 / 进; **por la pieza que da el sonido**: 很 / 跟.
- **Al oído**: 多 / 都, 朋友 / 苹果, 去 / 取, y los que traen las palabras nuevas (`check` exige agrupar lo que suena igual sin tonos): 话 / 花, 长 / 常 / 唱, 一般 / 一半, 小 / 笑, 元 / 远; 事 entra con 是 / 试 / 十, 妈 con 吗 / 马 y 爸 con 八 / 吧. Y 五 / 午, que suenan igual.
- **Parejas para oír de tus deberes corregidos**: 张 / 江, 热 / 这, 个 / 课, 字 / 次, 奶 / 买, 风 / 分, 绿 / 路, 坏 / 会, 先 / 些, 吃 / 去, 国 / 果 y 没 / 每; y de tus notas, 多 / 都, 走 / 坐, 早 / 走, 去 / 取 y 朋友 / 苹果.

## Material de clase

- **Diapositivas del 23**: lección 1-2 otra vez, con ocho diapositivas nuevas: el repaso, la lista de zh / ch / sh / r, el cambio de tono de 一 (tres diapositivas), el diálogo para completar y el dictado del principio. Lo útil, arriba; la teoría del cambio de tono no va a las tarjetas (está en tu cuaderno): entra como tarjetas de oír los tonos de 一 con números.
- **Deberes del 23**: resueltos, ver arriba. La página de oír (iniciales, finales y tonos con j, q, x) va con el audio de sílabas, que no se puede transcribir de forma fiable.
- **Deberes corregidos del 8, el 13 y el 15** (con la hoja de respuestas del 8): 30 fallos en 162 casillas de oír. El tono es casi la mitad (14), sobre todo el 2.º (5); luego j q x / zh ch sh (4), las nasales (4), el soplo (2), la ü (2) y la vocal del medio (2). Bajan de un 23 % el 8 a un 18 % el 13 y un 12 % el 15. Fuera del oído, dos fallos: 十万六千二百三十四 y 您多大年纪了. Van a «Para entender» y a las parejas para oír; además, YAGO tiene fuera del mazo un programa de práctica con esas mismas confusiones.

## Del desván

- **Entran**: 同意, que despertó al volver a investigarlo (lo tenías con 我同意 desde el lote 009), y 扫码, que despertó con 付钱: para pagar en China, casi todo se escanea.
- **Despiertan y esperan** (`snooze`): 发票 (HSK 4; para el día a día bastan 付钱 y 扫码), 确定 (HSK 3; 一定 ya dice «seguro») y 继续 (palabra de un ejercicio de pinyin: espera a salir en clase).
- **市** despertó con 超市, pero no tiene uso propio: su nota pasa a 超市 y sale del desván.
- **Entran al desván**: 思考 y 思想 (de tu consulta sobre 意 y 思; para pensar basta 想), 大概 (para aproximar ya está 左右), y de la lista de pinyin de la clase, 热闹, 出差, 厨师, 常识, 事实, 手术, 充值, 长城 y 燃烧.

## No entró, y por qué

- **超人** (Superman), de la lista de pinyin: no es vocabulario.
- **一张, 一条, 一种** (diapositivas del 一): sus clasificadores aún no están en el mazo; los tonos de 一 se practican con números y 个, 块, 斤.
- **Lo de HSK 3 a 5 de tus consultas**, salvo lo frecuente (开始) o lo de clase: ver «Del desván».

## Reorganización

- **Compras se divide** en «Compras» y «Comida y bebida» (ver arriba).
- **Las fórmulas, a su situación**: las 63, ver arriba.
- **Cosas** pasaba de 60 entradas al entrar los verbos nuevos: 走路 va a Lugares, 唱 a Tiempo libre, 笑 a Describir, 看到 y 听到 a Entender y 事 a Trabajo.
- **Tu nombre**: 13 tarjetas retiradas y sus frases sustituidas; 门多萨 y 雅戈 quedan descartados con su motivo. En Anki se borraron las 11 sin ningún repaso (con `--prune --force`, tras comprobar una por una que eran esas); leer 雅戈 y leer 门多萨 tienen repasos y siguen allí, a la espera de su respuesta.

## Fricciones del proceso

- **Al clasificar las frases, dejaron de exigir tarjetas, sin aviso**: el código reconocía una frase porque no tenía `kind`. Salió al ver que las frases nuevas no tenían tarjeta y `plan` no lo echaba en falta. Arreglado con `is_sentence` y su prueba.
- **La primera versión del contexto descuadraba la mezcla**: adelantaba las palabras de todas las frases y leer subía al 43 % de las próximas 400 nuevas. Se rehízo dentro de la mezcla, contando solo lo que se ve escrito.
- **Escritura de datos**: un ayudante de un solo uso añadió comentarios después de otro campo en tres entradas y rompió el YAML (arreglado en el acto); dos frases ya existían (我不忙, 我明天再来), cazadas antes de escribir; la estructura del «hay» se rehízo porque 这里 no cabía en el hueco de lugar.
- **Las diapositivas de 113 páginas no se pueden leer como PDF** sin pdftoppm: se convirtieron con PyMuPDF en un entorno temporal.
- **El ayudante de edición cambió los finales de línea** de 60 archivos en la primera prueba (CRLF); se restauraron sin cambios de contenido.
- **Las pruebas siguen pasando de 10 minutos** (unos 18 este lote), y tres pruebas antiguas suponían cosas que el lote cambió a propósito: la pareja de 十 (ahora puede ser 事), el bloque de clase sin intrusas (ahora se cuela lo que una tarjeta de clase enseña escrito) y la primera tarjeta de la cola. Se ajustaron sin dejar de comprobar lo de fondo.
- **Un polífono suelto (哦 ò) puede leerse mal** con la voz sintética: el `<phoneme>` de Azure sí funciona (comprobado fuera del mazo, con reconocimiento de voz), pero `anki.py` aún no lo usa.

## Seguimiento

**Nivel.**
- HSK 1: 336 de 506 (66,4 %; en el lote 012, 61,3 %). Te faltan 69 palabras para el 80 %.
- El salto viene de las 20 de HSK 1 por frecuencia y de lo que pedías en tus notas (从, 常, 打开).

**Las clases.**
- La clase del 23 sigue en la lección 1-2 (edad y zodiaco): repaso, pinyin (zh / ch / sh / r y el cambio de tono de 一) y un dictado. La unidad 3, nacionalidad y ciudad natal, aún no ha empezado.
- Tus deberes corregidos dicen lo mismo que Anki: el tono es lo que más falla, sobre todo el 2.º. Pero vas a mejor: del 23 % de fallos de oído del 8 al 12 % del 15.
- Desde el 30 de octubre, una clase por semana: buen momento para pedirle a la profesora más tonos y hablar, como querías.

**Tu método.**
- Has estudiado 26 de los últimos 30 días, unos 22 minutos cada uno. Abres unas 11 nuevas al día, no 30: la cola crece más deprisa de lo que estudias.
- En Anki: 19 % de «Otra vez» y 83 % de retención (en el lote 012, 21 % y 79 %). Los tonos fallan un 44 % y decir un 32 % (antes, 55 % y 43 %): siguen siendo lo difícil, pero bajan.
- Tus notas son tu forma de investigar, y rinden cuando son contrastes y confusiones tuyas («confundo 多 con 都», «guó con zhōng»): esas entran casi todas. Lo pegado de HSK 3 a 5 (思考, 思想, 大概) espera; tú mismo lo notaste.

**Consejo.** Cuando le preguntes al asistente, pídele que se quede en HSK 1-2 y que te dé contrastes y frases cortas, no listas. Y diez minutos al día con el programa de oído de tus deberes, mejor que solo releer.

**Avisos.**
- Antes de estudiar, sincroniza el móvil: este lote mueve muchas nuevas (el contexto antes) y retira 13 tarjetas.
- Las 10 tarjetas de oír y el banquillo siguen esperando tu respuesta.
