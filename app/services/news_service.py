import json


def get_news(query: str):
    with open("data/sample_news.json", "r", encoding="utf-8") as file:
        news = json.load(file)

    filtered_news = []

    for item in news:
        text = f"{item['title']} {item['description']}".lower()
        if query.lower() in text:
            filtered_news.append(item)

    if filtered_news:
        return filtered_news

    return news