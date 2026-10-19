<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 012-2026-10-19-querer-poder-y-matices

**Origen.**
- **Tus respuestas al review 011** y lo hablado en el chat del 16 (la última clase primero, oír solo en las frases de clase, la hoja de la familia).
- **«Tus notas» del review 011**: unas 1500 líneas. Tus mnemotecnias, contrastes que pedías, comentarios sobre cómo se ven las tarjetas y dos «exámenes» de 想 xiǎng, 觉得 juéde, 要 yào, 会 huì, 能 néng, 可以 kěyǐ y 得 děi que pegaste de tus consultas, además de un resumen de gramática del tiempo y de las formas de «todo».
- **Tu apunte del 18**: separar las frases en fórmulas y ejemplos.
- **Materiales de clase pendientes**: las copias «hechas» de los deberes del 13 y del 15, el material de una clase de prueba que no llegaste a hacer y los dos libros del curso (solo su índice).
- **En el chat, al empezar**: los exámenes entran filtrados a HSK 1-2, pasamos a 30 nuevas al día y el móvil estaba sincronizado.

En cifras: 338 tarjetas nuevas y 232 retiradas (231 de oír y una con nombres que no querías); 73 entradas (55 palabras, 3 expresiones, 1 componente y 14 grupos) y 106 frases.

## Cambios en el sistema

- **La última clase, delante.** Lo de la clase más reciente sale primero; detrás, lo atrasado, de la primera clase a la última. Lo que no es de clase pero va muy ligado a una clase sale con ella (`source.with_class`): este lote, los pesos con la clase del 15. Vive en `docs/goal.md`, `docs/design.md` («Niveles») y `anki.py` (`new_card_order`, `class_date`).
- **Oír una frase para decir, solo si es de clase.** Se quitaron 231 tarjetas de oír sin ningún repaso. Las 10 que tenían alguno en el historial se quedan con `listen: true` hasta que digas: 你好吗？, 我很好，你呢？, 欢迎你！, 你怎么样？, 去哪里啊？, 最近忙吗？, 这个怎么样？, 我最近很忙。, 请问，你叫什么名字？ y 我是工程师。. Vive en `docs/goal.md` («Las de oír, retos»), `docs/design.md` («Cobertura») y `anki.py` (`required_cards`).
- **30 nuevas al día** (`STUDY_PACE`). Se vuelve a 20 si los repasos pasan de una hora o el «Otra vez», del 30 %. Vive en `docs/owner.md`.
- **`push` no sube sin tu «ya»**: se niega sin `--phone-synced`. Y `--prune` ya no borra una tarjeta con repasos reales en el historial aunque parezca nueva. Vive en `docs/owner.md`, `docs/design.md` («Anki», «Garantías») y `anki.py` (`cmd_push`, `orphans`).
- **Recuperadas 33 tarjetas** que habías aprendido en el móvil entre el 29 de septiembre y el 8 de octubre y que habían vuelto a nuevas: vuelven como repasos para hoy, y FSRS recalcula con su historial. Otras 66 solo habían pasado los pasos de minutos y siguen como nuevas.
- **El reverso, en orden**: los bloques salen siempre en el mismo orden (en clase, tu mnemotecnia, cómo suena, notas; el porqué del carácter junto a «Sus caracteres»). La mnemotecnia dice de qué hanzi es y tiene color e icono propios. Las notas de una misma entrada van juntas, con «Palabra a palabra» delante (60 entradas tenían dos «Nota»). Tus mnemotecnias salen también en las frases y en las palabras que llevan ese hanzi. Las tarjetas de matiz traen una fila por palabra con su audio.
- **Una franja del día dibujada** para 早上 zǎoshang, 上午 shàngwǔ, 中午 zhōngwǔ, 下午 xiàwǔ y 晚上 wǎnshang (`timeline` en un grupo).
- **`check` caza las comas que rompían los datos**: `{meaning: hē, beber.}` perdía «beber». Pasaba en 16 sitios, entre ellos las 6 tarjetas de vocales (por eso no decían qué significaba la palabra), 4 de 点 diǎn, 英国 Yīngguó y 电视 diànshì.
- **Fórmula o ejemplo**: el campo `kind` está diseñado y la exportación ya lo lleva (vacío). La clasificación va propuesta en el review; se aplica en el lote 013.
- **Los deberes son material**: no se esperan hechos ni se piden (lo dijiste al preguntarte por los del 13).
- `docs/decisions.md`, siete entradas del 2026-10-19; `docs/hypotheses.md`, dos hipótesis nuevas (tus mnemotecnias en todas partes, la franja dibujada) y notas en tres.

