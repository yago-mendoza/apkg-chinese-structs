<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 019-2026-11-24-charla-cotidiana-y-reacciones

Una fuente grande: dos pegados de WhatsApp. El primero (`wa-2026-11-24-0000.md`, ~36 KB) es una reconstrucción —hecha por un asistente— de las fotos de las páginas 3-12 de tu curso, ordenada en tres lecciones: conversación básica, pedir en el restaurante y charla cotidiana (small talk). El segundo (`wa-2026-11-24-0148.md`) son dos consultas tuyas con código de tarjeta: #59HQP (que se explique el 校 de 学校) y #9JDK4 (更多 frente a 多 + verbo). No había materiales de clase pendientes (`anki.py materials`: 0). El review 018 llegó sin respuestas: sus preguntas siguen abiertas y las recojo abajo y en el review 019.

Lo esperable con un volcado así: **casi todo el vocabulario ya estaba en el mazo** tras 18 lotes (restaurante, saludos, comida, tiempo, conectores, aficiones…). El lote no repite lo que existe; mete lo genuinamente nuevo —frecuencia, aficiones, conectores y, sobre todo, las reacciones coloquiales de las dos últimas páginas— y los contrastes que marcó tu profesora.

## Cambios en el sistema

- **Norma escrita: fórmula / ejemplo / compose.** El encargo del lote. Se deja escrito el criterio para clasificar cada frase por sentido común, de ahora en adelante. **Fórmula** (`kind: formula`): un trozo fijo que se dice tal cual, sin huecos que varíen (我吃饱了, 我什么都吃, 我吃饭了); gana sus cartas de producir/reconocer según su `use`. **Ejemplo** (`kind: example`): ilustra una palabra o estructura con un contenido que no se dice verbatim (这是一家饭店, 他做的饭很好吃); va de contexto en el reverso, sin carta propia. **Patrón generativo** (hueco que rellena el que aprende: 我喜欢吃__, 我要一杯__, 我最喜欢__): no se vuelca como muchos ejemplos sueltos, sino que se agrupa en una sola carta `compose`. Es criterio de propuesta, no volcado: se juzga frase a frase. No cambia el código (`kind` existía desde el 2026-10-19/23 y `compose` desde el 2026-10-11). Vive en: `docs/design.md` («Datos», Frases) y `docs/decisions.md` (2026-11-24).

## Material de clase

- Las tres lecciones son material del curso (fotos pp. 3-12), tratadas como clase (`origin: class`), con `file` apuntando al pegado de WhatsApp y fecha de procesado (24 nov): no traían fecha y las fechas de clase siguen por verificar (review 018, sin contestar). Son una **reconstrucción por LLM**, no una transcripción literal, así que el contenido se contrasta con el mazo y con la lista del HSK y lo dudoso va a «Por verificar» (⚠️), no se da por bueno.
- Los role-play del restaurante y de la charla, y las «preguntas sorpresa» de la profesora, ya estaban cubiertos por los lotes 013-017; de aquí salen solo las piezas nuevas.

## Promoción a fórmula (encargo del lote)

- `s.wo-chifan-le` (我吃饭了 «ya he comido»), `s.wo-mei-chifan` (我没吃饭 «no he comido») y `s.wo-shenme-dou-chi` (我什么都吃 «como de todo»): de `example` a `formula`. Se dicen tal cual. IDs y cartas intactos (el `kind` no cambia las tarjetas exigidas; verificado con `scaffold`/`check`). Siguen en el tema `comida`, que es su situación.
- 我吃饱了: el encargo pedía añadirlo como fórmula nueva, pero `lookup` lo encontró **ya en el mazo** (`s.wo-chi-bao-le`, ya `kind: formula`, y la entrada 饱 `w.bao.full`, use `say`, con su comentario de uso). No se duplica: ya estaba bien.

## Compose (patrones generativos)

- `x.compose.xihuan-chi` (我喜欢吃__ «una comida que te gusta»): agrupa los ejemplos existentes 我喜欢吃鱼 / 汉堡 / 火锅 / 上海小吃 como modelos. En `comida`.
- `x.compose.yao-yi-bei` (我要一杯__ «una bebida»): modelos 我要一杯可乐 / 水 / 果汁. En `comida`.
- `x.compose.zui-xihuan` (我最喜欢__): modelos 我最喜欢中国菜 y 我最喜欢吃火锅 (frase nueva `s.wo-zui-xihuan-chi-huoguo`, para tener dos mezclas). En `comida`.

