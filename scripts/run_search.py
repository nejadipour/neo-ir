from src.usecases.search import SearchQuery
import json

sq = SearchQuery()
result = sq.main(query='دیروز امروز')

print(json.dumps(result, indent=4, ensure_ascii=False))
