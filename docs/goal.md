# Objetivo del que aprende

Este documento es un módulo de prompt: la única parte del sistema que depende de quién aprende. El agente lo lee antes de procesar un lote y lo aplica como primer filtro: con él decide qué entra, cuánto se practica, en qué orden y qué huecos señalar. Si algo de aquí choca con una regla de `docs/design.md` en lo que es del que aprende, manda este archivo.

**Qué va aquí y qué no.** Va lo que cambiaría con otra persona u otro objetivo: quién es, para qué estudia, qué entra, cómo quiere practicar y cómo quiere que se le hable. No va cómo funciona el sistema (`docs/design.md`), la configuración de su equipo y sus límites diarios (`docs/owner.md`), por qué o cuándo se decidió algo (`docs/decisions.md`) ni cómo va ahora (`2-digests/state.md`). Se escribe en presente, sin fechas. Para otra persona se reescribe este archivo y nada más.

## Quién aprende

YAGO, ingeniero, hispanohablante. Empezó mandarín en septiembre de 2026 con clases particulares que siguen un curso de HSK 1. Estudia en ratos sueltos, casi siempre en el móvil, con auriculares y teclado chino: el audio está disponible en cualquier sesión y puede escribir pinyin con tildes o hanzi.

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
- **Espera en el desván**: lo de su investigación propia que es de un nivel superior y está poco conectado, o lo que llega suelto sin frase. No entra aún, pero se guarda con todas sus notas y entra solo cuando llegue algo con lo que conecte (`docs/design.md`, «Desván»). Lo de clase nunca va al desván.
- **Queda fuera**: literario, arcaico, en desuso, variantes regionales que no son estándar y rarezas sin uso real. Se dice en el log y en el review, con el motivo, por si no está de acuerdo.
- Lo que viene de sus apuntes se respeta aunque no esté en ninguna lista, siempre que pase el filtro: si lo apuntó, suele ser porque lo necesita.

## Cuánto entra

Lo que entra en un lote tiene que caber en lo que puede estudiar antes del siguiente: a su ritmo de nuevas al día (`docs/owner.md`), las nuevas pendientes no deberían pasar de unas dos semanas de estudio. Si un lote trae más, primero lo de clase y lo básico de su nivel; lo demás entra con un `use` más bajo (`hear` en lugar de `say`) o espera, y el review lo dice. Un mazo con meses de nuevas pendientes retrasa justo lo que se acaba de ver en clase.

## El pinyin por delante

Hablar depende del pinyin y de los tonos, no de los hanzi. YAGO tiende a investigar a fondo los caracteres después de clase y a descuidar el pinyin, así que el mazo compensa: lo nuevo se practica primero oyéndolo y diciéndolo (dictado, producción, tonos, frases en voz alta); el análisis de caracteres (componentes, origen, mnemotecnias) va como apoyo en el reverso y casi nunca como tarjeta propia. Las estructuras del pinyin (sílabas, finales, pares que se confunden) cuentan tanto como las palabras.

El pinyin es para él una herramienta, una forma de fijar lo que suena o lo que escribe antes de pasarlo a hanzi; no un sistema de escritura para leer. Por eso **leer es leer hanzi**: ninguna tarjeta le da a leer un texto solo en pinyin.

Hablar se entrena sobre todo fuera del mazo: YAGO conversa con su profesora y lee en voz alta todo lo que estudia, también las tarjetas. Por eso el mazo no necesita muchas tarjetas de voz alta, y la pista de pronunciación no tiene prisa; lo que sí aporta el mazo es el oído y el pinyin: dictado, tonos y audio en todo.

## Cómo se practican las frases

