import csv

from models.venue import Venue


def is_duplicate_venue(venue_name: str, seen_names: set) -> bool:
    return venue_name in seen_names


def is_complete_venue(venue: dict, required_keys: list) -> bool:
    return all(key in venue for key in required_keys)


def save_venues_to_csv(venues: list, filename: str):
    if not venues:
        print("No venues to save.")
        return

    # Define a header that includes the new fields
    fieldnames = ["title", "url", "snippet", "emails", "contact_links", "summary"]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for venue in venues:
            writer.writerow({
                "title": venue.get("title", ""),
                "url": venue.get("url", ""),
                "snippet": venue.get("snippet", ""),
                "emails": ";".join(venue.get("emails", [])) if isinstance(venue.get("emails", []), list) else venue.get("emails", ""),
                "contact_links": ";".join(venue.get("contact_links", [])) if isinstance(venue.get("contact_links", []), list) else venue.get("contact_links", ""),
                "summary": venue.get("summary", ""),
            })
    print(f"Saved {len(venues)} venues to '{filename}'.")