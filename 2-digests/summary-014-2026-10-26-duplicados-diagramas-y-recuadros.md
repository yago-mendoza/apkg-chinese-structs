<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->

# Log del lote 014-2026-10-26-duplicados-diagramas-y-recuadros

**Origen.**
- **Tus respuestas al review 013**: «bórralas» a las 10 tarjetas de oír; «sí, bórralas» a leer 雅戈 y leer 门多萨; tres parejas para oír (吃 / 次, 渴 / 个, 孟 / 门); el audio de cada frase de los matices delante. Lo demás, en blanco.
- **«Tus notas» del review 013**: unas 850 líneas, del 23 al 26. Tus mnemotecnias, frases tuyas hechas con el vocabulario del mazo, contrastes que pedías, consultas pegadas de un asistente (我来, 从, 一起 / 跟 / 还是 / 或者, 这些 / 那些 / 哪些, 的 de relativo, 听不懂 / 不明白), tu examen de 这个 / 这里, la tabla de palabras de trabajo y la sospecha de tarjetas repetidas.
- **En el chat, el 26**: la revisión de duplicados y de por qué te volvían las tarjetas (solo lectura de Anki), y lo que decidiste a partir de ahí («contesta tú mismo», «pon lo que vas a hacer, decididamente»), apuntado al final del review 013: deduplicar, diagramas siempre que aclaren, el orden y el aspecto de los recuadros, la nota con aspecto de nota y quitar «Mismo sonido». Y que cada lote compruebe en Anki que lo nuevo funciona.
- **Materiales de clase**: ninguno pendiente.
- **Al empezar**: el móvil sincronizado, sin tocarlo hasta mañana.

En cifras: 154 tarjetas nuevas y 33 retiradas (3449 en total); 25 entradas (13 palabras y expresiones, 1 carácter, 3 estructuras y 8 grupos), 69 frases y 10 elementos al desván.

## Cambios en el sistema

- **Una pregunta, una respuesta**: no había notas duplicadas en Anki, pero sí tarjetas que para ti eran la misma pregunta (ver «Duplicados»). Ahora `check` avisa de dos tarjetas con el mismo anverso (`duplicate_prompts`; una pareja legítima lleva `same_prompt_ok` con motivo) y da error con un contraste que suena delante y tiene una opción que suena igual que la respuesta (`homophone_contrasts`). Una tecleada acepta otras respuestas igual de buenas (`answer.accept`), para fusionar sin marcarte mal lo bueno.
- **Contrastes de un grupo, separados**: dos contrastes nuevos del mismo grupo (妈 / 吗 / 马) no salen a menos de un día de estudio el uno del otro; se veían iguales y parecían la misma tarjeta (`interleave_streams`).
- **Un código en cada tarjeta** (tu nota): en medio de la cabecera, cinco caracteres (`#K7Q2M`), sacados del ID, que no cambian nunca. Para referirte a una tarjeta en el inbox; `anki.py lookup #K7Q2M` dice cuál es.
- **El reverso, por importancia y con su aspecto**: ejemplos como siempre; luego lo de clase, tus mnemotecnias, «Uso real», la nota y sus caracteres; más abajo, con otro aspecto, «Otras formas de decirlo» (🔁, lo de `also:`) y las familias de palabras con su diagrama (🧭); lo último, lo que solo se parece a la vista o al oído (👀). Fuera «Mismo sonido». Si una palabra o un carácter tiene mnemotecnia propia, no se cuenta además por qué se escribe así. La nota se titula «Uso y significado · 了», con aspecto de nota (📝); el apunte, más discreto (✎).
- **Los matices suenan delante**: cada frase de la consigna, con su audio en el anverso, salvo los calcos que se comparan (`prompt.no_audio`: 我是高兴, 我很高也, 我们很高都, 这个你怎么样？) y los componentes.
- **Diagramas**: la franja del día lleva el nombre de cada palabra debajo de su barra; un grupo puede llevar una escala de menos a más (`scale`) y un eje de tiempo con «ahora» en el centro (`aspect`). Norma: un diagrama siempre que aclare algo.
- **Despedidas con sus alternativas** (tu nota de 明天见): grupo «Despedirse» (再见, 拜拜, 明天见, 晚安), que sale como familia en sus tarjetas.
- **Comprobar en Anki que lo nuevo funciona**, paso fijo de cada lote tras subir (`docs/design.md`, «Flujo de un lote», 10b).
- **Con FSRS, los días los decide FSRS**: `docs/owner.md` decía que «Fácil» en una nueva da 4 días; con FSRS da 2. Corregido el documento; la configuración no cambia.
- Vive en `docs/goal.md` («El reverso…», «Una pregunta, una respuesta», «Diagramas sin cortarse»), `docs/design.md` («Flujo de un lote», «Comentarios», «Tarjetas», «Anki», «Garantías»), `docs/hypotheses.md`, `docs/owner.md`, `3-data/README.md` y `anki.py`; siete entradas del 2026-10-26 en `docs/decisions.md`; pruebas nuevas en `tests/` (`Lot014`).