## Palabras y frases nuevas

Por temas. 🃏 = con tarjeta.

**Charla cotidiana / frecuencia (tiempo)** — 🃏 每天 měitiān «todos los días»; 🃏 平时 píngshí «normalmente, de ordinario»; 🃏 空 kòng «tiempo libre» (polífono: kōng «vacío»). Frases: 我每天去健身房, 我平时在家工作, 你有空吗？.

**Comida y bebida** — 🃏 好喝 hǎohē «rico de beber» (frente a 好吃); 🃏 酒 jiǔ «alcohol» (id `w.jiu.alcohol`, porque `w.jiu` ya es 九). Frases: 这个茶很好喝, 我不喝酒.

**En el restaurante** — 🃏 瓶 píng «botella (clasificador)»; 🃏 碗 wǎn «cuenco (clasificador)». Frases: 我要一瓶啤酒, 我要一碗面条, 下次再来 (fórmula del camarero).

**Tiempo libre y deporte (ocio)** — 🃏 踢 tī «dar una patada, jugar (al fútbol)» (frente a 打); 🃏 健身房 jiànshēnfáng «gimnasio». Frases: 我喜欢踢足球, 我常常去健身房.

**Unir frases (conectores)** — 🃏 除了 chúle «excepto; además de» (dos usos); 🃏 只 zhǐ «solo» (adverbio; `use: [say]`, se practica en hueco, porque la lectura y el sonido de 只 ya los cubre el clasificador 只 zhī). Frases: 除了咖啡，我什么都喝, 我只喝水.

**Saludos y charla (saludos)** — 🃏 约 yuē «quedar, citarse»; 🃏 你呢 (expresión) «¿y tú?». Frase: 我们下次再约.

**Reacciones (cortesía)** — 🃏 厉害 lìhai «impresionante; fuerte, intenso»; y las expresiones 🃏 太好了 «¡qué bien!», 🃏 我的天 «¡madre mía!», 🃏 真的假的 «¿en serio?», 🃏 笑死我了 «¡me parto!». Frase: 你太厉害了.

