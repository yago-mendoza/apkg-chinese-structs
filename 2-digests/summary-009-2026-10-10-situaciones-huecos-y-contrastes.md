<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 009-2026-10-10-situaciones-huecos-y-contrastes

**Origen.**
- **Tus notas en el review 008**:
  - tu crítica del diseño de las tarjetas;
  - tus correcciones;
  - muchas consultas que pegaste: 想 / 要 / 想要 / 需要, 不 / 没, 怎么样, 进来 / 进去, 会 / 回, 过, 好 «qué…», 坐 con transportes y la pronunciación de chī frente a qī;
  - tu lista de 16 frases de conversación.
- **Lo que pediste en el chat**: que el mazo esté siempre mezclado por tipo de tarjeta, menos carga en cada tarjeta y más ejemplos y audio.

Nivel HSK 1 salvo que se indique.

## Cambios en el sistema

Lo cuenta entero [la decisión](/docs/decisions.md#2026-10-10--tarjetas-que-se-puntúan-de-cabeza-huecos-parejas-que-suenan-juntas-y-nuevas-siempre-mezcladas). En corto:

- **Nuevas siempre mezcladas.**
  - En Anki, las primeras 100 nuevas no traían ninguna de decir, solo bloques de dictados y de frases para oír.
  - Ahora cada tramo trae oír, decir, leer y contrastes, y nunca más de dos seguidas del mismo tipo.
  - Las frases para decir salen desde el principio.
  - Los pasos de una palabra (leer, oír, decir) salen separados unas 15 nuevas, un día tuyo de estudio. Con esto queda resuelta la decisión pendiente de escalonar las de decir.
  - Está en `docs/design.md`, «Anki».
- **Una tarjeta, una respuesta corta.** Tú contestas de cabeza y te puntúas. Por eso `check` avisa si la respuesta de un matiz o de una situación pasa de 160 caracteres. Lo que necesita un párrafo se parte en situaciones o huecos.
- **Parejas que suenan juntas.**
  - Cada par de sílabas (shì / chī, chī / qī…) es ahora una sola tarjeta.
  - Suenan las dos, una tras otra, y se pregunta cuál es cuál.
  - Detrás vuelven a sonar, con su pinyin.
- **La teoría de pronunciación, de cara.**
  - Fuera las de «lee en voz alta» con el pinyin delante.
  - Ahora son preguntas directas sobre un caso: ¿cómo suena 一 en 一个?, ¿cómo suena la i de 四?
  - Se responden en una línea; la explicación larga, al final del reverso.
- **El reverso, de más a menos importante.**
  - Primero, los ejemplos con audio (ahora hasta tres) y tus notas.
  - Después, los recuadros y el porqué de cada hanzi, cada carácter con su sílaba (lo pedías: «los pinyin de sílabas no aparecen»).
  - Al final, la teoría.
  - Los ejemplos de cada regla de pronunciación llevan ya su pinyin.
- **Recuadros sin listas ni otro nivel.**
  - Fuera de su propia tarjeta no sale un grupo de más de cuatro: lo de 谁 con las nueve palabras de pregunta.
  - Tampoco sale un miembro de nivel superior al de la tarjeta.
  - Era tu respuesta por defecto a la primera pregunta del review 008.
- **El nivel de un sentido.** Una entrada puede fijar su nivel cuando su sentido no es el de la lista, con el motivo escrito (`sense_level`). Entra así 王 como apellido, nivel 1.
- **Varios huecos por regla y «También vale».**
  - Varios huecos de una palabra, cada uno en su frase, ya no cuentan como redundancia.
  - Una tarjeta de decir puede dar por buena otra forma de decirlo (我们是朋友 / 我和他是朋友).
- **Diálogos.** Entran cuatro o cinco por lote, como proponía el review 008; en este, cuatro.
- **Tus notas.** «Tus notas» del review es el sitio oficial de tus apuntes entre clases, como proponía el review 008; `homework-feedback.md` queda como cuaderno opcional.

## Tarjetas que se van y qué las sustituye

Se borran 56 tarjetas; casi ninguna tenía repasos:
- las 24 de sílabas sueltas;
- las 8 de 一 / 不 de una sola palabra;
- las 11 de «lee en voz alta» de pronunciación;
- 13 de matiz con párrafo.

Las sustituyen:

- **Parejas para oír (15):**
  - shì / chī, shì / sì, chī / qī (la i de chī no es i), sì / cì y shī / xī;
  - zhǎo / zǎo, chǎo / cǎo, jiā / xiā, xīn / qīn y qiú / jiǔ;
  - xīn / xīng, fàn / fàng;
  - chū / qù: la u frente a la ü, como pedías;
  - 一本 / 一个 y 不是 / 不好.
- **Preguntas de pronunciación (18):**
  - 一 en 一个, 一本 y 第一; 不 en 不是 y 不好;
  - 水 en 水果, el tercer tono de 老师, la sílaba átona de 朋友;
  - el aire de 他, la h de 很;
  - las sílabas de 西班牙人, la lengua curvada en 学生;
  - la i de 四 y de 是, la e de 喝 y de 谢, la u de 去, la o de 我.
- **Vocales para oír y completar (6):** p_ngy_u (朋友), h_ (喝), x__x__ (谢谢), h_n (很), x__ (学) y q_ (去).
- **Situaciones (21), en vez de «¿cuándo cada uno?»:**
  - saludar en una tienda (你好), a la vecina a mediodía (吃饭了吗) y a quien sale con prisa (去哪里啊);
  - preguntar qué tal (最近怎么样), si anda liado (最近忙吗) y devolver la pregunta (我很好，你呢);
  - proponer (我们明天去，怎么样), preguntar qué pasa (怎么了) y dar la bienvenida (欢迎回来);
  - pedir que te sujeten algo (帮我拿一下) y que echen un vistazo (请你看一下);
  - irse (走吧), asumir la culpa (我的错), «espere un momento» (请稍等), «ya lo sé» (我知道) e invitar (我请客);
  - decir tu apellido y tu nombre, y preguntar el apellido con respeto (您贵姓);
  - «¿qué estás haciendo?» y «¿cuándo vienes?».
  - Las de edad, «¿estás bien?», «¿en serio?», 小心 y 没问题 ya existían.
- **Huecos de reglas (17):**
  - 不 / 没 en un hábito, un adjetivo, una decisión, con 要 y en lo que no ha pasado;
  - 没有 con 有;
  - 想 / 要 / 想要 / 需要 / 喜欢 y 要 / 有;
  - 进来 / 进去, 怎么样 para proponer y 回 tras 会.
  - Las opciones van en la consigna: «¿不 o 没? «No tomo té.»».
- **Dos matices cortos nuevos:**
  - 早上 frente a 明天, los dos «mañana»;
  - qué partes del día acaban en 上 y cuáles en 午 (pedías una tarjeta sobre el segundo hanzi).
- **Matices que se quedan, más cortos:** 也 / 都 al final, 很高兴, 饭 / 吃饭 / 食物, 次 / 遍 y la posición de 了.

## Contrastes nuevos

- ✅🃏 **Visuales**, con los hanzi juntos en la tarjeta como pedías:
  - 对, 时, 的 y 狗: tus «conejitos»;
  - 有 / 看;
  - 西 / 四;
  - 日, 白, 百 y 目 (自 no está en el mazo).
- ✅🃏 **Al oído:** 会 huì / 回 huí, 最近 / 再见 y 王 / 忘.
- ✅🃏 **Mismo sonido, distinta pieza:**
  - 进, 近 y 今: 进 lleva 井, «pozo», que le da el sonido;
  - 坐, 做 y 左.

## Palabras y frases nuevas

- ✅🃏 **Para decir:**
  - 进来 / 进去 «entrar hacia aquí / hacia allí»;
  - 做 «hacer»;
  - 回 «volver»;
  - 多 «mucho»;
  - 贵 «caro»;
  - 真的 «de verdad»;
  - 什么时候 «cuándo»;
  - de tu lista de 16, 走吧, 怎么了 y 我的错;
  - 请客 «invitar» [HSK 2];
  - 稍等 «un momento» [HSK 2, estimado].
- ✅🃏 **Para oír:**
  - 出 «salir»;
  - 开车 «conducir»: para ir en un transporte se usa 坐, y 开车 si conduces tú;
  - 旁边 «al lado»;
  - 王 como apellido.
- ✅🃏 **Para reconocer:**
  - 西 «oeste», para el contraste con 四;
  - 近 «cerca», el de 最近 [HSK 2];
  - 时 y 今, ligados.
- ✅🃏 **Frases nuevas:**
  - 我还没吃饭, 他还没来 y 你还在吗 (还, como pedías);
  - 我会回来 «volveré»;
  - 明天再说;
  - 我没去过中国;
  - 好冷！ y 好贵！ (好 = «qué…»);
  - 我开车去;
  - 你要小心;
  - 你在做什么？;
  - 我真的知道;
  - 王阿姨好.
- ✅🃏 **Cuatro diálogos para oír:**
  - 你怎么了？…走吧，我们去吃饭！;
  - 我会说中文。真的吗？真的！;
  - 你回来了！…今天好冷！;
  - 你什么时候去中国？…我想坐飞机去。
- ⚠️ **Del ejemplo de 吗 sale 一起**, como pediste: 你想跟我吃饭吗？.

## Tus notas, en sus tarjetas

- **Tus imágenes:**
  - las manos de 对不起 (juntas, como quien afirma) y de 不客气 (la mano que dice que no);
  - 东西, todo lo que hay entre el este y el oeste;
  - el truco de 没关系: «¡eso no tiene relación con nada importante!»;
  - 可以 suena a «can»;
  - el ala de 习, la cabeza que camina de 道;
  - el sol que se libra del trabajo en 晚;
  - el corazón y la papelera de 忙.
- **Explicaciones:**
  - 想要 frente a 想有;
  - 那个 nèige;
  - 怎么样, el «¿qué tal?» chino, con sus usos;
  - 为 «para, por» en 为什么;
  - 米饭 frente a 吃饭, y 他不吃东西 para el que no come;
  - 过 como sello en el pasaporte;
  - 知 suelto suena literario;
  - los usos de 的;
  - el 月 «carne» de las partes del cuerpo;
  - y que preguntar es wèn, no wèi.
- **Ya estaban:**
  - 你还好吗 «¿sigues bien?»;
  - 要 «tener que»;
  - 啊 en 去哪里啊;
  - el 再 de «después» (明天再说 añade el ejemplo);
  - 吧 ya tenía sus cuatro tarjetas (leer, dictado, hueco y contraste con 八), que con el orden mezclado te llegarán antes.

## Del desván

- ✅ 王 «Wang (apellido)», para oír: ya puede fijar su nivel por sentido.

## No entró, y por qué

En el [desván](/3-data/attic.yaml), con tus notas:
- **Sin conexión, de nivel superior y fuera de clase:** 理解, 确定, 同意 y 主意 [HSK 3], y 道歉 y 原谅 [HSK 6]. Son de tu lista de 16 frases.
- **Las posiciones con 面:** 里面, 外面, 上面, 下面, 前面 y 后面 [HSK 3]. Entrarán juntas cuando lleguen en clase.
- **Partes del cuerpo:** 脸 y 脚 [HSK 2].
- **井 «pozo»** [HSK 6]: queda dicho en la tarjeta de 进 como la pieza que da el sonido.
- **免:** 免费 y la familia de 免 no entran (免 es HSK 7). Basta su papel en la imagen de 晚.

## Reorganización

Sin cambios de temas. Grupos nuevos: los siete contrastes de arriba y 王 / 忘. Dos tarjetas cambiaron de archivo a su tema: 我知道, a «Cosas», y 早上 / 明天, a «Saludos».

## Fricciones del proceso

- **Huecos de nivel superior:** `check` avisó que varios usaban 咖啡 (HSK 3) o 猫 (HSK 2). Se rehicieron con 茶 y con 时间.
- **Una frase duplicada:** 我们是朋友 ya existía; `check` lo detectó como ID repetido.
- **El heredoc de bash** falla con textos largos con comillas: los scripts del lote se escribieron como archivos.
- **La primera subida dejó la pronunciación en bloque al frente.** La mezcla se calculaba con todas las tarjetas, también las ya vistas, y casi todas las de leer del principio ya lo estaban. Se vio en Anki y se corrigió: se calcula solo con las nuevas, y la pronunciación va en su propia cola, repartida.
- **La prueba de la mezcla destapó dos fallos del nuevo orden.** Al soltarse una cola que esperaba, salían seis de decir seguidas; se arregló limitando las rachas. Y al final de un nivel no queda con qué separar los últimos pasos.

## Añadido tras el cierre

Al repasar el review 008 punto por punto quedaban cosas sin hacer:
- **Dos frases que marcaste con «!!!»**, para decir y oír: 你真的知道吗？ y 请问，你需要什么帮助？, esta también como situación (atiendes en una tienda).
- **Los huecos que faltaban del banco de palabras:** 爱 frente a 喜欢 (我爱你) y 想有 frente a 想要 (我想有一个家).
- **El cuaderno de deberes, fuera**, como pediste: tus apuntes van en «Tus notas» del review.
- **Tus imágenes de 腿** (la pierna que da pasos atrás, 退) **y de 肚** (月 «carne» + 土 «tierra»); 肚子 [HSK 3] espera en el desván.

El contraste 晚 / 万 ya existía desde el lote 006.

## Seguimiento

**Nivel.**
- HSK 1: 234 de 506 (46 %; en el lote 008, 44 %).
- Te faltan 171 palabras para el 80 %.

**Las clases.** No hubo clase nueva en este lote. Lo siguiente probable sigue siendo la hora.

**Tu método.**
- **Tu revisión de las tarjetas acertó en lo esencial.** Las de matiz no se podían puntuar. Las de sílabas sueltas no te dejaban comparar, y las pasabas con «fácil» sin saberlas.
- **El orden repartía mal la carga.** Daba primero bloques de dictados, y lo de decir llegaba semanas después.
- **En Anki, 458 repasos en 13 de los últimos 30 días**, con un 24 % de «Otra vez»:
  - leer, 14 %;
  - escuchar, 24 %;
  - decir, 64 %;
  - huecos, 25 %.
- **Retención de lo aprendido: 90 %**, justo la que pide el mazo.
- **Carga: unos 15 minutos y 15 nuevas por día de estudio.** La cola de tu nivel son unos 50 días con lo que entra en este lote.

**Consejo.** Las tarjetas de decir con hueco o situación son las que más te van a costar al principio, porque ahora llegan antes. Cuando falles una, di la respuesta entera dos veces en voz alta con el audio antes de pasar: así el «Otra vez» se convierte en práctica de verdad.