- **Nada de producción libre.** Ninguna tarjeta pide «di una frase con esta estructura» o «inventa algo así»: obliga a ser creativo sin modelo y no educa. Una estructura se practica oponiendo la frase buena a un calco claramente erróneo del español o del inglés (他很高 frente a 他是高), o a otra frase con la que se confunde; así el oído aprende el orden del chino.
- **Reutilizar, pero bien.** Las frases nuevas reutilizan el vocabulario del mazo siempre que se use con su sentido real; nunca se fuerza una palabra donde un nativo diría otra (大小 es «tamaño», no «talla»).
- **Sonar natural.** Si un apunte trae una forma correcta pero forzada (非常谢谢你), se corrige con ⚠️ hacia la natural (太谢谢你了, 非常感谢), y se dice cómo saluda de verdad la gente (早, 你回来了, 去哪里啊) frente a la fórmula de libro (你好吗).
- **Solo mandarín estándar.** Las formas del norte (erhua: 哪儿, 这儿), del cantonés o de otra región no entran, no se enseñan ni se mencionan, ni se guardan en el desván: se descartan (`use: drop`). Se usa la general: 哪里.
- **Traducir con contexto.** Además de «dilo en chino», tarjetas que ponen una situación (alguien dice que le encantó la comida y tú también: 我也喜欢) para sacar lo que uno quiere decir. A medida que suben los niveles, frases más largas que combinan lo ya aprendido (tiempos, lugares, encadenar acciones): el mazo debe leerse cada vez más como chino de verdad.
- **Monólogos y diálogos breves, de vez en cuando.** Una o dos frases por lote que juntan varias oraciones en una miniescena (你是谁？不对。你是什么东西？你为什么这么高？), solo con vocabulario de su nivel o inferior, para escuchar. Ayudan a entender trozos seguidos y a fijar estructuras en contexto; no más, porque una tarjeta larga se evalúa peor.
- **Comprensión lectora.** Un texto corto hecho con frases del mazo (tres o cuatro, de su nivel o inferior), en hanzi, que lee en voz alta de principio a fin; al terminar abre una pregunta sobre lo leído, en español o, cuando ya puede, en chino. Unas veces solo hanzi y otras con el pinyin encima, como apoyo; nunca solo pinyin. Al girar, la respuesta y el texto con pinyin, traducción y audio. Dos o tres por lote, con lo que ese lote trajo: es lo que hace que lo aprendido se lea como chino de verdad.
- **Lo que se confunde, contrastado sin rodeos.** Cuando dos o más cosas se parecen mucho, en el hanzi (大/太/天), en el sonido (是 shì / 十 shí, 大家 / 大象) o en la idea (来 / 进; 不 / 没 / 别), se agrupan y tienen tarjeta propia de «¿cuál es…?» con todas las opciones y el porqué; el nivel del contraste es el del miembro más difícil. Además aparecen juntas en los ejemplos del reverso.
- **Leer en voz alta.** Las tarjetas de lectura piden decir el hanzi en voz alta antes de girar, y el audio del reverso sirve para comparar.
- **Situaciones de calle.** Lo que se decide por la situación (请问, 不好意思, 对不起; 对, 是的, 好的) se pregunta con la situación delante y el grupo entero detrás, con audio.

## Cómo se explica un carácter

Condición indispensable en todo el mazo (tarjetas, cuaderno, log y review): que nunca se confunda lo que se usa con lo que solo ayuda a recordar.

- **Palabra, ligada o componente.** Cada carácter que es objetivo de una tarjeta muestra su estatus, calculado: **palabra** (se usa solo: 门, 来, 爱), **ligada** (solo dentro de palabras: 们, 师, 欢 en 喜欢) o **componente** (solo como parte de otros caracteres: 亻, 讠, 氵). En las tarjetas de palabras, el estatus de uno de sus caracteres se dice solo cuando engaña: 们 parece palabra y no lo es; 口 parece pieza y también es palabra. Un componente nunca se oye ni se dice: como mucho tiene una tarjeta para reconocerlo (si merece la pena, como 亻 o 氵) o la de contraste con otro que se le parece.
- **Mnemotecnia frente a origen.** Una mnemotecnia es una imagen para recordar y se dice que lo es; el origen real, cuando se conoce y está comprobado, va aparte. Si el significado de una pieza vale para casi todos los caracteres donde aparece (讠 «hablar», 氵 «agua»), se dice; si solo sirve para uno, también.
- **Series fonéticas.** Cuando una pieza da el sonido (票 piào en 漂 piào, 半 bàn en 胖 pàng, 青 qīng en 请 qǐng, 门 mén en 们 men y 问 wèn), se señala: ver el hanzi debe evocar el sonido, y el sonido, el hanzi.
- **Conexiones cruzadas.** Relacionar lo nuevo con lo que ya hay (机 en 手机, 飞机 y 机票; 可 en 可爱 y 可以) ayuda a YAGO a recordar: se hace siempre que sea verdadero.
- **Un recuadro de «Conexión», como mucho, por tarjeta.** Con un código visual fijo según el tipo: 🔊 *da el sonido* (青 → 请, 清, 晴), 🧩 *da el significado* (讠 en 说, 请, 认识) o 👀 *se parece, pero no tiene que ver*. La conexión es del carácter: se escribe una vez, en su entrada propia, y la heredan las tarjetas de las palabras que lo llevan.
- **Solo con lo que ya sabe.** Una conexión enlaza solo con caracteres que ya están en el mazo, de su nivel o inferior: refuerza lo aprendido, no añade nada nuevo.
- **Calculado, no inventado.** Qué pieza da el sonido y cuál el significado sale de datos abiertos (`sources/hanzi/`, `anki.py hanzi`), no de la memoria del agente; el agente solo redacta. Una relación solo sale si es verdadera: el 马 de 妈 da el sonido, no el caballo.
- **Tarjetas, solo si se confunden de verdad.** Una relación va como nota; tarjeta propia (contraste) solo si los caracteres están en el mazo, son de su nivel y de verdad se confunden. Así el mazo no se infla.
- **Otros niveles.** Una nota puede mencionar palabras de niveles superiores para completar una familia, marcadas con su nivel entre corchetes («发票 fāpiào [HSK 4]»). Mencionarlas no las mete en el mazo.
- **«En clase».** Lo que dijo la profesora se rotula «En clase» en las tarjetas, nunca «Profesora».

