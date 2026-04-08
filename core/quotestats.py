from my_types.quote_types import QuoteHistory
import re


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
    

    def count_total_quotes(self, known_users: list[str]) -> list[tuple[str, int]]:
        result: dict[str, int] = {}

        for quote_chain in self.history:
            for quote_part in quote_chain:
                author_data = quote_part[1]

                matches = []
                for user in known_users:
                    match = re.search(r'\b' + re.escape(user) + r'\b', author_data, re.IGNORECASE)
                    if match:
                        matches.append((match.start(), user))

                if not matches:
                    continue

                _, matched_user = min(matches, key=lambda pair: pair[0])
                result[matched_user] = result.get(matched_user, 0) + 1

        return sorted(result.items(), key=lambda item: item[1], reverse=True)