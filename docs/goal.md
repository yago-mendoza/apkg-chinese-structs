# Objetivo del que aprende

Este documento es un módulo de prompt: la única parte del sistema que depende de quién aprende. El agente lo lee antes de procesar un lote y lo aplica como primer filtro: con él decide qué entra, cuánto se practica, en qué orden y qué huecos señalar. Si algo de aquí choca con una regla de `docs/design.md` en lo que es del que aprende, manda este archivo.

**Qué va aquí y qué no.** Va lo que cambiaría con otra persona u otro objetivo: quién es, para qué estudia, qué entra, cómo quiere practicar y cómo quiere que se le hable. No va cómo funciona el sistema (`docs/design.md`), la configuración de su equipo y sus límites diarios (`docs/owner.md`), por qué o cuándo se decidió algo (`docs/decisions.md`) ni cómo va ahora (`2-digests/state.md`). Se escribe en presente, sin fechas. Para otra persona se reescribe este archivo y nada más.

## Quién aprende

YAGO, ingeniero, hispanohablante. Está empezando mandarín, con clases particulares que siguen un curso de HSK 1. Estudia en ratos sueltos, casi siempre en el móvil, con auriculares y teclado chino: el audio está disponible en cualquier sesión y puede escribir pinyin con tildes o hanzi. Puede hablar en voz alta siempre, también en público: cualquier tarjeta puede pedirle decir algo en voz alta.

**Rutina.** Clases los martes y los jueves. Estudia todos los días: de 20 a 40 minutos lo normal, hasta hora y media algunos días, y rara vez menos de 20 (cuando pasa, suelen ser varios días seguidos). Los lotes, cuando él los pide: no hay costumbre fija.

## Para qué

Hablar chino y **sonar natural**: no solo correcto, sino como lo diría un nativo. No es preparar el examen del HSK: el HSK sirve de escala para ordenar, no de meta. Llegar a un nivel equivalente a C1 con **mucho énfasis en fluidez y en pronunciación**, para:

- conversación cotidiana, con naturalidad y algo de personalidad;
- trabajo y negocios: es ingeniero; reuniones, trato profesional, vocabulario técnico cuando llegue;
- vivir en China: transporte, compras, comida, casa, salud, trámites, aplicaciones;
- viajar;
- leer y entender lo que aparece en ese día a día (carteles, menús, mensajes).

## Filtro de lo que entra

Cada elemento de los apuntes se juzga contra el «para qué» de arriba:

- **Entra para decir** (`say`): lo que usaría hablando en esas situaciones.
- **Entra para entender** (`hear` o `read`): lo que oirá o leerá pero no necesita producir (registro formal, carteles, fórmulas escritas).
- **Espera en el desván**: lo de su investigación propia que es de un nivel superior y está poco conectado, o lo que llega suelto sin frase. No entra aún, pero se guarda con todas sus notas y entra solo cuando llegue algo con lo que conecte (`docs/design.md`, «Desván»). Lo de clase nunca va al desván, salvo las palabras que salen solo para practicar sonidos (ver abajo).
- **Queda fuera**: literario, arcaico, en desuso, lo tradicional que hoy suena anticuado (哪里哪里 ante un elogio: hoy se dice 谢谢), variantes regionales que no son estándar y rarezas sin uso real. Vale lo formal de trabajo y lo coloquial de la calle. Se dice en el log y en el review, con el motivo, por si no está de acuerdo.
- Lo que viene de sus apuntes se respeta aunque no esté en ninguna lista, siempre que pase el filtro: si lo apuntó, suele ser porque lo necesita.
- **Lo de clase incluye lo que va dentro de los ejercicios.** El vocabulario de las frases de huecos, los ejemplos de las diapositivas y los deberes cuenta como enseñado en clase, aunque solo salga de pasada, y se clasifica en su nivel del HSK como todo lo demás. Los nombres propios de los ejercicios y el vocabulario del aula (热身, 生词) no entran.
- **Las palabras de los ejercicios de pinyin** (listas para leer en voz alta, para oír tonos o finales: 篮球, 轮船, 惭愧) se enseñan por cómo suenan, no por lo que significan. Las útiles de HSK 1 y 2, y las muy cotidianas de HSK 3 (啤酒, 香蕉), entran para oír (`hear`), con su significado detrás; las demás esperan en el desván a que salgan en clase con su sentido, y las literarias o de registro escrito quedan fuera.