## Por qué te volvían las tarjetas

Revisión de solo lectura de Anki, con lo estudiado en el móvil hasta el 26:

- **No era una tarjeta: eran muchas que se parecen.** Unas 30 tarjetas llevan «ma». Del 23 al 26 te salió cada día una distinta: el contraste de 吗 el 23 (a 21 días), leer 妈妈 el 24 (a 23), los tonos de 妈妈 el 25 (a 26), y las nuevas de 妈 «mamá (al llamarla)», leer y contraste, el 24, el 25 y el 26. Cada una se fue a los días que le diste; tres contrastes tenían el mismo anverso, 妈 / 吗 / 马.
- **Los botones se respetan.** Desde el 19 no ha habido ninguna reprogramación manual. Las que acortaron intervalos ganados fueron las del 16 (42 tarjetas) y el 19 (33): las subidas que pisaron el móvil y su recuperación, ya cerradas con `--phone-synced`.
- **Con FSRS, «Fácil» en una nueva da 2 días**, no 4, y lo que fallaste hace poco vuelve pronto aunque pulses «Fácil»: los parámetros del 21 parten de una estabilidad inicial de 0,04 días. Mejorará con la próxima optimización.
- **De ahí, este lote**: deduplicar (abajo), separar en días distintos los contrastes de un mismo grupo y el aviso de `check` para que no vuelva a pasar.

## Duplicados

Progreso mirado en Anki antes de decidir cuál se queda: siempre la que tiene repasos.

- **Un hanzi con dos sentidos y el mismo anverso**: un dictado por sonido para 两, 又 y 早, con los dos sentidos detrás (se retiran los otros tres); la lectura lleva ahora una palabra al lado que dice qué sentido es (两个人 / 一两茶, 又高又帅 / 他又来了, 早！ / 很早), con el mismo ID y su progreso; el contraste de 又 «repetir» se funde con el de 又 «a la vez».
- **La misma pregunta tecleada con otra respuesta**: «olvidar» es una tarjeta que acepta 忘 y 忘记; «país», una que acepta 国家 y 国, con una nota de cuándo cada uno; las glosas de 早 ya no se pisan («¡buenos días!» / «temprano»).
- **«Dilo en chino» con la misma frase en español**: una tarjeta por frase, con la otra en «Otras formas de decirlo» (我忘了 / 我忘记了, 这是 / 这个是什么意思, 中文 / 汉语, 我在北京出生 / 我出生在北京, 你多大了 / 你多大, 你喜欢就买吧 / 如果你喜欢就买吧). Donde la diferencia importa, además un matiz: 你好吗 / 你怎么样, 明白了 / 懂了, 哪国人 / 来自哪个国家.
- **Dos que estudiaste en el móvil del 24 al 26**: en «¿De qué país eres?» se queda la de 你来自哪个国家？ (a 16 días), con 你是哪国人？ y 你是哪个国家的人？ como otras formas; en «¿Cuántos años crees que tiene?», la de 她, con 他 como otra forma. Las que se iban a quedar no tenían repasos.
- **Frases hechas tecleadas y dichas**: se quedan solo las de decir (你好吗, 你还好吗, 最近忙吗, 最近怎么样, 这个怎么样, 没什么); 小心 conserva las dos, porque se combina.
- **Contrastes de oído imposibles**: los 13 en que otra opción suena igual que la respuesta (又 / 右, 属 / 鼠, 钱 / 前, 难 / 男, 块 / 快, 长 / 常) se preguntan ahora por el significado, sin audio delante («¿Cuál es shǔ, «rata (del zodiaco)»?»), y sin pistas que delaten la respuesta.
- **Lo que sospechabas de 你 / 欢**: no era un duplicado (uno pregunta nǐ y otro huān); ahora el anverso es 你 / 欢 / 饭, que pedías contrastar.
- **De paso**: en 13 parejas para oír, el significado de la primera sílaba era el texto de la respuesta («La 1.ª: sì 四.»); corregido («cuatro», «ser», «vez»…).

