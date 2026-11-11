<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 017-2026-11-11-pedir-en-el-restaurante

Lo procesado: la clase 2 con la profesora nueva (pedir en un restaurante, PDF del 9 de noviembre, anotado a mano), el review 016 con «Tus notas», un mensaje del chat (al principio del diálogo, «¿aquí o para llevar?») y las 20 de HSK 1 por frecuencia que el review 016 proponía. Prioridad, la que pidió YAGO: lo de conversación que necesita para la próxima clase, por delante del orden del HSK.

En cifras: 60 palabras nuevas (38 para decir, 18 para oír y 4 sentidos solo en frases), 2 caracteres, 10 grupos de contraste, 2 estructuras, 122 frases (89 para decir) y 343 tarjetas nuevas (de 3975 a 4318). Con ellas, **el HSK 1 pasa del 80 %: 406 de 506 (80,2 %)**, y el nivel de trabajo es ya el HSK 2.

## Cambios en el sistema

- **El complemento de orden de nuevas recibe el mazo de `anki.py`.** El 9 de noviembre YAGO movió el mazo en Anki a `🌐 Language::🀄 Chino práctico` y `DECK_NAME` se cambió, pero el complemento `tools/anki-order` llevaba escrito «🐉 Chino práctico» y en la primera subida de este lote rechazó las 3943 nuevas («not a new card of the deck»): el orden no se aplicó. Ahora `push` le manda el nombre del mazo en la petición, y el complemento solo acepta un mazo cuyo nombre acabe en «Chino práctico». Instalado en Anki (reiniciado con su propio «salir», ya sincronizado) y vuelto a subir: 3943 nuevas recolocadas. Dónde está: `docs/design.md`, «Anki» (orden de nuevas), `tools/anki-order/README.md`, `docs/decisions.md` (2026-11-11) y la prueba `NewCardOrderAddon`.
- **El nombre del mazo en la documentación**: `AGENTS.md`, `docs/design.md` y `README.md` decían `🐉 Chino práctico`; ahora «Chino práctico», en la ruta de `DECK_NAME`.
- El cambio de `DECK_NAME` y de `docs/owner.md` del día 9 (hecho fuera de un lote) entra en el commit de este lote.

## Material de clase

- **La profesora nueva.** La hoja del 6 era de ella: lo dice el apunte del 9 («mi profesora nueva desde el 06.11.2026»), y responde a la primera pregunta del review 016. Las dos hojas quedan en local, en la carpeta de materiales de clase (`slides/261106…` y `slides/261109…`), registradas como procesadas en los lotes 016 y 017. En nada versionado sale su nombre ni la plataforma.
- **Clase 1** (págs. 2-5 del PDF del 9): la misma hoja del 6, ya procesada en el lote 016. Nada nuevo.
- **Clase 2, 第二课, pedir en un restaurante** (págs. 6-8), ⚠️ fechada el 9 por el PDF (no dice el día de la clase):
  - Lista de palabras por grupos (carne, platos básicos, fruta, bebidas, «otros de pedir»), con pinyin anotado y subrayado en amarillo lo que marcó.
  - Tres rondas de pedir, 22 minutos corrigiendo sobre la marcha: un guion (几位？ / 这是菜单。你吃什么？ / 我要…，还要… / 多少钱？ / 我买单。可以打包吗？), una situación libre (un plato de carne, uno básico y una bebida, precio, pagar, para llevar; al menos 6 frases; vale preguntar 这个怎么说？) y preguntas para descolocar (你说什么？再说一遍。 / 你要鸡肉还是猪肉？ / 你要米饭还是面条？ / 茶还是水？ / 这个菜很好吃，你要不要？ / 要不要汤？ / 打包吗？).
  - Cambio de papeles: YAGO hace de camarero, con una chuleta (你好 / 几位 / 菜单 / 吃什么 / 鸡肉 猪肉 面条 米饭 汤 / 喝的 / 多少钱 / 买单 / 打包 / 谢谢).
  - Anotado a mano: 还要 = «también, y además»; 来 para pedir (来一个…); 美女 y 帅哥 para llamar a quien atiende; 下次再来; 我可以要…吗？; 我要 / 我想要; y en verde, 你没有看菜单, 你怎么知道你想吃什么？, 哪里 / 那里 / 这里.
- Todo lo de la clase 2 entró, para decir lo que se pide y lo que dice el camarero (YAGO hace los dos papeles), y para oír la fruta y lo menos común.

## Tus respuestas al review 016

