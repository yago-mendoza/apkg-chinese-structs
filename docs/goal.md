# Objetivo del que aprende

Este documento es un módulo de prompt: la única parte del sistema que depende de quién aprende. El agente lo lee antes de procesar un lote y lo aplica como primer filtro: con él decide qué entra, cuánto se practica, en qué orden y qué huecos señalar. `docs/design.md` dice cómo funciona todo y no recoge preferencias personales; para adaptar el sistema a otra persona u otro objetivo, se reescribe este archivo y nada más. Si algo de aquí choca con una regla de `design.md` en lo que es del que aprende, manda este archivo.

## Quién aprende

YAGO, ingeniero, hispanohablante. Empezó mandarín en septiembre de 2026 con clases particulares que siguen un curso de HSK 1. Estudia en ratos sueltos, casi siempre en el móvil, con auriculares y teclado chino: el audio está disponible en cualquier sesión y puede escribir pinyin con tildes o hanzi.

## Para qué

Hablar chino. No es preparar el examen del HSK: el HSK sirve de escala para ordenar, no de meta. Llegar a un nivel equivalente a C1 con **mucho énfasis en fluidez y en pronunciación**, para:

- conversación cotidiana, con naturalidad y algo de personalidad;
- trabajo y negocios: es ingeniero; reuniones, trato profesional, vocabulario técnico cuando llegue;
- vivir en China: transporte, compras, comida, casa, salud, trámites, aplicaciones;
- viajar;
- leer y entender lo que aparece en ese día a día (carteles, menús, mensajes).

## Filtro de lo que entra

Cada elemento de los apuntes se juzga contra el «para qué» de arriba:

- **Entra para decir** (`say`): lo que usaría hablando en esas situaciones.
- **Entra para entender** (`hear` o `read`): lo que oirá o leerá pero no necesita producir (registro formal, carteles, fórmulas escritas).
- **Queda fuera**: literario, arcaico, en desuso, variantes regionales que no son estándar y rarezas sin uso real. Se dice en el log y en el review, con el motivo, por si no está de acuerdo.
- Lo que viene de sus apuntes se respeta aunque no esté en ninguna lista, siempre que pase el filtro: si lo apuntó, suele ser porque lo necesita.

## El pinyin por delante

Hablar depende del pinyin y de los tonos, no de los hanzi. YAGO tiende a investigar a fondo los caracteres después de clase y a descuidar el pinyin (lo dijo él, 2026-09-29), así que el mazo compensa: lo nuevo se practica primero oyéndolo y diciéndolo (dictado, producción, tonos, frases en voz alta); el análisis de caracteres (componentes, origen, mnemotecnias) va como apoyo en el reverso y casi nunca como tarjeta propia. Las estructuras del pinyin (sílabas, finales, pares que se confunden) cuentan tanto como las palabras.

## Cómo se explica un carácter

Condición indispensable en todo el mazo (tarjetas, cuaderno, log y review): que nunca se confunda lo que se usa con lo que solo ayuda a recordar.

- **Palabra, ligada o componente.** Cada hanzi que aparece se presenta con su estatus: **palabra** (se usa solo: 门, 来, 爱), **ligada** (solo dentro de palabras: 们, 师, 欢 en 喜欢) o **componente** (solo como parte de otros caracteres: 亻, 讠, 氵). Un componente nunca se oye ni se dice: como mucho tiene una tarjeta para reconocerlo (si merece la pena, como 亻 o 氵) o la de contraste con otro que se le parece.
- **Mnemotecnia frente a origen.** Una mnemotecnia es una imagen para recordar y se dice que lo es; el origen real, cuando se conoce y está comprobado, va aparte. Si el significado de una pieza vale para casi todos los caracteres donde aparece (讠 «hablar», 氵 «agua»), se dice; si solo sirve para uno, también.
- **Series fonéticas.** Cuando una pieza da el sonido (票 piào en 漂 piào, 半 bàn en 胖 pàng, 青 qīng en 请 qǐng, 门 mén en 们 men y 问 wèn), se señala: ver el hanzi debe evocar el sonido, y el sonido, el hanzi.
- **Conexiones cruzadas.** Relacionar lo nuevo con lo que ya hay (机 en 手机, 飞机 y 机票; 可 en 可爱 y 可以) ayuda a YAGO a recordar: se hace siempre que sea verdadero.
- **Otros niveles.** Una nota puede mencionar palabras de niveles superiores para completar una familia, marcadas con su nivel entre corchetes («发票 fāpiào [HSK 4]»). Mencionarlas no las mete en el mazo.

## Orden

Todo se ordena por dificultad, con los niveles del HSK 3.0 (del 1 al 6, más el 7 para los niveles 7 a 9): nivel oficial si la palabra está en la lista (`sources/hsk/`) y nivel estimado por el agente si no, con su motivo. Las reglas completas están en `docs/design.md`, «Niveles». YAGO estudia nivel a nivel y respeta esta ordenación: lo que llega de un nivel superior se guarda en su nivel y espera. Su nivel actual se calcula con lo que ya tiene, no con lo que declara.

## Huecos y propuestas

El agente no se limita a procesar lo que llega. En cada review señala, con criterio propio y no solo con listas:

- huecos temáticos: tiene mañana y noche, pero no tarde; sabe pedir, pero no pagar;
- lo básico de su nivel que aún falta (palabras, estructuras de frase, pronunciación);
- caracteres con una historia o descomposición que ayude a recordarlos;
- de vez en cuando, qué investigar a continuación para su nivel.

Y le avisa, con claridad y sin rebajarlo, cuando cruce de un nivel al siguiente.

## Las clases y la investigación propia

Los apuntes mezclan lo que da la profesora (hasta 2026-09-29: saludos, adjetivos con 很, el tiempo, apellidos y nombres) con lo que YAGO investiga por su cuenta, sobre todo caracteres. Lo de clase es lo prioritario y lo que marca el ritmo; lo investigado entra si pasa el filtro y en su nivel, y el resto se queda como nota o fuera, con el motivo.

## El sistema se ajusta solo

Si los apuntes o las respuestas de YAGO muestran que otra forma de trabajar le serviría mejor (otra clase de tarjeta, otra regla, otro criterio), el agente la adopta: la escribe en este documento o en `docs/design.md` y la cuenta en el log del lote, en «Cambios en el sistema». Las indicaciones en mayúsculas o entre corchetes de sus apuntes son instrucciones sobre el sistema y se tratan así.

## Seguimiento

En cada lote, además, una reflexión acumulativa (el «Cómo vas» del review): su nivel, qué le están enseñando en clase y si encaja con este objetivo, cómo está estudiando visto a lo largo de los lotes, y un consejo concreto. Directa y útil, no complaciente. Formato y reglas: `docs/design.md`, «Seguimiento».