## Tus respuestas al review 013

- **Las 10 tarjetas de oír** de frases que ya practicas para decir: retiradas (tenían de 1 a 4 repasos; se borran en Anki a mano, porque `--prune` protege lo que tiene historial).
- **Leer 雅戈 y leer 门多萨**: borradas en Anki.
- **Parejas para oír**: 吃 / 次, 渴 / 个 y 孟 / 门, y además 文 / 问 y 现 / 先, que pedías en tus notas.
- **El audio de los matices, delante**: hecho (ver arriba).
- **哦 ò suelto**: sin respuesta; sigue en «Por verificar».

## Tus notas, en sus tarjetas

- **Tus mnemotecnias**, con tu texto en `original`: 克 (el pesito con patas colgado de un cable), 超市, 岁, 属, 热, 慢, 觉得 (y «juéde suena a juzgar»), 准备, 见面 («una cara clavada»), 休息, 出 y 出生 («salir a la vida», con sus dos tonos altos), 从 (la chincheta), 时 y 时候, 介绍 (el hilo), 爷爷 y 奶奶, 电 y 电脑, 能 (熊 con cuatro patas), 谁 y 难 (la estantería de cabezas), 推, 一定 y 定, 来自 («venir uno mismo»: proceder), 年轻, 现在 y 知识 (识).
- **Explicaciones, en su palabra**: 我来 + verbo «yo me encargo»; 从…到…; 跟我来; 哪 + clasificador («cambia 一 por 哪»: 哪天, 哪本书, 哪国人); 多 + adjetivo (多大, 多高, 多远); 你多大了, más natural con 了; 同 «compartido» y 事 frente a 工; 孩 / 还; 还是 «aun así»; 见面 frente a 约 y 认识; 不一定; 久 frente a 时间; 什么时候 palabra a palabra; 我想想; 准备 + verbo «ir a»; 在 + 哪里 delante del verbo; las despedidas; 阿姨 frente a 女士; el 的 de relativo, que no dice que sea pasado; 现 no es 先.
- **Tus frases**: 69 nuevas, la mayoría tuyas o de tus tablas, con vocabulario del mazo (我来付钱。, 我从九点工作到五点。, 以前你帮我，以后我帮你。, 我的手机没电了。, 我听不懂他说的话。, 我说了，我不要水！, 中国是一个很大的国家。, 我想学习更多知识。, 我明天要上班。, 你要水还是茶？, 我跟你一起去。, 这些多少钱？, 这是我买的书。…). Corregidas: 你太忙 → 你太忙了; tu tabla de 这儿 / 那儿 pasa a 这里 / 那里 (solo mandarín estándar). Fuera: 你要害我吗 (害 es HSK 5), 我的大脑怎么了 y 动脑子 (HSK 5, poco naturales a tu nivel). Cinco diálogos para oír con 这个 / 那个 / 这里 / 那里, por tu examen.
- **«DEMASIADOS EJEMPLOS»**: de las tablas de 一起 / 跟 / 还是 / 或者 se quedan seis frases y tres matices.
- **Contrastes que pedías**: 都 / 哪 / 那 / 脚 (se parecen); 欢 / 饭; 文 / 问 y 现 / 先 (parejas para oír); 定 / 走 / 是; 要 / 有 con los pesos (de elegir: 我要三斤苹果, 这里有两斤左右的苹果); 是的 frente a 好的 / 对 (tres de elegir, con escena); 这个 / 这里 (un matiz y tres de elegir).
- **Matices** (14): 你好吗 / 你怎么样, 我很好 / 我还好 / 我觉得很好, 明白 / 懂, 听不见 / 听不懂, 听不懂 / 不明白, 哪国人 / 来自哪个国家, 还是 / 或者, 还不懂 / 还是不懂, 还是 «o» / 还 + 是, 跟 / 一起 (con «我跟你(一起)去»: lo opcional, entre paréntesis), 今 / 现, 这个 / 这里, 我来了 / 我来, 得 děi / de.
- **Huecos** (9): 还是 / 或者 (dos), 哪天, 什么都, 我来, 总是, 有些, 更, y «要 es tener que».
- **Situaciones** (5): pagar yo, ayudar yo, no te oigo, sin batería y felicitar. **Construir** (3): quedar, el horario y la reunión en que no entiendes. **Comprensión** (2).
- **Estructuras** (3, con su calco): 从…到… (我工作从九点到五点 ✗), 还没 + verbo (我还没买了 ✗) y el 的 de relativo (这是书我买的 ✗).
- **Tratamientos**: 阿姨 se queda para decir (es el útil); 叔叔, con nota de que a un desconocido basta 请问; 女士, 姑姑 y 姨妈 al desván, como sospechabas que no hacían falta todos.
- **知识, ¿HSK 1 o HSK 4?**: es HSK 1 en el HSK 3.0, la lista que usa el mazo; HSK 4 era en el antiguo HSK 2.0. No cambia nada.
- **上车 sin ejemplos**: ya lo tiene (快上车！).
- **«ESTA CARD ELIMÍNALA»** (En 中国, ¿cuál es guó?): retirada.
- **El número de cada tarjeta**, **el recuadro de alternativas** y **el audio delante en los matices**: ver «Cambios en el sistema».