## Qué entra y qué sale primero

No se limita lo que entra: YAGO avanza y aprende cosas laterales, y todo lo que pasa el filtro entra en el diccionario, aunque la cola de nuevas de Anki crezca. Una tarjeta que aún no ha visto no le cuesta nada; lo que cuesta tiempo son los repasos, y Anki absorbe al ritmo que permite su tiempo (el ritmo vigente, en `docs/owner.md`). Lo que importa es el orden:

1. **Lo de clase, antes que nada y sea del nivel que sea.** Todo lo que viene de clase (diapositivas, deberes, sus apuntes de clase, lo que dijo la profesora) sale en Anki lo antes posible: es lo que trabaja con su profesora y lo que necesita para seguirla. Un 猜 de HSK 5 que salió el jueves va antes que un 给 de HSK 1 que aún no ha salido en clase. Las clases salen por dos colas a la vez, 7 de cada 10 tarjetas de la reciente y 3 de la atrasada: la reciente va de la clase más nueva hacia atrás, para que lo de esta semana salga enseguida y las clases de una misma semana, juntas; la atrasada va de la más antigua hacia delante, para que lo antiguo avance siempre aunque entre más de lo que estudia. Se encuentran en el medio. Lo que no es de clase pero va muy ligado a algo de una clase (lo que apunta en el review a raíz de ella) sale con esa clase. Hipótesis en prueba en `docs/hypotheses.md`.
2. **Después, el resto nivel a nivel**, con mucho énfasis en el HSK 1: dentro de cada nivel salen primero las tarjetas de lo que va a decir (`say`), luego lo que va a oír (`hear`) y al final lo que solo reconoce.

Por eso el `use` decide también la prioridad: lo lateral que no va a decir entra como `hear` o `read`, con menos tarjetas, y lo de clase, para decir (salvo las palabras que solo sirven para practicar sonidos, ver arriba).

## Cuánto y en qué proporción

El presupuesto es su tiempo, no el tamaño del mazo: de 20 a 40 minutos al día. De ahí salen las nuevas que puede abrir; lo que se vigila son los minutos al día y la mezcla, con tres reglas que el código mide (los valores, en `anki.py`):

- **Tarjetas de más, sin miedo**: la base la fija su `use`; encima, el agente crea toda tarjeta que vea útil para él (contrastes, matices, huecos, construir, oír las dos…) sin esperar a que la pida y sin ser parco. Las que crea por iniciativa propia las cuenta en el review, por si alguna sobra. `CARDS_PER_ITEM_MAX` queda como alarma para no inflar una palabra por descuido: pasarlo pide anotar el motivo (`accept_cards`), y que le sea útil basta.
- **Mezcla de lo que viene**: en las próximas `UPCOMING_NEW` nuevas, no en el mazo entero (con semanas de cola, el mazo no es lo que estudia), oír al menos un cuarto, decir al menos un cuarto, leer como mucho un tercio y el resto (contrastes, matices, estructuras) como mucho otro cuarto (`SKILL_TARGETS`). Es el pinyin por delante, en números; mientras toca aprender muchas palabras y sus hanzi, oír pesa menos y sale menos a menudo (`STREAM_WEIGHT`).
- **Cola de su nivel**: si las nuevas de su nivel pasan de `QUEUE_DAYS_MAX` días, lo que entra va más rápido de lo que estudia; no se frena la entrada (ver arriba), se mira qué sobra o qué baja de `use`.

**Siempre mezclado.** Cualquier tramo de nuevas trae de todo: oír, decir, leer y contrastes, y las frases desde el principio, no en bloques de un solo tipo (YAGO estudia de arriba abajo y un bloque de dictados seguidos cansa y no enseña a decir). Los pasos de una misma palabra (leer, oír, decir) salen separados un día de estudio (`STAGE_GAP` nuevas, las de un día a su ritmo).

