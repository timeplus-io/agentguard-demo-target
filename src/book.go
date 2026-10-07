package main

// Book is a minimal two-sided order book keyed by price level.
type Book struct {
	Bids map[float64][]Order
	Asks map[float64][]Order
}

// Order is a resting limit order.
type Order struct {
	ID    string
	Side  string
	Price float64
	Qty   int
}

// Add places an order at its price level (FIFO within the level).
func (b *Book) Add(o Order) {
	if o.Side == "buy" {
		b.Bids[o.Price] = append(b.Bids[o.Price], o)
		return
	}
	b.Asks[o.Price] = append(b.Asks[o.Price], o)
}