## Tus respuestas al review 011

- **Orden de clases** («las cards de clase siempre por delante… y lo de la 6, dejarlo antes, ya está bien»): aplicado. Lo de la lección 1-2 que se preparó el 6 sigue saliendo con esa fecha.
- **Oír solo en clase** («sí, hazlo»): aplicado, ver arriba.
- **La hoja de la familia** («era de clase»): ya estaba como clase.
- **ü tras j, q, x**: tu resumen es correcto (xu siempre es ü; shu, nunca).
- **Números** («más claro y automático 万 wàn, 千 qiān, 百 bǎi, 十 shí… y el tono de cada número»): 8 números grandes como frases (oír y escribir las cifras; ver las cifras y decirlo), entre ellos 106 234 (el de tus deberes), y dos tarjetas de tonos: del uno al diez y 百 千 万 亿 零 两.
- **La edad según a quién**: sin cambios; ya estaba.
- **觉得 frente a 想** («hace falta meterla»; «想 es querer o tener pensado»): 想 se glosa ahora «querer o tener pensado (hacer algo); pensar», y 打算 dǎsuàn, para no chocar, «planear, tener previsto». Entran dos huecos «¿觉得 o 想?» y un matiz de los tres usos de 想.
- **¿觉得 es como 怎么样?**: respuesta en el review.
- **左右 y los kilos** («IMPORTANTÍSIMO»): la familia de los pesos entera, ver abajo.
- **买 y 商店** («tienda, centro comercial… estas son las importantes»): entra 商场 shāngchǎng «centro comercial».
- **他 / 她 / 它** («good»): sigue en observación.
- **«Falta hablar de corrido… no sabría qué decir»**: en el review, con 5 tarjetas de construir nuevas.
- **Pinyin en los reviews** («como norma»): en `docs/goal.md` y en este review.

## Tus notas, en sus tarjetas

- **Tus mnemotecnias**, con tu texto en `original`: 脚 jiǎo (ampliada: 去 «irse» y 卩, alguien arrodillado), 哪 nǎ, 爸 bà (dos martillos y media puerta), 吧 ba (boca y media puerta), 走 zǒu (como 是, pero balanceando los brazos), 呢 ne (alguien sentado bajo un techo), 帮 bāng, 错 cuò (la campana del concurso), 茶 chá, 校 xiào de 学校, 喝 hē (tu segunda versión) y 嗯 èn.
- **Contrastes que pedías**: 吧 / 呢 (por la forma), 休息 xiūxi / 学习 xuéxí y 真的 zhēnde / 正在 zhèngzài (por el sonido), 青 qīng / 请 qǐng y 讠 / 辶 (por la pieza), y 喝 / 渴 (por la izquierda). Además, 你们都是哪国人？ nǐmen dōu shì nǎ guó rén?, con 哪 y 都 a la vez, en el reverso de su contraste.
- **El hueco de 姚明和科比** (nombres que no querías): sustituido por el mismo con 爸爸和妈妈.
- **我的错 wǒ de cuò**: una sola nota, que dice que «mi error» es como se dice «culpa mía».
- **早上 / 明天**: con la franja dibujada, audio en cada palabra y sin la nota repetida de 早上.
- **La tarjeta de vocales sin significado**: arreglada en las seis.
- **什么时候 / 几月几号 / 几点**: un matiz con los tres.
- **都对了 / 一切都很好**, **我都喜欢 / 我什么都喜欢** y **知道 / 明白** (我知道，但是我不明白): tres matices.
- **Del vídeo de expresiones**: 哈喽 hālou y 嗨 hāi (oír), 马马虎虎 mǎmǎhūhū (oír), 最近还好吗？, 我没错。 y, ya en el mazo, 不好意思 y 我的错. **❌ 不咋滴**: habla del noreste, no estándar; se dice 不怎么样.
- **De los comentarios de redes**: 别说话！, 应该是。, 嗯嗯 (nota en 嗯) y 他明年回国。 (oír).
- **是男的还是女的？**: entra con 还是 háishi «o», HSK 1 que faltaba.
- **问题 y 关系**: 有问题吗？; 关系 guānxi, para oír, con 这跟你没关系 y 我们关系很好.
- **El 再 de 再见**: respuesta en el review.

## Palabras y frases nuevas

