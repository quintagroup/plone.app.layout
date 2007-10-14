def quoteQuery(query):
    evil = ["(", ")"]

    for char in evil:
        query = query.replace(char, '"%s"' % char)

    return query

