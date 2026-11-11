# anki-order

An Anki add-on that lets `anki.py push` put the deck's new cards in their order. AnkiConnect no longer changes a
card's position (its October 2026 version refuses it as protected state and has no reposition action), so `push`
hands the positions to this add-on through a file and waits for its answer.

It only ever changes the position of a new card of the deck `anki.py` names in the request (`DECK_NAME`, today
`🌐 Language::🀄 Chino práctico`), and only if that deck's own name ends in `Chino práctico`; anything else in a request
is refused and listed in the answer.

Install: copy this folder into Anki's add-ons folder as `chino_practico_order`
(`%APPDATA%\Anki2\addons21\chino_practico_order` on Windows) and restart Anki. `anki.py push` says so if it is missing.
