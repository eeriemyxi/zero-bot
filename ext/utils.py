def parse_desc(text: str, limit: int):
    if len(text) > limit:
        return text[:limit] + "..."
    else:
        return text

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]