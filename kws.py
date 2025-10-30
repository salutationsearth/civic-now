import os
from fuzzywuzzy import fuzz  

def news_agenda_fetch(folder_path, n=4):
    """
    Load the latest `n` agenda .txt files from a folder.
    Assumes filenames are date keys like 20251014.txt.
    Returns a dict: {date_key: {"link": str, "text": str}}
    """
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    if not all_files:
        raise FileNotFoundError("No .txt files found in folder.")

    # Sort descending (newest first)
    all_files.sort(reverse=True)

    latest_files = all_files[:n]
    agendas = []

    for fname in latest_files:
        path = os.path.join(folder_path, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Split into link + body (first nonempty line = link)
        parts = content.splitlines()
        link = parts[0].strip() if parts else ""
        text = "\n".join(parts[1:]).strip() if len(parts) > 1 else ""

        agendas.append({"link": link, "text": text})

    return agendas



def fuzzy_search(agendas, keywords):
    """
    Perform fuzzy search on the agenda text corpus and return
    the single best-matching agenda (dict with one entry).
    """

    best_match = [{}, {}, {}, {}]
    best_scores = [-99999, -99999, -99999, -99999]

    # rank the top 4 agenda by fuzz partial ratio score
    for agenda in agendas:
        text = agenda["text"].lower()
        score = fuzz.partial_ratio(text, keywords)
        
        for i in range(len(best_scores)):
            if score > best_scores[i]:
                best_match.insert(i, agenda)
                best_scores.insert(i, score)
                best_match.pop()
                best_scores.pop()
                break

    print(f"Best match score: {best_scores}")
    print(f"Best matches: {best_match}")

    # remove empty if the set of agenda length < 4
    best_match = [match for match in best_match if match != {}]

    return best_match if best_match else {}


if __name__ == "__main__":
    folder = "irvine_agendas_2025" 
    try:
        agendas = news_agenda_fetch(folder)
        print(f"Loaded {len(agendas)} latest agendas.\n")
        for k, v in agendas.items():
            print("→", k, v["link"])

        print("\n--- Fuzzy Search Test ---")
        kw1 = input("Keyword 1: ").strip()
        kw2 = input("Keyword 2: ").strip()
        kw3 = input("Keyword 3: ").strip()

        result = fuzzy_search(agendas, kw1, kw2, kw3)
        if result:
            for date, data in result.items():
                print(f"\nTop match: {date}")
                print(f"Link: {data['link']}\n")
                print(data["text"][:1000], "…")
        else:
            print("No match found.")
    except Exception as e:
        print("Error:", e)