Cada review trae, calculado, «Carga y equilibrio»: minutos al día, nuevas y palabras nuevas al día, días de cola y la mezcla frente al objetivo, con un punto por cada aviso. Las cifras se revisan con datos en la retrospectiva, no a ojo.

**Las de oír, retos.** Una tarjeta de oír tiene que costar: frases que mezclan vocabulario, aunque sean cortas, como las que dicta la profesora al empezar la clase (您贵姓？, 这个人是不是你的朋友？, 他二十二岁。), con números o con algo que se confunde al oído. Las fórmulas hechas que entiende cualquiera (谢谢！不客气。) no tienen tarjeta de oír. Una frase que ya practica para decir lleva la de oír solo si es de clase: al girar la de decir ya suena, pero descifrarla sin saber qué dice es lo que entrena el dictado de la profesora. Más adelante, cuando toque entender más que aprender palabras nuevas, las de oír crecerán. Hipótesis en prueba en `docs/hypotheses.md`.

## El pinyin por delante

Hablar depende del pinyin y de los tonos, no de los hanzi. YAGO tiende a investigar a fondo los caracteres después de clase y a descuidar el pinyin, así que el mazo compensa: lo nuevo se practica primero oyéndolo y diciéndolo (dictado, producción, tonos, frases en voz alta); el análisis de caracteres (componentes, origen, mnemotecnias) va como apoyo en el reverso y casi nunca como tarjeta propia. Las estructuras del pinyin (sílabas, finales, pares que se confunden) cuentan tanto como las palabras, y se practican de oído.

**La teoría de pronunciación no va en las tarjetas.** YAGO la estudia en su cuaderno de papel. Ninguna tarjeta está dedicada a una regla (cómo cambia un tono, dónde va la lengua, qué vocal suena), y ningún reverso la explica: ni las reglas de las entradas de pronunciación, ni trampas del pinyin, ni notas sobre el sandhi. Lo que sí entra, y mucho, es oír: parejas que suenan juntas, dictados, vocales para completar y tonos de cada palabra. Sus propias pistas de cómo suena una palabra (`sound`) se quedan, porque son suyas.

El pinyin es para él una herramienta, una forma de fijar lo que suena o lo que escribe antes de pasarlo a hanzi; no un sistema de escritura para leer. Por eso **leer es leer hanzi**: ninguna tarjeta le da a leer un texto solo en pinyin.

**Los tonos, también por color.** Recordar el tono de cada palabra es lo que más le cuesta, así que cada sílaba y su hanzi llevan el color de su tono allí donde se ve su pinyin, nunca donde la tarjeta lo pregunta. Hipótesis en prueba en `docs/hypotheses.md`.

Hablar se entrena sobre todo fuera del mazo: YAGO conversa con su profesora y lee en voz alta todo lo que estudia, también las tarjetas. Lo que aporta el mazo es el oído y el pinyin: dictado, tonos y audio en todo, y las parejas de tonos de dos sílabas, que son la base de sonar natural.

## Cómo se practican las frases