- **De tus exámenes, filtrados a HSK 1-2**: 生病 shēngbìng, 常常 chángcháng, 已经 yǐjīng, 快要 kuàiyào, 马上 mǎshàng, 刚 gāng, 打算 dǎsuàn, 完 wán, 必须 bìxū, 聊天 liáotiān (nivel 2 estimado), 应该 yīnggāi, 每 měi (HSK 3, para decir: 每天), 说话 shuōhuà; para oír, 一切 yíqiè, 全部 quánbù, 留 liú y 回国 huíguó. Unas 40 frases: 我喜欢吃汉堡 / 我想吃汉堡 / 我要一个汉堡; 我会游泳 / 我今天不能游泳 / 我可以游泳吗？; 我明天得工作; 我以前不会游泳，但是现在会了; 我要睡觉了，但是我还想跟你聊天…
- **Huecos de modales**: 会 / 能 / 可以 con 开车 kāichē (sé conducir / hoy no puedo / ¿me dejas?): con 游泳 yóuyǒng (HSK 3) la frase era de más nivel que la palabra. Y 得 / 想 (obligación frente a ganas).
- **Los pesos**: 斤 jīn y 公斤 gōngjīn pasan a decir; entran 克 kè «gramo», 千克 qiānkè (el kilo de las etiquetas) y 两 liǎng como peso (50 g), en un recuadro de menor a mayor. Frases: 一斤苹果多少钱？, 我要两斤, 一公斤是两斤, 一斤是五百克, 这个有两公斤左右.
- **HSK 1 por frecuencia** (propuesta del agente, `origin: gaps`): 这些, 那些, 一样, 重要, 告诉, 地方, 最后, 住, 准备, 别人, 路, 穿, 记得, 介绍, 电脑, 上班, 忘记, 最好, 见面, 还有, 不用, 没什么 y 一半, cada una con su frase.
- **Construir**: cinco escenas nuevas (la fiesta y la edad, el mercado, la comida rápida, la invitación de hoy que no puedes y el chat de madrugada).
- **Material de la clase de prueba** (no la hiciste: entra como material, por nivel): 汉语 Hànyǔ, 开 kāi, 雨 yǔ, y para oír 德国 Déguó y 巴西 Bāxī; frases 你是谁？, 你有猫吗？, 我在学习汉语。, 请开门。.
- **Fichas de hanzi**: 39 caracteres nuevos con su porqué en `3-data/hanzi.yaml`. Donde la fuente abierta no daba el origen y solo había memoria, quedan como discutidos: sin historia, solo la imagen (已, 巴, 必, 介, 告, 方, 脑, 备, 重).

## Contrastes nuevos

- **Solo los separa el tono**: 还 hái / 嗨 hāi, 鱼 yú / 雨 yǔ, 晚 wǎn / 完 wán / 万 wàn, 没 méi / 每 měi, 六 liù / 留 liú, 住 zhù / 猪 zhū, 穿 chuān / 船 chuán; y 克 kè entra en el grupo de 渴 kě y 棵 kē. `check` exige agrupar lo que suena igual sin tonos, y son justo lo que más te cuesta.
- **Los que pediste**: ver «Tus notas».

## Material de clase

- **Deberes del 13, copia «hecha»**: está en blanco, idéntica a la que ya se procesó en el lote 011. Nada nuevo que sacar.
- **Corrección del lote 011**: en el ejercicio 三 de esos deberes, 汉堡 hànbǎo, 沙发 shāfā, 麦克风 màikèfēng, 香槟 xiāngbīn y 巧克力 qiǎokèlì salen con su significado (unir dibujo y palabra), no solo para oír cómo suenan. 麦克风 sale del desván y entra para oír; 香槟 se había descartado como nombre propio y no lo es: entra para oír.
- **Deberes del 15, copia hecha** (la guardaste durante el lote): en la elección múltiple, 请问，您多大___？ con 岁 en vez de 年纪; lo demás, bien (是, 年轻, 哪, 对); la 6 y la de unir, sin hacer. La página de oír (iniciales, finales y tonos) no se puede corregir sin el audio. 您多大年纪了？ pasa de oír a decir, y va a «Para entender».
- **Libros del curso**: las diapositivas siguen *Tones & Conversation*, unidades 1 y 2; la lección 1-3 será su unidad 3 (nacionalidad y ciudad natal), que coincide más o menos con la lección 3 del libro de HSK 1.

## Del desván

- **门票 ménpiào «entrada»** despertó porque el HSK 1 pasa del 60 %: entra para decir, con tu nota sobre 门 y 门票多少钱？.
- **Siguen esperando, con motivo**: 完蛋 (muy coloquial, HSK 7), 终于 y 小区 (palabras de ejercicios de pinyin), 出生地 (de formularios), y 决定 y 总是, que entraron hoy al filtrar tu examen.
- **Entran al desván**: 决定, 总是, 从来, 不再, 一天到晚 y 尝尝, de tus exámenes; 西瓜, 双, 美女 y 滑, de la lista de pinyin de la clase de prueba. 确定 ya esperaba: se amplían sus notas.

