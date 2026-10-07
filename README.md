# Orderbook Service

A small Go service that keeps an in-memory order book for the demo exchange and
exposes it over HTTP. Orders arrive as JSON, are matched FIFO per price level,
and fills are published to a Timeplus stream.

- `src/book.go` — the order book (price levels, FIFO queues)
- `src/server.go` — HTTP handlers: `POST /orders`, `GET /book`
- `src/publish.go` — fill publisher (Timeplus REST ingest)

Build with `go build ./...`. Configuration comes from `config.yaml`.