- **Construir: producción libre, pero con material y con modelos.** Es la tarjeta principal desde que empieza a formar frases, y entran varias en cada lote. Da unas cinco palabras que ya sabe y que combinan mucho entre sí (一下, 可以, 想, 请…) y una escena concreta, cotidiana pero poco habitual: en el metro, antes de empezar una reunión, cenando solo junto a otra mesa. Con esas palabras, o con otras que sepa, dice algo que encaje en la escena: no es ordenar, es crear. Detrás, tres o cuatro frases posibles con audio, cada una con otra mezcla de las palabras, para comparar. Se puntúa él; las frases suyas que le dejen con dudas las apunta en «Tus notas» y el agente las revisa en el lote. Solo palabras del mazo, y las escenas y las mezclas cambian de una tarjeta a otra para que no se memorice el reverso. Fuera de esta tarjeta, ninguna pide «di una frase con esta estructura» sin más: una estructura se practica oponiendo la frase buena a un calco claramente erróneo del español o del inglés (他很高 frente a 他是高), o a otra frase con la que se confunde. Hipótesis en prueba en `docs/hypotheses.md`.
- **Elegir entre opciones.** Cuando la pregunta es escoger lo que se dice en una situación (晚上好 o 晚安 a las once de la noche), las opciones van en la tarjeta con su letra (a, b, c…), alineadas a la izquierda, y detrás la buena con su audio.
- **Reutilizar, pero bien.** Las frases nuevas reutilizan el vocabulario del mazo siempre que se use con su sentido real; nunca se fuerza una palabra donde un nativo diría otra (大小 es «tamaño», no «talla»).
- **Sonar natural.** Si un apunte trae una forma correcta pero forzada (非常谢谢你), se corrige con ⚠️ hacia la natural (太谢谢你了, 非常感谢), y se dice cómo saluda de verdad la gente (早, 你回来了, 去哪里啊) frente a la fórmula de libro (你好吗).
- **Solo mandarín estándar.** Las formas del norte (erhua: 哪儿, 这儿), del cantonés o de otra región no entran, no se enseñan ni se mencionan, ni se guardan en el desván: se descartan (`use: drop`). Se usa la general: 哪里.
- **Una respuesta que se puede puntuar.** YAGO contesta de cabeza, gira y se puntúa: cada tarjeta pide una sola cosa con una respuesta corta. Lo que necesita un párrafo («¿cuándo cada uno?» con seis saludos) no es una tarjeta: se parte en situaciones o huecos, uno por uso.
- **Huecos, muchos.** El hueco en una frase es el formato que más rinde: obliga a producir y deja ver el contexto. Las reglas que confunden (不 / 没, 想 / 要 / 想要 / 需要 / 喜欢, 进来 / 进去, 会 / 回) tienen varios, uno por uso, con las opciones en la consigna («¿不 o 没?»).
- **Traducir con contexto.** Además de «dilo en chino», tarjetas que ponen una situación (alguien dice que le encantó la comida y tú también: 我也喜欢) para sacar lo que uno quiere decir. Si hay otra forma igual de buena de decirlo (我们是朋友 / 我和他是朋友), el reverso la da por buena: «También vale». A medida que suben los niveles, frases más largas que combinan lo ya aprendido (tiempos, lugares, encadenar acciones): el mazo debe leerse cada vez más como chino de verdad.
- **Monólogos y diálogos breves, en cada lote.** Cuatro o cinco frases por lote que juntan varias oraciones en una miniescena (你是谁？不对。你是什么东西？你为什么这么高？), solo con vocabulario de su nivel o inferior, para escuchar. Ayudan a entender trozos seguidos y a fijar estructuras en contexto; no más, porque una tarjeta larga se evalúa peor.
- **Comprensión lectora.** Un texto corto hecho con frases del mazo (tres o cuatro, de su nivel o inferior), en hanzi, que lee en voz alta de principio a fin; al terminar abre una pregunta sobre lo leído, en español o, cuando ya puede, en chino. Unas veces solo hanzi y otras con el pinyin encima, como apoyo; nunca solo pinyin. Al girar, la respuesta y el texto con pinyin, traducción y audio. Que haya al menos una por tema y nivel, y dos o tres más por lote con lo que ese lote trajo: es lo que hace que lo aprendido se lea como chino de verdad, y lo que más acerca a leer lo cotidiano.
- **Lo que se confunde, contrastado sin rodeos.** Cuando dos o más cosas se parecen mucho, en el hanzi (大/太/天), en el sonido (是 shì / 十 shí, 大家 / 大象) o en la idea (来 / 进; 不 / 没 / 别), se agrupan y tienen tarjeta propia de «¿cuál es…?» con todas las opciones juntas y el porqué (los hanzi que se parecen, juntos en la misma tarjeta: 对, 时, 的 y 狗); el nivel del contraste es el del miembro más difícil. Además, el reverso trae una frase de la pareja dentro de su fila del recuadro, nunca mezclada con los ejemplos. Fuera de su propia tarjeta, un grupo largo (las nueve palabras de pregunta) no se muestra: sería una lista, no un contraste. Hipótesis en prueba en `docs/hypotheses.md`.
- **Leer en voz alta.** Las tarjetas de lectura piden decir el hanzi en voz alta antes de girar, y el audio del reverso sirve para comparar.
- **Situaciones de calle.** Lo que se decide por la situación (请问, 不好意思, 对不起; 对, 是的, 好的) se pregunta con la situación delante y el grupo entero detrás, con audio. Las respuestas hechas (对不起, 没关系, 不客气, 你回来了, 吃了，你呢？) tienen además su tarjeta «Situación»: una escena en español y se contesta en voz alta.
- **Oír las dos y elegir.** Los pares que el español junta (shì / chī, chī / qī, sì / cì, zh / z, j / x, -n / -ng, chū / qù) se practican con las dos sílabas sonando en la misma tarjeta, una tras otra, y la pregunta de cuál es cuál: sin oír la otra, el oído no tiene con qué comparar. Detrás vuelven a sonar las dos, con su pinyin y su significado, sin explicar la regla. Son de lo más importante para hablar.
- **Sin tarjetas de teoría de pronunciación.** No hay tarjetas de «lee en voz alta» con el pinyin delante (YAGO ya imita cada audio del mazo) ni preguntas sobre una regla (¿cómo suena 一 aquí?): la teoría va en su cuaderno de papel (ver «El pinyin por delante»).
- **El reverso, de más a menos importante.** Primero la respuesta; después unos pocos ejemplos con audio; lo que ayuda a recordar (lo de clase, sus mnemotecnias, cómo suena, las notas), los recuadros de contraste y el porqué de cada hanzi, debajo. El orden exacto, en `docs/design.md`, «Tarjetas». Sin vocabulario de un nivel superior en los ejemplos ni en los recuadros.