- Todas las líneas «>» estaban vacías: nada cambia por ellas. Lo que sí responde algo vino por otro lado: la hoja del 6 es de la profesora nueva (apunte del 9).
- **El recuadro 💡 «Para entender»**: tercera vez sin respuesta; se da por bueno tal como está (lo anunciaba el review 016).
- **Tus apuntes de debajo de la hoja** (你能听懂我说的吗, 周末愉快, 他现在在美国): sin respuesta; siguen tratados como de clase.
- **Las 20 de HSK 1 por frecuencia**: sin respuesta, así que entran (lo anunciaba el review).
- **灰色**, **哦 / 得 děi**, el mantenimiento (borrar audios sin usar) y «Suenan parecido»: sin respuesta, se quedan como estaban.

## Tus notas, en sus tarjetas

«Tus notas» del review 016 traía tres partes: arriba, notas nuevas; en medio, un bloque ya archivado en el lote 016 (de 你能听懂我说的吗 a 9JDK4), que no se vuelve a meter; y abajo, notas nuevas otra vez. Lo nuevo:

- **Llegar y quedar**: 我到了！ wǒ dào le, 你到了吗？ nǐ dào le ma, 我在路上了 wǒ zài lùshang le (para decir), y en 刚 gāng la nota de 刚刚 gānggāng. 我刚到 ya estaba.
- **遍 biàn y 次 cì** («!!»): 遍 sube a decir, con 再说一遍 zài shuō yí biàn de la clase; frases 再听一遍 y, para oír, 我读了两遍 y 我去过北京两次. El matiz 次 / 遍 ya existía.
- **没问题 méi wèntí para aceptar una propuesta** (我选地方，你选时间，怎么样？ —没问题！): nota en 没问题.
- **好啊 hǎo a y 好的 hǎo de**, y **这里可以 y 这里很好** (tus «Contrastes»): una tarjeta de matiz cada uno. Que 很 a menudo no es «muy» ya lo decía su entrada.
- **想让 xiǎng ràng**: la estructura {S} + 想 + 让 + {N} + {V}, con 我想让你帮我 wǒ xiǎng ràng nǐ bāng wǒ para decir (la tarjeta que pedías: «Quiero que me ayudes») y el matiz 我想你 «te echo de menos» / 我想让你去.
- **里 lǐ, 早 zǎo y 果 guǒ** (tu «diferenciar el li de sitio, el zao de zaoshang y el de pingguo»): grupo visual, con 果 como carácter.
- **做饭 zuò fàn**: entra, con 我在做饭. 你在做什么？ ya estaba.
- **快 kuài y 决 jué**: tu imagen del corazón 忄 que late rápido ante una decisión 夬 va a 快 como mnemotecnia (inventada: 夬 da el sonido, como en 块, lo decía tu propia nota). Entran 快来！, 生日快乐！ y **决定 juédìng** (despierta del desván) con 我决定了, 你决定吧, 我还没决定. 解决 jiějué, al desván.
- **高兴 gāoxìng, 快乐 kuàilè y 开心 kāixīn** («OJO CONTRASTE IMPORTANTE», dos veces): 快乐 sube a decir, entra 开心, y una tarjeta de matiz con los tres; frases 跟你在一起很快乐 y 我很开心.
- **见到 jiàndào**: 我想再见到你 «quiero volver a verte» en vez de tu 我想再见你, que se puede leer como «quiero decirte adiós otra vez»; y 很高兴见到你.
- **可以请你喝咖啡吗？**, para decir.
- **Las formas de preguntar de dónde es alguien**: nota en 国家 de la más llana a la más educada. 你是哪个国家的人？ y 你从哪里来？ ya estaban; 你是哪儿人 queda fuera (solo mandarín estándar).
- **一只猫 y 小猫**: matiz (只 cuenta, 小 dice el tamaño), con 我有一只小猫 para oír y nota en 猫.
- **外 wài y el «wèi plural»**: ⚠️ leído como 位 wèi, el que cuenta personas (几位？, de la misma clase). Grupo de sonidos parecidos 外 / 位.
- **觉 jiào de 睡觉 y jué de 觉得**: tarjeta de matiz (un carácter, dos lecturas).
- **Descripción + 的 + cosa** («Importante»): la estructura ya existía; entra el matiz 你喜欢的人 / 喜欢你的人, con 喜欢你的人很多 (decir) y 我喜欢的人不喜欢我 (oír), y una nota en la estructura.
- **Tiendas y tamaños**: 哪个最便宜？, 这个是最便宜的吗？, 为什么这么贵？, 十块可以吗？, 我想要便宜一点的, 有大一点的吗？, 有小一点的吗？, 最小的多少钱？, 有白色的吗？, para decir; y la estructura **{Adj} + 一点 + 的** («uno un poco más…») con su calco 有一点大的吗？.
- **Hoteles y sitios**: 有房间吗？, 我想要一个安静的房间 (entra **安静 ānjìng**), 最便宜的房间多少钱？, 这里可以坐吗？.
- **Tus «frases importantes»**: 所以现在我是老师了, 我到家再看 (tu 我到家看, con el 再 que lo hace natural), 请给我五星！谢谢！ (entra **星 xīng**), 太谢谢你了 (ya estaba), 今天不要出去, 对，我想请你喝咖啡，但是今天不行了, 你今天要做什么？, 我去健身 (entra **健身 jiànshēn**, tu «!!!») y 我会在家附近喝咖啡 (entran **附近 fùjìn** y 会 «lo que va a pasar», solo en frases). Para oír, la larga de las cinco estrellas.
- **Los letreros de Shanghái**: **小吃 xiǎochī** (oír), **街 jiē** y **拍照 pāizhào** (decir), con 我喜欢吃火锅, 上海的街很漂亮, 这里可以拍照吗？ y 饭店在二楼.
- **Tu diálogo del restaurante**, lo que no repetía la clase (sale con la clase, `with_class`): 不好意思，可以给我菜单吗？, 菜单在这里，你们看一下 (sin 慢慢), 你们想好了吗？, 你们这里有什么好吃的？ (tu 这儿, en estándar), 我要一份饺子 (entra **份 fèn**), 不要辣 y 这个辣吗？ (entra **辣 là**), 不辣，放心吧 (entra **放心 fàngxīn**), 还要别的吗？, 对了，再来一杯水, 我没听清楚，你能再说一遍吗？, 那我要可乐, 这是什么肉？, 那这个呢？, 请慢用, 我吃饱了 (entra **饱 bǎo**), 怎么样？还满意吗？ (entra **满意 mǎnyì**), 不好意思，买单！, 好的，马上来, 一共多少钱？, 我请客！开玩笑的！ (entra **开玩笑 kāi wánxiào**), 可以刷卡吗？ (entra **刷卡 shuākǎ**), 慢走！.
- **Del chat**: al principio del diálogo, 在这里吃还是打包？ «¿para tomar aquí o para llevar?» y 不打包，谢谢，我们在这里吃 «para llevar no, gracias: comemos aquí». Están en la tarjeta de construir de pedir, en la de hacer de camarero y en el diálogo para oír.

