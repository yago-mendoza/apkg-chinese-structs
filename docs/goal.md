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

## Orden

Todo se ordena por dificultad, con los niveles del HSK 3.0 (del 1 al 6, más el 7 para los niveles 7 a 9): nivel oficial si la palabra está en la lista (`sources/hsk/`) y nivel estimado por el agente si no, con su motivo. Las reglas completas están en `docs/design.md`, «Niveles». YAGO estudia nivel a nivel y respeta esta ordenación: lo que llega de un nivel superior se guarda en su nivel y espera. Su nivel actual se calcula con lo que ya tiene, no con lo que declara.

## Huecos y propuestas

El agente no se limita a procesar lo que llega. En cada review señala, con criterio propio y no solo con listas:

- huecos temáticos: tiene mañana y noche, pero no tarde; sabe pedir, pero no pagar;
- lo básico de su nivel que aún falta (palabras, estructuras de frase, pronunciación);
- caracteres con una historia o descomposición que ayude a recordarlos;
- de vez en cuando, qué investigar a continuación para su nivel.

Y le avisa, con claridad y sin rebajarlo, cuando cruce de un nivel al siguiente.