## Cómo se explica un carácter

Condición indispensable en todo el mazo (tarjetas, cuaderno, log y review): que nunca se confunda lo que se usa con lo que solo ayuda a recordar.

- **Palabra, ligada o componente.** Cada carácter que es objetivo de una tarjeta muestra su estatus, calculado: **palabra** (se usa solo: 门, 来, 爱), **ligada** (solo dentro de palabras: 们, 师, 欢 en 喜欢) o **componente** (solo como parte de otros caracteres: 亻, 讠, 氵). En las tarjetas de palabras, el estatus de uno de sus caracteres se dice solo cuando engaña: 们 parece palabra y no lo es; 口 parece pieza y también es palabra. Un componente nunca se oye ni se dice: como mucho tiene una tarjeta para reconocerlo (si merece la pena, como 亻 o 氵) o la de contraste con otro que se le parece.
- **Mnemotecnia frente a origen.** Una mnemotecnia es una imagen para recordar y se dice que lo es; el origen real, cuando se conoce y está comprobado, va aparte.
- **Lo difícil, con su imagen.** Todo hanzi cuyo porqué no ayuda a recordarlo lleva una imagen para recordarlo, inventada por el agente a partir de su forma de hoy y rotulada como tal: el de origen discutido (que no se cuenta) y el que se usa solo por su sonido (来 «venir» era trigo; 我 «yo» era un arma). Es de lo más importante para YAGO: sin ella, esos hanzi solo se aprenden a pulso. Si el significado de una pieza vale para casi todos los caracteres donde aparece (讠 «hablar», 氵 «agua»), se dice; si solo sirve para uno, también.
- **Series fonéticas.** Cuando una pieza da el sonido (票 piào en 漂 piào, 半 bàn en 胖 pàng, 青 qīng en 请 qǐng, 门 mén en 们 men y 问 wèn), se señala: ver el hanzi debe evocar el sonido, y el sonido, el hanzi.
- **Conexiones cruzadas.** Relacionar lo nuevo con lo que ya hay (机 en 手机, 飞机 y 机票; 可 en 可爱 y 可以) ayuda a YAGO a recordar: se hace siempre que sea verdadero.
- **Un recuadro de «Conexión», como mucho, por tarjeta.** Con un código visual fijo según el tipo: 🔊 *da el sonido* (青 → 请, 清, 晴), 🧩 *da el significado* (讠 en 说, 请, 认识) o 👀 *se parece, pero no tiene que ver*. La conexión es del carácter: se escribe una vez, en su entrada propia, y la heredan las tarjetas de las palabras que lo llevan.
- **Solo con lo que ya sabe.** Una conexión enlaza solo con caracteres que ya están en el mazo, de su nivel o inferior: refuerza lo aprendido, no añade nada nuevo.
- **Calculado, no inventado.** Qué pieza da el sonido y cuál el significado sale de datos abiertos (`sources/hanzi/`, `anki.py hanzi`), no de la memoria del agente; el agente solo redacta. Una relación solo sale si es verdadera: el 马 de 妈 da el sonido, no el caballo.
- **Tarjetas, solo si se confunden de verdad.** Una relación va como nota; tarjeta propia (contraste) solo si los caracteres están en el mazo, son de su nivel y de verdad se confunden. Así el mazo no se infla.
- **Otros niveles.** Una nota puede mencionar palabras de niveles superiores para completar una familia, marcadas con su nivel entre corchetes («发票 fāpiào [HSK 4]»). Mencionarlas no las mete en el mazo.
- **Cada hanzi, su porqué.** Todo carácter del mazo tiene en `3-data/hanzi.yaml` su origen redactado: el dibujo o la idea si es pictograma o ideograma, qué pieza da el significado y cuál el sonido si es fonético-semántico (y si ese sonido aún se parece), o que no hay historia que contar cuando solo se usa por su sonido. Si el origen es discutido, no se cuenta: ni su historia ni su tipo; queda lo que significa y la imagen para recordarlo, rotulada como tal. El cuaderno web lo enseña al pasar el ratón por cualquier hanzi; el reverso de las tarjetas de palabras lo resume en «Sus caracteres»: lo mínimo de cada carácter (qué significa, una frase para recordarlo o su porqué, y en qué otras palabras del mazo sale).
- **La palabra de verdad.** Un componente no es una palabra, y se dice. Todo componente dice cuál es la palabra que se usa al hablar para su sentido y por qué, sobre todo cuando engaña: 目 es «ojo» solo dentro de otros caracteres, y al hablar se dice 眼睛; suelto, 口 no es la boca (eso es 嘴), sino un clasificador.
- **Ver el hanzi y oír su sílaba.** Leer pide asociar cada carácter con su sonido. Los que se repiten en varias palabras del mazo y no tienen tarjeta propia (学, 们, 怎) tienen una de «¿cómo suena?», y aparecen más a medida que crece el mazo.
- **Las expresiones, palabra a palabra.** Toda expresión hecha (你好, 不客气, 好久不见) lleva una línea «Palabra a palabra» con lo que aporta cada palabra y su traducción literal, para entenderla por dentro en vez de memorizarla entera.
- **Un hanzi solo, con su sonido y sus sentidos.** En las tarjetas de un solo carácter, qué otros caracteres del mazo suenan igual o casi (misma sílaba, mismo tono u otro) y qué otros sentidos tiene ese mismo hanzi: un carácter casi siempre tiene un solo sonido, pero una sílaba corresponde a muchos caracteres.
- **«En clase».** Lo que dijo la profesora se rotula «En clase» en las tarjetas, nunca «Profesora».

