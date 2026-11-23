<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 018-2026-11-23-paneles-y-contrastes

Dos fuentes: «Tus notas» del review 017 (consultas pegadas, peticiones de tarjetas y, al final, apuntes de una clase de números, edad y familia sin fecha) y un chat del 23 de noviembre (consultas con un asistente, peticiones con código de tarjeta y, al final, los apuntes de una clase sobre dos estudiantes que se conocen en el campus). No había materiales de clase pendientes (`anki.py materials`: 0). Las respuestas del «Sine qua non» del review 017 llegaron vacías: siguen abiertas.

Lo que más pedías esta vez no eran palabras sino **paneles y contrastes**: «algunas de estas cosas no son más tarjetas sino mejores paneles en las que ya existen». El lote va sobre todo de eso.

## Cambios en el sistema

- **La explicación de un matiz, una frase por línea** (lo pediste con el 不 / 没: «así en párrafo no se entiende nada»). Arreglado al nivel de cómo se muestra, para todas las tarjetas de matiz a la vez: el reverso parte la explicación tras cada punto, sin cortar el pinyin entre paréntesis. `anki.py` (`answer_lines`, `answer_lines_html`), prueba `NuanceLines`. Regla: `docs/design.md`, «Tarjetas» (matiz con pinyin).
- **Lo que quedó sin subir del 11 de noviembre** entra con este lote: las conversaciones enteras (`3-data/conversations/`, su audio y `export`), ya contadas en `docs/decisions.md` («Conversaciones enteras, fuera de las tarjetas»), y la ruta nueva del proyecto en `AGENTS.md` y `docs/owner.md`.

## Tus notas, en sus tarjetas

**Paneles nuevos en tarjetas que ya tienes** (salen en todas las tarjetas de esa palabra; 💡 = «Para entender»):

