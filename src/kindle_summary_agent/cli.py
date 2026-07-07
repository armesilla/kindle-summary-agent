from kindle_summary_agent.clients.readwise import ReadwiseClient


def main() -> None:
    client = ReadwiseClient()

    if not client.validate():
        raise RuntimeError("Invalid Readwise token")

    books = client.get_books()

    print("✅ Readwise token válido")
    print(f"📚 Libros encontrados: {len(books)}")

    for book in books[:5]:
        print(f"- {book.title} ({book.highlight_count} highlights)")


if __name__ == "__main__":
    main()