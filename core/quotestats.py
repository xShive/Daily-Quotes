from my_types.quote_types import QuoteHistory


class QuoteStats:
    def __init__(self, history: QuoteHistory):
        self.history = history
    

    def count_quotes_made(self) -> list[tuple[int, int]]:
        result: dict[int, int] = {}

        for quote_chain in self.history:
            for quote_part in quote_chain:      # AUTHOR = 4587654327
                author = quote_part[2]
                result[author] = result.get(author, 0) + 1
        
        # sort by value
        sender_data = sorted(result.items(), key=lambda item: item[1], reverse=True)

        
        return sender_data