## Palabras y frases nuevas

**En el restaurante** (tema nuevo): 菜单 càidān · carta 🃏 · 买单 mǎidān · ¡la cuenta!, pagar 🃏 · 位 wèi · cuenta personas con respeto (几位？两位) 🃏 · 打包 dǎbāo · para llevar 🃏 (del desván) · 一共 yígòng · en total 🃏 · 份 fèn · ración 🃏 · 刷卡 shuākǎ · pagar con tarjeta 🃏 · 美女 měinǚ y 帅哥 shuàigē · para llamar a quien atiende 🃏 (美女, del desván) · 满意 mǎnyì · satisfecho (oír) · 还 hái «además» (还要), 来 lái «póngame» (来一杯可乐) y 点 diǎn «pedir» (点菜): otros sentidos de caracteres que ya se leen y se oyen, solo en frases, como 那 «entonces».

**Comida**: 鸡肉 jīròu, 猪肉 zhūròu, 米饭 mǐfàn, 面条 miàntiáo, 饺子 jiǎozi, 汤 tāng, 辣 là, 饱 bǎo 🃏 (decir); 寿司 shòusī, 橙子 chéngzi, 草莓 cǎoméi, 蔬菜 shūcài, 豆腐 dòufu, 小吃 xiǎochī (oír).

**Orientarse** (tema nuevo): 东 dōng, 南 nán, 北 běi 🃏 (y 西 xī sube de leer a decir), con 边 biān «lado» (oír) detrás: 北京在中国的北边; 中间 zhōngjiān, 附近 fùjìn, 街 jiē 🃏; 地点 dìdiǎn (oír).