## No entró, y por qué

- **❌ 不咋滴**: regional.
- **De los exámenes, las frases de HSK 3 en adelante** (probar el café con 尝尝, 我从来没想过…, 我已经决定…): esperan, con sus palabras, en el desván.
- **一会儿**: lleva erhua, que el mazo no enseña.
- **De la clase de prueba**: el vocabulario de aula y la lista de sílabas.

## Reorganización

- **Compras pasa de 60 entradas** (65): se divide en el lote 013, junto con la separación de fórmulas y ejemplos, para que las tarjetas cambien de subdeck una sola vez (`keep` en `themes.yaml`).
- **想 y 打算**: glosas reescritas, ver arriba. Las tarjetas conservan su progreso: cambia el texto, no lo que preguntan.
- **Las frases de trabajo** estrenan archivo (`3-data/sentences/trabajo.yaml`).

## Mantenimiento y retrospectiva

- **Mantenimiento de Anki**: en el review (borrar los audios sin usar).
- **Retrospectiva** de los lotes 008 a 011 y de este: en el review. Lo que más se repite es escribir datos a mano con scripts de un solo uso (comillas, frases repetidas, archivos que no existen), y las pruebas, que ya tardan más de diez minutos.

## Fricciones del proceso

- **Una tarjeta estudiada hoy en el móvil no se veía** hasta que el móvil sincronizó: al comprobar la de 姚明 parecía sin repasos, y al subir, la protección nueva de `--prune` la encontró en el historial y no la borró. Se borró a mano, porque pediste quitarla y ya tiene sustituta (un repaso de hoy).
- **La cuenta de las tarjetas de oír se rehízo**: la primera salía de 241 con 2 estudiadas, mirando solo el estado en Anki; una tarjeta que había perdido su progreso parecía nueva. Al cruzarla con el historial salieron 10 con repasos. Ahora `--prune` mira el historial.
- **La regla nueva de `check` se quedó corta a la primera**: buscaba espacios o puntos en la clave perdida y no vio `{es: Reino Unido, Inglaterra, …}`. Ahora vale cualquier clave vacía, salvo las tres de `hanzi.yaml` que lo son a propósito.
- **Huecos de nivel superior otra vez** (como en el lote 009): los de 游泳 yóuyǒng y 汉堡 hànbǎo se rehicieron con 开车 y con frases de HSK 1.
- **Los números como palabras sueltas** chocaban con la regla de teclear la respuesta: pasaron a frases.
- **Escritura de datos**: un id repetido (w.mei, w.zhu, w.chuan ya existían), un apóstrofo en inglés que rompió el YAML, un archivo de frases que no existía (el generador se paró a medias) y una frase que ya existía (我要走了). Los scripts de este lote comprueban ids y textos repetidos antes de escribir.
- **Las pruebas tardan más de 10 minutos** (626 s), frente a unos 3,5 al principio.
- **Fichas de hanzi**: el borrador nombraba una pieza de sonido (de 应) que no está en la fuente abierta; se reescribió sin ella.

## Seguimiento

**Nivel.**
- HSK 1: 310 de 506 (61,3 %; en el lote 011, 54,7 %). Te faltan 95 palabras para el 80 %.
- El salto es mayor que en el 011 porque entran 23 palabras de HSK 1 por frecuencia y varias de tus exámenes.

**Las clases.**
- Esta semana no hubo materiales nuevos: lo último son las clases del 13 y del 15 (edad y zodiaco), ya procesadas. Lo siguiente es la unidad 3 del libro de conversación: nacionalidad y ciudad natal, que encaja con lo que ya sabes (哪国人, 来自, 住在).

**Tu método.**
- Has estudiado 13 de los últimos 14 días, unos 18 minutos cada uno (en el 011, 9 de 14): la constancia ha dado un salto.
- Tus notas se han convertido en tu forma de investigar: preguntas a un asistente, pegas lo que te convence y lo comentas. Rinde mucho cuando pegas contrastes (想 / 觉得, 会 / 能 / 可以) y poco cuando son listas largas de un nivel que aún no tienes.
- En Anki: 21 % de «Otra vez», 79 % de retención; los tonos fallan un 55 % y decir, un 43 %.

**Consejo.** Con 30 nuevas al día, mira cada domingo el tiempo de repaso: si pasa de una hora, volvemos a 20.

**Avisos.**
- Antes de estudiar, sincroniza el móvil: este lote movió y borró tarjetas.
- 10 tarjetas de oír se quedan esperando tu decisión (ver el review).
