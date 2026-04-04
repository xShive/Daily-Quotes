from my_types.quote_types import QuoteHistory

class QuoteStats:
    def __init__(self, history: QuoteHistory):
        self.history = history
    
    def count_quotes_made(self) -> dict[int, int]:
        result = {}

        for quote_chain in self.history:
            for quote_part in quote_chain:
                author = quote_part[1][1:]