## Palabras y frases nuevas

- **De tus notas**: 明天见, 或者, 有些, 哪些, 电 «electricidad; batería», 更, 果汁, 推 y 拉 (para leer, por las puertas), y para oír, 下班, 请假 y 经理, de tu tabla de trabajo (las de HSK 1–2).
- **Suben a decir**: 同事, 公司 y 恭喜.
- **Del desván**: 总是 (con la escala de frecuencia).
- **Diagramas**: los pesos (克 → 两 → 斤 → 公斤, en el grupo de pesos), la intensidad (有点 → 很 → 非常 → 太), la frecuencia (有时候 → 常常 → 总是), antes / ahora / después (以前 / 现在 / 以后) y el eje del tiempo de 过, 已经, 了, 在, 快要 y 还没. 快要 va justo después de «ahora»: está a punto de pasar. 要…了, 就 / 才 y …的时候 no tienen entrada propia aún.
- **HSK 1**: 341 de 506 (67,4 %).

## Del desván

- **总是**: entra para la escala de frecuencia (有时候 → 常常 → 总是).
- **Despiertan, pero esperan**: 者 (despertó con 或者, donde no es el sufijo de agente) y 饮料 (despertó con 果汁; sigue siendo palabra de un ejercicio de pinyin).

## No entró, y por qué

- **Al desván**: 女士 (HSK 4), 姑姑 (HSK 6) y 姨妈, con su nota; 介意 (nivel 7) y 唯一 (HSK 5, con tu imagen); 河 (HSK 2, pero llegó suelto, sin frase ni el clasificador 条; con tu imagen del puente); 台 (HSK 3, con tu frase 我要十台电脑); 加班, 工资 y 面试 (HSK 3–4, de la tabla de trabajo).
- **Fuera**: 害 y su frase; 喜悦 y 喜爱 (literario o formal); 大脑, 脑子 y 动脑子; lo de HSK 5–7 de la tabla de trabajo y la jerga (摸鱼, 内卷, 躺平), una lista de curiosidad sin frases; 打工 (no es de un ingeniero); «Los cambios radicales externos…» (no es chino).

## Reorganización

