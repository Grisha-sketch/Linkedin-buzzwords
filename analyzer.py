import re
from buzzwords import BUZZWORDS


def normalize(text: str) -> str:
    return text.lower().strip()


def detect_buzzwords(text: str) -> list[dict]:
    normalized = normalize(text)
    found = []

    for word in BUZZWORDS:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        matches = pattern.findall(normalized)
        if matches:
            found.append({
                "buzzword": word,
                "count": len(matches),
            })

    return sorted(found, key=lambda x: x["count"], reverse=True)


def buzzword_score(found: list[dict], text: str) -> int:
    total_words = max(len(text.split()), 1)
    total_hits = sum(item["count"] for item in found)
    raw_score = (total_hits / total_words) * 100
    return min(int(raw_score * 10), 100)


def parse_posts(raw_text: str) -> list[str]:
    separator = re.compile(r'\n{2,}|---+')
    posts = separator.split(raw_text.strip())
    return [p.strip() for p in posts if len(p.strip()) > 20]


def analyze_posts(raw_text: str) -> list[dict]:
    posts = parse_posts(raw_text)
    results = []

    for i, post in enumerate(posts):
        found = detect_buzzwords(post)
        score = buzzword_score(found, post)
        results.append({
            "index": i + 1,
            "text": post,
            "buzzwords": found,
            "rule_based_score": score,
        })

    return results


def get_frequency_map(results: list[dict]) -> dict[str, int]:
    freq = {}
    for result in results:
        for item in result["buzzwords"]:
            word = item["buzzword"]
            freq[word] = freq.get(word, 0) + item["count"]
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))