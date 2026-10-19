2026-10-18

Para este lote: separar las frases en fórmulas y ejemplos

Hay dos clases de frase mezcladas en el mazo y quiero que este lote las separe, siguiendo el método del repositorio y sin cambiar cómo aprendo ni qué piden las tarjetas.

El problema. Hoy el tema de una frase es el archivo donde vive, y eso no distingue entre:
- Fórmulas: frases que se usan tal cual en muchas situaciones, sin construirlas: 这个怎么样？, 好久不见, 你吃饭了吗？, 慢慢来, 我很好，你呢？. Su sitio natural es la situación (saludar, pedir, disculparse). Una fórmula puede tener un hueco (X怎么样？) y sigue siendo fórmula.
- Ejemplos: frases que enseñan cómo funciona una palabra o una estructura, con un contenido concreto: 谢谢你的礼物！ es un ejemplo de 谢谢 + 的 + 礼物, no un saludo. Son útiles, pero no pertenecen a ninguna situación: su sitio son las palabras que ilustran, que ya enlazan con segments.
Por eso en 3-data/sentences/saludos.yaml acabaron «¡Gracias por tu regalo!», «Por la mañana tomo té», «¿Qué tal este?» o «Últimamente estoy muy liado», que entraron en bloque con el lote 005-2026-10-05-saludos-y-sonidos.

Lo que pido:
1. Diseño. Un campo por frase (por ejemplo kind: formula | example) y la regla para decidirlo, escrita en docs/design.md y con su porqué en docs/decisions.md. Decide también qué pasa con los temas. Prefiero lo que menos mueva las tarjetas: si basta con marcar kind y dejar los ejemplos en el archivo del tema de su palabra principal, mejor que moverlos; si mover compensa, dime cuántas tarjetas cambiarían de subdeck y confirma que push conserva el progreso. Que la exportación (dictionary.json) lleve el campo en cada frase como añadido compatible (schemaVersion sigue en 2), y que check avise de una frase sin kind. La web (infraphysics) lo usará para que cada tema muestre solo sus fórmulas y los ejemplos salgan en la ficha de cada palabra.
2. Clasificación. Recorre todas las frases de 3-data/sentences/ y propón el kind de cada una; si alguna fórmula está en un tema que no es su situación, propón a cuál va. No lo apliques todavía: déjalo en el review de este lote como una tabla por tema (id, hanzi, traducción, kind propuesto, tema propuesto si cambia), con las dudosas aparte y su motivo, y enlazado desde «Sine qua non». Yo corregiré solo lo que esté mal.
3. Aplicación. Cuando conteste el review, aplícalo en el lote siguiente como una reorganización normal: contado en el log, check sin errores, push y cierre como siempre.

Límites: no cambies lo que piden las tarjetas, ni el use de nada, ni su formato. No borres frases ni reutilices IDs. Pregunta lo ambiguo en vez de adivinar.