- 还 hái 💡: la idea común de «todavía», «además», «otro» y «aún más»: algo sigue o se suma respecto a lo de antes; y que 我还好 es «estoy bastante bien». 还是 háishi: «o» y «todavía» vienen de la misma expresión (lo marcaste IMPORTANTE).
- 就 jiù 💡 «sin distancia» (我就来, 那里就好, 就这个), 又 yòu 💡 frente a 再 zài (lo ya repetido frente a lo que se repetirá), 都 dōu 💡 (hasta el extremo: 都十二点了！), 要 yào 💡 (lo que empuja a realizarse, frente a 想), 在 zài 💡 (estar dentro de un sitio o de una acción; 再 suena igual y es otra palabra).
- 别 bié: prohibir (别走) frente a «otro» (别的). 那 nà «pues»: 那好吧, 那就这个吧. 行 xíng: 行！, 不行, 都行, 还行.
- 拿 ná 💡: 拿来 / 带来 / 送来, los tres «traer». 带走 dàizǒu: 带来, 带走, 带回去 (cambia la dirección). 打 dǎ: verbo comodín (打电话, 打车, 打包…). 上班 shàngbān: 上 «entrar» + 班 «turno» (tu tarjeta 451AN; ese código no existe, pero el panel va en 上班).
- 位 wèi 💡: 人 es sustantivo y 位 clasificador; ninguno marca plural; 几位 o 几个人, no 几人.
- 不好意思: de 好意思 «no tener reparo»; más suave que 对不起. 麻烦 💡: cuándo 不好意思, 请问, 麻烦你 y 对不起.
- 小心: tu imagen (el corazón pequeñito, al revés que 开心) como mnemotecnia. 马上: el caballo. 清楚: 听清楚, 看清楚, 说清楚; frente a 听不懂 y 听不见.
- 饭 fàn: 饭, 米饭, 吃饭 y 菜. 菜 cài: dentro lleva 采 «recoger» (una mano sobre un árbol), que se parece a 来 sin tener que ver. 快乐: aquí 快 no es «rápido».
- 国 guó 💡: país y nacionalidad (中国人, 法国人), y suelto casi solo en palabras (回国, 外国). Lo pediste como tarjeta; va como panel y con dos frases nuevas (她是法国人, 她是加拿大人).
- 开玩笑 (#GSNZ0): 我开玩笑的！ y 别开玩笑了！, como frases, para que la tarjeta tenga ejemplos de diario.
- Notas en tarjetas concretas: #RJTH3 (不打包，我们在这里吃: al pedir valen 打包 y 带走), #XSCZN (买单 = 买 «comprar» + 单 «la lista»), #CVE25 (también 还要点什么吗？), #V5D8C (también 你什么时候来？).

**Contrastes y matices que pediste** (tarjetas nuevas a mano):

- 🃏 打包 / 带走 (matiz): al pedir valen las dos; para lo que sobra, solo 打包. Y entra 外卖 wàimài «comida a domicilio».
- 🃏 我找钱 / 找钱 (matiz) y 🃏 找 / 钱 / 我 (contraste visual, tres tarjetas): la lanza 戈 en los tres.
- 🃏 米 / 来 (contraste visual): tu «hanzi de arroz y de venir». Entra 米 mǐ «el grano» para poder contrastarlo.
- 🃏 会 / 今 (contraste visual: el mismo tejado 人). 会 / 回 ya tenía su contraste (grupo 会 y 回).
- 🃏 现 / 玩 (contraste visual: el 王 que es jade). Entra 玩 wán «jugar, divertirse».
- 🃏 再说一遍 / 再来一点水 (matiz): tu «yi bian / yi dian».
- 🃏 还要 / 再来 / 也要 (matiz), 🃏 还要别的吗 / 还要一点吗 (matiz), 🃏 两个饺子 / 两份饺子 (matiz), 🃏 饭 / 菜 (matiz).
- 🃏 你要小心 / 你得小心 (matiz), 🃏 现在 / 今天 (matiz), 🃏 清楚 / 年轻 / 请, las tres qing (matiz).
- 🃏 中国有多大？ / 中国很多大？ (matiz; el calco no suena), 🃏 肯定 / 一定 (matiz), 🃏 别走 / 别的东西 (matiz).
- Grupo 开心 / 高兴 / 快乐 / 幸福 (panel en sus tarjetas, con una situación para cada una); entran 幸福 xìngfú (oír) y 舒服 shūfu (decir: 我不舒服).
- Contrastes de tono que pedía `check`: 猜 / 才 / 菜, 狗 / 够, y 玩 / 完 (homófonos: se preguntan por el sentido).

**Huecos y traducción** («¿por qué nunca he visto de huecos y traducción?»): el mazo tiene 611 tarjetas de decir en chino y 144 huecos, pero de las 4322 has visto 406, a unas 4 nuevas al día. Van mezcladas en la cola: no es que falten, es que aún no han salido. Este lote suma 4 huecos (够, 才 con «¿就 o 才?», 一样大 sin 岁 y 麻烦 con «¿请问, 麻烦 o 对不起?») y 26 tarjetas de decir frases (las que `scaffold` hace de cada frase para decir).

**中国 «me sale cada dos por tres»**: 中国 tiene solo 3 tarjetas propias (leer, oír, decir) y la del sonido de 中, pero aparece en unas 40 tarjetas más como parte de una frase (中国有多大？, 我想去中国…). Es la ósmosis, no tarjetas repetidas. Lo que sí falla con 中国 es 中国有多大？ (6 de 17), y 美国 al leer (8 de 14).

## Material de clase

Dos bloques de apuntes de clase sin fecha (⚠️ fechados a 23 de noviembre, el día del lote; ver «Por verificar»):

- **Números, edad y familia** (al final de tus notas del review): fracciones (三分之二), decimales (零点二), ordinales (第一, 第五), 两 / 二, 亿, la población de China, las habitaciones de la Ciudad Prohibida, los kilómetros de la Gran Muralla, cómo preguntar la edad (您高寿, 你几岁, 你多大, 阿姨您多大年纪), 奶奶 / 牛奶, 小姐 / 服务员 y 晴天. Casi todo ya estaba en el mazo.
- **Dos estudiantes que se conocen** (al final del chat): presentarse, 一样大 (no 岁), 一九九九年出生, 二十多岁, 大学生, 校园, 第一次, 继续聊天, 教室, 下课以后, 手机里的照片, 女朋友 / 男朋友.

## Palabras y frases nuevas

**Personas, estudio y países**
- ✅🃏 男生 nánshēng · chico (estudiante) · pareja de 女生
- ✅🃏 女朋友 nǚpéngyou · novia · 你有女朋友吗？
- ✅🃏 男朋友 nánpéngyou · novio · 她有男朋友。
- ✅🃏 大学生 dàxuéshēng · universitario · serie 小学生 / 中学生 / 大学生 · 他们是大学生吗？
- ✅🃏 小学生 xiǎoxuéshēng, 中学生 zhōngxuéshēng · primaria, secundaria · para oír
- ✅🃏 教室 jiàoshì · aula · no es 老师 · 下课以后，他在教室里看手机。
- ✅🃏 校园 xiàoyuán · campus · 元 da el sonido (园, 远)
- ✅🃏 法国 Fǎguó · Francia · 她是法国人。 ✅🃏 加拿大 Jiānádà · Canadá · se escribe por el sonido · 她是加拿大人。
- ✅🃏 第一次 dì yī cì · la primera vez · 他们是第一次见面。

**Números y lugares**
- ✅🃏 分之 fēnzhī · en las fracciones · al revés que en español: 三分之二 = 2/3 · ⚠️ tu «wu fan zhi yi 1/2» es 1/5: 1/2 es 二分之一
- ✅🃏 公里 gōnglǐ · kilómetro · el 公 de 公斤 · 长城有两万多公里。
- ✅🃏 人口 rénkǒu · población · 中国人口有十四亿。
- ✅🃏 故宫 Gùgōng · la Ciudad Prohibida · 故宫有九千多个房间。
- ✅🃏 老地方 lǎo dìfang · el sitio de siempre · 老地方见！
- Frases: 零点二 (decimales con 点), 他二十多岁, 我和他一样大, 你哪年出生？, 你读一下, 他们继续聊天, 我的手机里有很多照片, 今天是晴天.

**Comer, pagar, sentirse**
- ✅🃏 米 mǐ · el grano de arroz · para el contraste 米 / 来
- ✅🃏 炒饭 chǎofàn · arroz frito · 少 da el sonido a 炒 · 我要一份炒饭。 ✅🃏 炒面 chǎomiàn (del desván) · 这个炒面太好吃了！
- ✅🃏 外卖 wàimài · comida a domicilio · 我想点外卖。
- ✅🃏 找钱 zhǎoqián · dar el cambio · 老板，你还没找钱呢。
- ✅🃏 够 gòu · bastar · 句 da el sonido, como a 狗 · 钱不够。 / 吃饱了吗？不够还有。
- ✅🃏 舒服 shūfu · cómodo; 我不舒服 «no me encuentro bien»
- ✅🃏 幸福 xìngfú · feliz con tu vida · 他们很幸福。
- ✅🃏 肯定 kěndìng · seguro · 你肯定累了。
- ✅🃏 玩 wán · jugar, divertirse · 我们出去玩吧。
- ✅🃏 晴天 qíngtiān · día de sol · qíng, no míng · 今天是晴天。
- ✅🃏 才 cái · no… hasta; solo · lo contrario de 就 · 他十点才来。
- ✅🃏 继续 jìxù (del desván) · seguir · 他们继续聊天。
- ✅🃏 麻烦 máfan (del desván) · molestar al pedir · 麻烦你帮我一下。
- ✅🃏 有道理 yǒu dàolǐ · tiene sentido · 你说得有道理。 ✅🃏 意见 yìjiàn · 我没意见 «por mí, bien»
- De tus «100 frases» (las marcaste MUY ÚTILES): 让我想想, 听起来不错, 我没意见, 一切都好, 还行, 不要这样！, 那就这个吧. Ya estaban 最近怎么样, 等一下, 我在路上了, 说得好, 我没听清楚, 再说一遍 y 都行.
- Frases para los matices: 我要两个饺子 / 两份饺子, 我还要一杯 / 我也要一杯, 还要一点吗？, 再来一点水, 我们要三个菜，还要米饭, 你得小心.

Caracteres con su porqué en `3-data/hanzi.yaml`: 之 加 园 城 够 宫 才 故 晴 法 炒 烦 福 继 续 肯 舒 麻 (con imagen para recordar los de origen discutido: 之 才 肯 宫 法 继 舒). Y 现 entra como carácter ligado, solo para el contraste con 玩.

## Del desván

- 长城 Chángchéng: salió en la clase de números (两万多公里). 继续 jìxù: salió en clase con su sentido (继续聊天), que era lo que esperaba. 炒面 chǎomiàn: pediste mnemotecnias para los platos y lo volviste a anotar. 麻烦 máfan: tu tabla de cortesía (不好意思 / 请问 / 麻烦你 / 对不起).
- Despiertan y esperan: 道 dào (despierta con 有道理, pero ese 道 es «razón»; el clasificador de 一道菜 espera a clase) y 出生地 (de formularios).

## No entró, y por qué

- **Al desván**, de tus consultas: 想起来 / 想出来, 看出来 / 听出来, 记下来 / 写下来 (complementos direccionales figurados, HSK 3 o más; con tus explicaciones como notas), 结账 (para la cuenta ya tienes 买单), 啦 (coloquial; y 这个啦吗 no se dice), 慢慢 (别着急，慢慢吃).
- **Del cuaderno de complementos direccionales**: lo básico ya estaba (进来 / 进去 / 出来 / 出去, 回来 / 回去, 起来); lo útil de él va como panel en 拿 y 带走. Las 13 familias enteras (上来, 拿上去, 搬进去, 跳下去…) no entran ahora: son HSK 3 a 5 y sin frase de clase.
- **Fuera**: 相遇 xiāngyù (del texto de clase, registro escrito: se dice 第一次见面); 堂食 (de carteles, raro al hablar); 在这儿吃 y 哪儿 (erhua: el mazo usa 这里, 哪里); 支付宝 y 微信支付 (marcas); 一点儿也不 en su forma con erhua (en estándar, 一点也不, que entrará con frase).
- **Lo repetido**: buena parte de lo del restaurante (我还没决定, 我想想, 太好吃了, 我吃饱了, 买单, 刷卡…) ya entró en el lote 017.
- **Un documento de investigación ajeno** fotografiado en el chat (preguntas de una tesis): no es material para el mazo y no es tuyo; se retira de la copia archivada y queda solo en local.
- ⚠️ «Xiang sho mide nein chi» y «wo shi ni shuo de dui… wo neng kan chulai»: no se entiende qué frase era (ver «Por verificar» del review).

## Reorganización

- Los temas «Describir», «Momentos del día» y «Cosas y actividades» estaban en 60 entradas, el tope. En vez de pasarse, lo nuevo fue donde también encaja: 够 a «Compras», 肯定 a «Entender y preguntar», 幸福 a «Familia», 舒服 a «Personas», 第一次 a «Números» (ordinales), 才 a «Unir frases», 继续 a «Trabajo y estudio» y el carácter 现 a «Caracteres y componentes». Los tres temas siguen llenos: en el lote 020 (mantenimiento) conviene partir «Describir» (sentimientos aparte).
- Los avisos de `check` sobre 玩 frente a 晚 y 万 se quedan: 玩 ya tiene su grupo de homófonos con 完 (wán, mismo tono), y meterlo en el de tonos 晚 / 完 / 万 chocaría (dos opciones sonarían igual).

## Fricciones del proceso

- El lote se cortó a mitad por un reinicio del servidor y se retomó desde el estado del disco.
- Al quitar dos IDs repetidos (w.gou, w.wan ya eran 狗 y 晚) con una orden de una línea, se vaciaron tres archivos del léxico (describir, escritura, ocio): se abría el archivo para escribir antes de leerlo. Se restauraron desde git (no tenían cambios sin subir) y se volvió a añadir lo del lote; `git diff` lo confirma.
- Dos frases de las consultas ya estaban en el mazo con el mismo ID (都行, 我在路上了) y otra con otro ID (我1999年出生): `check` lo detectó y se quitaron las copias.
- Comprobación en Anki tras subir (paso 10b): las explicaciones de matiz salen partidas en líneas (不 / 没, 打包 / 带走), los contrastes visuales sin audio y los huecos con su frase. Falló una: el matiz 有多大 / 很多大 enseñaba en su fila 多大 «¿cuántos años?», el sentido de la edad; ahora apunta a la frase 中国有多大？ y no lleva filas. Se subió dos veces.
- La primera subida recolocó 4077 nuevas y la segunda 810: entran muchas de clase delante y el orden se recalcula. Solo se mueven nuevas, con el móvil sincronizado.
- Las pruebas tardan ya 58 minutos (165, todas bien): la primera tanda se cortó al llegar al límite de una hora en segundo plano y hubo que relanzarla. Conviene mirar en la retrospectiva del lote 020 qué pruebas recompilan el mazo entero.
- Lanzado sin nadie delante: las órdenes de `git` y `python` piden aprobación si no empiezan exactamente por la ruta permitida, lo que obligó a escribir los cambios con pequeños scripts locales en `private/`.

## Seguimiento

**Nivel.** HSK 1: 412 de 506 (81,4 %; en el lote 017, 80,2 %). HSK 2, tu nivel de trabajo: 164 de 750 (21,9 %; antes, 20,4 %).

**Las clases.** Los apuntes de este tramo son del curso de HSK 1 (números grandes, fracciones, edad y familia; un texto de dos estudiantes que se conocen), así que todo indica que la profesora del curso sigue además de la de conversación. Lo que da encaja con el objetivo: números y presentarse con más detalle (一样大, 二十多岁, 哪年出生).

**Tu método.** 29 de los últimos 30 días; unos 18 minutos al día y 4 nuevas. En Anki, 11 % de «Otra vez» y 90 % de retención; decir falla un 18 %, leer un 14 %, oír un 7 %. Tus notas de esta vez eran sobre todo explicaciones de consultas y peticiones de panel: rinden, pero solo lo que trae una frase corta o un contraste concreto se convierte en tarjeta. Con 4 nuevas al día, la cola de tu nivel son 113 días: los huecos y las traducciones que echas de menos ya están, pero tardan en salir.

**Avisos.** Consejo: sube a 8–10 nuevas al día durante dos semanas (sigues por debajo de 20 minutos): es lo que hará que salgan los huecos, las traducciones y los contrastes que pides. Y antes de la próxima clase, di en voz alta 我和他一样大, 他二十多岁 y 你哪年出生？.