**Contrastes nuevos (matiz), lo que marcó la profesora** — 🃏 更多 / 多 + verbo (cuantificar la cosa frente a la acción, tu consulta #9JDK4); 🃏 有点 / 一点; 🃏 一次 / 一遍; 🃏 做什么 / 做了什么 (aspecto 了); 🃏 踢 / 打 (jugar); 🃏 好吃 / 好喝; 🃏 平时 / 一般 / 常常 (frecuencia).

**Caracteres nuevos** (en `hanzi.yaml`, con su porqué y su imagen para recordar): 平, 踢, 瓶, 碗, 空, 酒, 约, 除, 厉, 害, 死. (假, 聊, 校, 次, 遍, 做, 更, 惨, 每 ya estaban.)

Volumen: unas 100 tarjetas nuevas (90 estándar de `scaffold` + 3 compose + 7 matices), dos quitadas (la lectura y el dictado duplicados de 只, cubiertos por el clasificador). Mazo: 4601 tarjetas. `check`: 0 errores, 13 avisos (justificados abajo). Audio: 36 clips nuevos de Azure.

## Tus notas, en sus tarjetas

- **#59HQP, el 校 de 学校**: tenías razón en que no se explicaba por qué suena xiào. La tarjeta de 学校 lleva una mnemotecnia, que por regla tapa el análisis del carácter; por eso no veías el porqué. Añadido un panel 💡 «Para entender»: 校 se lee xiào porque 交 (jiāo) le da el sonido; 木 da el sentido; el mismo 交 suena en 饺 jiǎo. (Tu segunda petición, revisar si otras tarjetas tienen algo notable sin explicar: el porqué de cada hanzi está en `hanzi.yaml` y sale en «Sus caracteres»; donde una mnemotecnia lo tapa, un panel 💡 lo saca, como aquí.)
- **#9JDK4, 更多 frente a 多 + verbo**: convertido en una tarjeta de matiz (no en un párrafo), con las dos frases modelo. 更多 + sustantivo cuantifica la cosa; 多 + verbo cuantifica la acción.

## Del desván

- Ninguno despertó (`anki.py attic 019…`: todos «espera»). 了解 y 舞蹈 reaparecieron, pero solo como palabras de la lista de pronunciación (shadowing 3+3), sin frase ni sentido de uso; siguen esperando (ya estaban en el desván, no se duplican).

## No entró, y por qué

- **Lo repetido**: casi todo el vocabulario de las tres lecciones ya estaba en el mazo (es un repaso del curso). No se crean tarjetas de lo que ya existe.
- **Fuera (erhua)**: 那儿, 这儿, 哪儿 → se usa 那里 / 这里 / 哪里 (ya en el mazo).
- **Fuera (rúbrica de los ejercicios)**: 句 y 至少 salían en las consignas («至少6句»), no como algo que YAGO diga; 至少 queda propuesto en el review.
- **Propuesto, no metido aún** (en el review, por si los quiere): 遇到, 打招呼, 走廊, 推荐, 英语, y las reacciones de jerga 绝了 y 太惨了.

## Reorganización

- **Tema `tiempo` («Momentos del día») en 63 entradas** (tope 60): lo cruzaron 每天, 平时 y 空. Aviso de `check`. No se parte ahora: en el lote 020 (mantenimiento) se propone separar las palabras de frecuencia de los momentos del día, junto con la división de «Describir» ya prevista. Anotado en el review.
- **Avisos de homófonos** (约/月, 酒/九, 酒/就, 碗/晚·完·万·玩, 只/纸): las palabras nuevas suenan igual (sin tonos) que otras del mazo. No se crean grupos por adelantado (regla de `docs/goal.md`: solo cuando YAGO confunde): van al review para que marque las que confunda.
- **Avisos de serie fonética** (平 con 苹 de 苹果; 空 con 工/红): quedan como posible conexión de sonido para un próximo lote; no se añaden ahora para no inflar.

## Fricciones del proceso

- `lookup` evitó duplicar 我吃饱了/饱, que el encargo daba por nuevos: estaban ya en el mazo. Confirma que el paso `lookup`/`gaps` antes de añadir cumple su función.
- Dos colisiones de ID al añadir: `w.jiu` (九) con mi 酒 → renombrado `w.jiu.alcohol`; y el polífono 只 generó lectura y dictado duplicados del clasificador existente → se resolvió con `use: [say]` (hueco) en el sentido nuevo y borrando los dos duplicados, siguiendo el patrón del mazo.
- `scaffold` dejó una carta con el texto viejo tras renombrar una frase por `sed` (每天): hay que reescribir los campos horneados (consigna, contexto, respuesta), no solo el id.
- Em-dash (—) en `hanzi.yaml`: `check` lo da como error (raya); hay que usar comas o paréntesis. En los comentarios sí se admite.
- AnkiConnect respondió (la carga y `stats` se leyeron de Anki), así que `push` se intenta en este lote.

## Seguimiento

**Nivel.** HSK 1: 412 de 506 (81,4 %, igual que el lote 018; estas lecciones repasan lo que ya tenías). HSK 2, tu nivel de trabajo: 168 de 750 (22,4 %; antes, 164).

**Las clases.** Las tres lecciones son un repaso amplio (presentarse, restaurante) más charla cotidiana nueva: frecuencia (平时, 一般, 常常), aficiones (踢足球, 健身房), conectores (因为…所以, 除了) y reacciones de verdad (太好了, 我的天, 真的假的, 笑死我了). Encaja de lleno con sonar natural, que es tu objetivo. Siguen sin confirmar las fechas y si continúas con las dos profesoras.

**Tu método.** Constancia alta (29 de 30 días), pero unos 17 minutos y 3 nuevas al día: sigues abriendo pocas frente al límite de 30. 12 % de «Otra vez», 90 % de retención. Lo que más cuesta no cambia: 我们一起去吧 (al decir, 5 lapsos), 跟 gēn y 帮 bāng. Consejo, el mismo que en 018: sube a 8-10 nuevas al día un par de semanas; con 117 días de cola, los huecos y contrastes que pides tardan por eso.

**Avisos.** `tiempo` llegó al tope de entradas: división propuesta para el 020 (mantenimiento y retrospectiva). Varios homófonos nuevos esperan en el review a que marques los que confundas.