## Orden

Todo se ordena por dificultad, con los niveles del HSK 3.0 (del 1 al 6, más el 7 para los niveles 7 a 9): nivel oficial si la palabra está en la lista (`sources/hsk/`) y nivel estimado por el agente si no, con su motivo. Las reglas completas están en `docs/design.md`, «Niveles». YAGO estudia el mazo entero en este orden: lo de clase que llega de un nivel superior entra en su nivel, pero sale con lo de clase (ver «Qué entra y qué sale primero»); lo investigado de un nivel superior y poco conectado espera en el desván. Su nivel actual se calcula con lo que ya tiene, no con lo que declara.

## Huecos y propuestas

El agente no se limita a procesar lo que llega. En cada review señala, con criterio propio y no solo con listas:

- huecos temáticos: tiene mañana y noche, pero no tarde; sabe pedir, pero no pagar;
- lo básico de su nivel que aún falta (palabras, estructuras de frase, pronunciación);
- lo que más falla en Anki (`anki.py stats`) y qué cambiaría para fijarlo;
- las palabras del mazo que suenan parecido y aún no se contrastan (休息 / 学习), para que marque las que confunde;
- caracteres con una historia o descomposición que ayude a recordarlos;
- de vez en cuando, qué investigar a continuación para su nivel.