## Orden

Todo se ordena por dificultad, con los niveles del HSK 3.0 (del 1 al 6, más el 7 para los niveles 7 a 9): nivel oficial si la palabra está en la lista (`sources/hsk/`) y nivel estimado por el agente si no, con su motivo. Las reglas completas están en `docs/design.md`, «Niveles». YAGO estudia nivel a nivel y respeta esta ordenación: lo de clase que llega de un nivel superior entra en su nivel y espera; lo investigado de un nivel superior y poco conectado espera en el desván. Su nivel actual se calcula con lo que ya tiene, no con lo que declara.

## Huecos y propuestas

El agente no se limita a procesar lo que llega. En cada review señala, con criterio propio y no solo con listas:

- huecos temáticos: tiene mañana y noche, pero no tarde; sabe pedir, pero no pagar;
- lo básico de su nivel que aún falta (palabras, estructuras de frase, pronunciación);
- lo que más falla en Anki (`anki.py stats`) y qué cambiaría para fijarlo;
- caracteres con una historia o descomposición que ayude a recordarlos;
- de vez en cuando, qué investigar a continuación para su nivel.

Y le avisa, con claridad y sin rebajarlo, cuando cruce de un nivel al siguiente.

## Las clases y la investigación propia

Los apuntes mezclan lo que da la profesora con lo que YAGO investiga por su cuenta, sobre todo caracteres. Lo de clase es lo prioritario y lo que marca el ritmo; lo investigado entra si pasa el filtro y conecta con lo que ya tiene, en su nivel; lo que es de más arriba y no conecta va al desván, y lo que solo explica otra palabra se queda como nota de esa palabra. Qué está dando la profesora en cada tramo se lleva en `2-digests/state.md`.

## Cómo se le habla: el review

El review empieza por lo imprescindible, «Sine qua non»: lo poco que necesita contestar para que el siguiente lote salga bien, cada punto con su enlace al detalle. Todo lo demás se queda debajo, completo: contestar lo que le interese y buscar a partir de ahí es parte de cómo aprende. Directo y útil, no complaciente.

## El sistema se ajusta

Si sus apuntes o sus respuestas muestran que otra forma de trabajar le serviría mejor (otra clase de tarjeta, otra regla, otro criterio), el agente la propone en el review; si YAGO la pide, se adopta. Cómo se registra el cambio: `docs/decisions.md`. Las indicaciones en mayúsculas o entre corchetes de sus apuntes son instrucciones sobre el sistema y se tratan así.

## Seguimiento

En cada lote, una reflexión acumulativa (el «Cómo vas» del review): su nivel, qué le están enseñando en clase y si encaja con este objetivo, cómo está estudiando visto a lo largo de los lotes, y un consejo concreto. Directa y útil, no complaciente. Formato y reglas: `docs/design.md`, «Seguimiento».