**HSK 1 por frecuencia** (las 20 del review 016): además de las de orientarse, 妹妹 mèimei, 老人 lǎorén, 干净 gānjìng, 记住 jìzhu, 考 kǎo, 网上 wǎngshàng 🃏 (decir); 工人 gōngrén, 毛 máo (dinero: 三块五毛), 页 yè, 车上 chēshang, 地上 dìshang, 学院 xuéyuàn, 动作 dòngzuò, 有时 yǒushí (oír: para decir ya está 有时候).

**Tus notas**: 开玩笑, 决定, 开心, 见到, 安静, 健身, 做饭, 星, 拍照 🃏 (decir); 放心 (oír).

**Tarjetas a mano**: dos de construir, **pedir en el restaurante** (#KW8SK: aquí o para llevar, lo que quieres con 还要, cuánto es) y **hacer de camarero** (#ASP4T); ocho de matiz (还 «todavía» / «además»; 高兴 / 快乐 / 开心; 好啊 / 好的; 这里可以 / 这里很好; 觉 en 睡觉 y 觉得; 一只猫 / 小猫; 你喜欢的人 / 喜欢你的人; 我想你 / 我想让你去); dos contrastes de caracteres (外, 果); un diálogo para oír (#X2K3F, de 几位 a 买单).

**Grupos**: nuevos, 外 / 位, 里 / 早 / 果, 东南西北, y seis de solo el tono (也 / 页, 包 / 饱, 猫 / 毛, 分 / 份, 杯 / 北, 遍 / 边, 洗 / 西); ampliados, 男 / 难 con 南, 懂 / 动 con 东, 姓 / 行 con 星.

**Notas en lo antiguo**: 遍 (再说一遍), 快 (tu mnemotecnia), 快乐 (los tres «contento»), 没问题 (aceptar una propuesta), 国家 (cómo preguntar de dónde es alguien), 刚 (刚刚), 服务员 (美女 y 帅哥), 猫 (一只猫 / 小猫), 到 (por mensaje: 我到了), la estructura de 的 (quién quiere a quién), 恭 (共 da el sonido) y conexiones de sonido en 饺, 汤, 饱, 草莓, 豆腐, 玩, 拍, 静.

**Caracteres nuevos con su porqué** (30): 份 位 健 共 决 净 刷 单 南 卡 妹 拍 条 橙 汤 满 玩 米 网 腐 草 莓 蔬 豆 辣 附 静 页 饱 饺; con imagen para recordar los de origen discutido (南, 刷, 单, 辣).

## Del desván

- **打包 dǎbāo**, **美女 měinǚ** y **决定 juédìng** despiertan: 打包 y 美女, por la clase del restaurante; 决定, por tus notas de 决 y tu diálogo (我还没决定).
- Cinco despiertan y se aplazan, con su motivo: 发票 fāpiào (con 买单; HSK 4, para pagar bastan 买单, 刷卡 y 扫码), 误会 wùhuì (con 会 «va a», otro sentido), 明星 míngxīng (con 星, sin frase), 打扫 dǎsǎo (con 干净, HSK 4 y sin frase), 厨师 chúshī (con 做饭, HSK 6).

## No entró, y por qué

- **Al desván** (del diálogo del restaurante y de tus notas, entraron y se aplazaron en el mismo lote): 推荐 tuījiàn (HSK 7 por la lista; de momento, 你们这里有什么好吃的？), 招牌菜, 受欢迎, 炒面, 小白菜, 宫保鸡丁, 位子 (con 几位 basta), 游行 (de tu «hoy hay protest»), 解决, 笑起来 (verbo + 起来 es HSK 3: 你笑起来真好看 espera) y 老字号; 正宗 va como nota a 地道, y 跑步过来 a 过来.
- **Fuera**: 不咋地 (del norte, coloquial: solo mandarín estándar), 我们AA吧 (lleva letras latinas; para pagar a medias, más adelante), 支付宝 (una marca), 渝 y 沪 (abreviaturas de ciudades), 主食 y 饮品 (títulos de la lista, no se dicen), 喝的 (va dentro de 要喝的吗 cuando haga falta).
- **Lo repetido**: el bloque de en medio de «Tus notas» (ya entró en el lote 016) y siete frases que ya estaban (我刚到, 我太高兴了, 你是哪个国家的人？, 你从哪里来？, 我没错, 这是我买的书, 太谢谢你了).

## Reorganización

- **Tema nuevo, «En el restaurante»** (tras «Comida»): todo lo de pedir. «Comida» se queda con los platos y la fruta; con todo junto pasaba de 60.
- **Tema nuevo, «Orientarse»** (tras «Lugares»): 东, 南, 北, 中间, 附近, 街, 地点 y el grupo de los cuatro puntos; «Lugares» pasaba de 60. 西 se queda en «Lugares» con sus tarjetas, en el grupo de los cuatro.
- **Usos**: suben 遍 y 快乐 (de oír a decir) y 西 (de leer a decir). 有时 queda para oír (para decir, 有时候).
- Los subdecks se renumeran por los dos temas nuevos; las tarjetas conservan su progreso.

## Fricciones del proceso

- La primera subida no aplicó el orden de nuevas: el complemento llevaba escrito el nombre antiguo del mazo (el de antes del 9 de noviembre). Arreglado en el lote, con reinicio de Anki y segunda subida.
- Al escribir los datos, tres tropiezos de formato del agente: grupos con `use: null`, títulos de grupo volcados con el `...` de fin de documento de YAML (rompió la carga de `compras.yaml`) y un ID de grupo repetido (`g.xi-xi`). `check` los cazó todos; ningún dato llegó roto a Anki.
- `scaffold` creó las tarjetas estándar (leer, dictado) de los segundos sentidos (还 «además», 来 «póngame», 会, 点 «pedir»), iguales que las del primer sentido; se quitaron al pasarlos a `use: context`, como 那 «entonces».
- El desván despertó en el mismo lote siete cosas que el agente acababa de guardar (推荐 con 菜单, 位子 con 位…): hubo que aplazarlas a mano con `snooze`.
- Una prueba (`test_private_names_stop_the_close`) escribe un momento un archivo en el inbox real (`2099-01-01_prueba-privada.md`) y lo borra al acabar: si un lote se cerrara mientras corren las pruebas, podría colarse en el commit. El cierre de este lote esperó a que acabaran; queda para la retrospectiva del lote 020.

## Seguimiento

**Nivel.**
- **HSK 1, superado**: 406 de 506 (80,2 %; en el lote 016, 75,9 %). Desde este lote el nivel de trabajo es el **HSK 2**: 153 de 750 (20,4 %). Las propuestas por frecuencia pasan a ser del HSK 2.
- Ya puedes pedir en un restaurante de principio a fin: cuántos sois (两位), aquí o para llevar (不打包，我们在这里吃), lo que quieres (我要饺子，还要汤; 来一杯可乐; 不要辣), preguntar (这个辣吗？, 这是什么肉？), pagar (一共多少钱？, 可以刷卡吗？, 买单！); y hacer de camarero. También pedir otra talla o precio (有大一点的吗？) y orientarte (北京在中国的北边).

**Las clases.**
- Ahora hay **dos profesoras**: la del curso de HSK 1 y la nueva, desde el 6 de noviembre, que da clases de conversación por situaciones (presentarse, quedar, pedir en un restaurante), con rondas de práctica y cambio de papeles. Encaja de lleno con `docs/goal.md`: hablar en situaciones reales.
- La clase 2 fue toda de restaurante: vocabulario por grupos, tres rondas de pedir y hacer de camarero. Lo que más anotó: 还要, 来 para pedir, 美女 / 帅哥 y 下次再来.

**Tu método.**
- **Constancia**: 28 de los últimos 30 días; unos 20 minutos al día (antes 26) y 5 nuevas al día (antes 10).
- **En Anki**: 12 % de «Otra vez» y 88 % de retención. Tonos, un 8 %; decir, un 16 %; oír, un 6 %.
- **Tus notas**: rinden igual que siempre lo marcado («!!!», «IMPORTANTE», «CONTRASTE»). Las listas largas del asistente (tiendas, hoteles, letreros) entraron casi enteras porque usaban tu vocabulario.

**Consejo.** Antes de la próxima clase, haz en voz alta las dos de construir (#KW8SK, pedir; #ASP4T, hacer de camarero) y escucha el diálogo #X2K3F: son la clase 2 entera. Ya salen primero en Anki.

**Avisos.**
- El HSK 1 está superado: lo que falta de él (100 palabras) entra cuando salga en clase o en tus notas; las propuestas por frecuencia, del HSK 2.
- La cola de nuevas de tu nivel son unos 114 días a 30 al día (lo de clase, unos 45). Abres unas 5 nuevas al día: lo de clase sale primero igual, pero cuantas más abras, antes llega lo demás.
- El orden de nuevas vuelve a funcionar tras el cambio de sitio del mazo en Anki (ver «Cambios en el sistema»). Sincroniza el móvil antes de estudiar.
