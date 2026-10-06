# records

What the review app (`tools/review/serve.py`) records of YAGO: `review-log.jsonl`, one JSON event per line, append only. Events: `approved` and `unapproved` (with the hash of the text he approved), `note` (a request, with its text) and `cleared`, `applied` (a request attended) and `caused` (that request made the agent change or create another item: `from`, `to`, `what`). The history of the data is not stored here: the app derives it from git each time.