Y le avisa, con claridad y sin rebajarlo, cuando cruce de un nivel al siguiente.

## Las clases y la investigación propia

Los apuntes mezclan lo que da la profesora con lo que YAGO investiga por su cuenta, sobre todo caracteres. Lo de clase es lo prioritario y lo que marca el ritmo; lo investigado entra si pasa el filtro y conecta con lo que ya tiene, en su nivel; lo que es de más arriba y no conecta va al desván, y lo que solo explica otra palabra se queda como nota de esa palabra. Qué está dando la profesora en cada tramo se lleva en `2-digests/state.md`.

**Lo que pega de sus consultas.** Los exámenes, chuletas y explicaciones que le escribe un asistente y pega en «Tus notas» son investigación propia, no clase:

- entra lo de su nivel o uno por encima, con prioridad para los contrastes (las palabras que se confunden, cada una en su frase) y las frases cortas que combinan lo que ya sabe;
- lo de más arriba espera en el desván, con su explicación como nota;
- nada de ello adelanta a lo de clase en la cola;
- las explicaciones largas no pasan a las tarjetas: se resumen en una nota, un matiz o un hueco;
- una frase poco natural o de registro escrito se corrige o se descarta, como cualquier apunte.

**Los deberes son material.** Las hojas de deberes son material de la profesora para crear tarjetas: el agente las resuelve y usa sus soluciones como lo demás de clase, sin esperar ni pedir que YAGO las haga. Resolverlas y corregirlas es cosa de la profesora y de él; si una copia hecha trae sus respuestas, pueden servir para «Para entender».

## Cómo se le habla: el review

El review empieza por lo imprescindible, «Sine qua non»: lo poco que necesita contestar para que el siguiente lote salga bien, cada punto con su enlace al detalle. Todo lo demás se queda debajo, completo: contestar lo que le interese y buscar a partir de ahí es parte de cómo aprende. Directo y útil, no complaciente.

- **Cada punto, con su contexto**: de dónde viene (qué clase, qué diapositiva, qué apunte suyo, qué tarjeta), qué se hizo y por qué, para entenderlo sin abrir el log.
- **Con pinyin**: cada palabra en chino del review lleva su pinyin al lado (觉得 juéde), para leerlo sin buscar y para que el hanzi se asocie a su sonido.
- **Una minilección en cada review** («Para entender»): lo que el agente cree que le falta por entender, a partir de sus deberes corregidos, sus fallos en Anki y lo que se dio en clase, explicado en corto y con ejemplos del mazo. Son los ruedines de la profesora: no sustituyen a la clase, la acompañan.

## El sistema se ajusta

Si sus apuntes o sus respuestas muestran que otra forma de trabajar le serviría mejor (otra clase de tarjeta, otra regla, otro criterio), el agente la propone en el review; si YAGO la pide, se adopta. Cómo se registra el cambio: `docs/decisions.md`. Las indicaciones en mayúsculas o entre corchetes de sus apuntes son instrucciones sobre el sistema y se tratan así.

## Seguimiento

En cada lote, una reflexión acumulativa (el «Cómo vas» del review): su nivel, qué le están enseñando en clase y si encaja con este objetivo, cómo está estudiando visto a lo largo de los lotes, y un consejo concreto. Directa y útil, no complaciente. Formato y reglas: `docs/design.md`, «Seguimiento».