- **33 tarjetas retiradas**: las 10 de oír, la de 中国, 16 fusiones y 6 tecleadas de frases hechas. Se borran en Anki tras subir (ver «Cambios posteriores» si hace falta).
- **g.you-you** pasa a serie (`set`) sin contraste propio: 又 «otra vez» y 又 «a la vez» son el mismo sonido.
- **g.na-dou** y **g.ni-huan** se amplían (哪, 脚; 饭); grupos nuevos: frecuencia, antes / ahora / después, eje del tiempo, 推 / 拉, 定 / 走 / 是, 电 / 店 / 点, 这些 / 那些 / 哪些 y «Despedirse».
- **Temas**: sin cambios; ninguno pasa del tope.

## Fricciones del proceso

- **La regla de los homófonos marcaba de más**: la primera versión de `homophone_contrasts` miraba si la tarjeta lleva audio detrás, y daba error en los contrastes que ya se preguntan por el significado (他 / 她 / 它, 在 / 再, 坐 / 做…). Se corrigió para mirar solo el audio delante.
- **Los matices pedían audio para calcos erróneos** (我是高兴): se añadió `prompt.no_audio`; y los componentes (亻, 讠), que la voz sintética no lee, quedan fuera solos.
- **La revisión de progreso se hizo con datos viejos**: el agente de contenido miró la copia del ordenador, que llegaba al 23; tras sincronizar, dos fusiones tenían ya repasos del móvil en la tarjeta que se iba a retirar, y se invirtieron. Antes de decidir con el progreso, sincronizar.
- **明天见 ya existía como frase y tarjeta**: al crear la expresión se duplicaron ID; `scaffold` se negó y se reutilizó lo que había.
- **Bash no acepta algunos bloques largos en línea** (comillas): los scripts de edición se escribieron en archivos; y un script del espacio temporal llamado `glob.py` tapó el módulo estándar.
- **Finales de línea**: la mitad de los YAML de `3-data` son CRLF y la otra mitad LF; las ediciones respetan los de cada archivo.
- **`push` y `stats` fallaban justo después de sincronizar** («Collection lifecycle operation is active»): la sincronización de AnkiConnect vuelve antes de terminar. `anki_request` espera y reintenta mientras Anki está ocupado.
- **`close-batch` falló al generar el cuaderno**: el grupo del eje del tiempo tiene estructuras como miembros, sin hanzi. Se nombran por su plantilla, como en los diagramas; el review leído ya se había archivado y el cierre se repitió.
- **Las pruebas pasan de 20 minutos** (132 pruebas, entre 24 y 33).

## Seguimiento

**Nivel.**
- HSK 1: 341 de 506 (67,4 %; en el lote 013, 66,4 %). Te faltan 64 palabras para el 80 %.
- Este lote no buscaba palabras nuevas: limpió duplicados y convirtió tus notas en frases, contrastes y matices.

**Las clases.**
- Sin material de clase nuevo: lo último sigue siendo la clase del 23 (lección 1-2, edad y zodiaco). Desde el 30 de octubre, una clase por semana, los viernes.

**Tu método.**
- 29 de los últimos 30 días, unos 26 minutos cada uno, y unas 12 nuevas al día.
- En Anki: 16 % de «Otra vez» y 86 % de retención (en el lote 013, 19 % y 83 %). Los tonos fallan un 34 % y decir un 23 % (antes, 44 % y 32 %): bajan otra vez.
- Tus notas de estos días son las mejores hasta ahora para el mazo: frases tuyas con lo que ya sabes, y confusiones concretas (这个 / 这里, 还 / 还是, 听不懂 / 不明白). Lo pegado del asistente rinde cuando es un contraste; las tablas largas, menos.

**Consejo.** Usa el código de la cabecera (#…) cuando algo de una tarjeta no te guste: con él la encuentro al instante. Y cuando notes que algo «se repite», apunta el código: así se ve si es la misma tarjeta o una parecida.

**Avisos.**
- Antes de estudiar, sincroniza el móvil: cambia el aspecto de todas las tarjetas y se retiran 33.
- Decir sigue por debajo del 25 % de lo que viene (19 %): el próximo lote, más tarjetas de decir y de construir.
- Las 20 de HSK 1 por frecuencia del review 013 y fijar la lectura de los polífonos sueltos (得, 哦) siguen sin respuesta: entran el próximo lote salvo que digas que no.
