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
        return sorted(result.items(), key=lambda item: item[1], reverse=True)


    def count_total_quotes(self) -> list[tuple[str, int]]:
        result: dict[str, int] = {}

        for quote_chain in self.history:
            for quote_part in quote_chain:
                author_date = quote_part[1]

                # Check for substrings
                for name in result.keys():
                    if name in author_date:
                        result[name] += 1

                # If substring check fails
                name = author_date.split(' ')[0]
                if ',' in name:
                    name = name.replace(',', '')
                


                result[name.lower()] = result.get(name.lower(), 0) + 1

        print(sorted(result.items(), key=lambda item: item[1], reverse=True))
        return sorted(result.items(), key=lambda item: item[1], reverse=True)

