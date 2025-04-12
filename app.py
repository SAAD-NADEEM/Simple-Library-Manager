import streamlit as st
import json
from pathlib import Path

# Initialize the books data file
DATA_FILE = "books_data.json"


# Create the file with empty list if it doesn't exist or is empty
def initialize_data_file():
    if not Path(DATA_FILE).exists() or Path(DATA_FILE).stat().st_size == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)


# Load books from JSON file with error handling
def load_books():
    initialize_data_file()  # Ensure file exists and is not empty
    try:
        with open(DATA_FILE, "r") as f:
            books = json.load(f)
            return books if isinstance(books, list) else []
    except json.JSONDecodeError:
        return []  # Return empty list if file is corrupted


# Save books to JSON file
def save_books(books):
    with open(DATA_FILE, "w") as f:
        json.dump(books, f)


# Add a new book
def add_book(title, author, year, genre, read_status):
    books = load_books()
    new_book = {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "read_status": read_status,
    }
    books.append(new_book)
    save_books(books)


# Remove a book by title
def remove_book(title):
    books = load_books()
    updated_books = [book for book in books if book["title"].lower() != title.lower()]
    save_books(updated_books)
    return len(updated_books)


# Search books by title or author
def search_books(query):
    books = load_books()
    query = query.lower()
    return [
        book
        for book in books
        if query in book["title"].lower() or query in book["author"].lower()
    ]


# Get all books
def get_all_books():
    return load_books()


# Get library statistics
def get_stats():
    books = load_books()
    total = len(books)
    read = sum(1 for book in books if book["read_status"])
    percentage = (read / total * 100) if total > 0 else 0

    genres = {}
    for book in books:
        genre = book["genre"]
        genres[genre] = genres.get(genre, 0) + 1

    return {"total": total, "read_percentage": percentage, "genres": genres}


# Streamlit App
def main():
    st.title("📚 Simple Library Manager")

    # Sidebar with all options permanently visible
    st.markdown(
        """
    <style>
    .sidebar-button {
        display: block;
        width: 100%;
        padding: 0.75rem 1rem;
        margin: 0.3rem 0;
        text-align: left;
        background-color: #f0f2f6;
        color: #333;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: 0.3s ease;
    }
    .sidebar-button:hover {
        background-color: #e4e8f0;
    }
    .sidebar-button.selected {
        background-color: #2c6df2;
        color: white;
    }
    </style>
""",
        unsafe_allow_html=True,
    )


    # Session state to track current page
    if "menu_option" not in st.session_state:
        st.session_state.menu_option = "Add Book"

    menu_items = ["Add Book", "Remove Book", "Search Books", "View All Books", "Statistics"]

    with st.sidebar:
        st.header("📚 Library Menu")
        for item in menu_items:
            btn_class = "sidebar-button"
            if st.session_state.menu_option == item:
                btn_class += " selected"
            if st.button(item, key=item):
                st.session_state.menu_option = item

    # Main content render
    if st.session_state.menu_option == "Add Book":
        show_add_page()
    elif st.session_state.menu_option == "Remove Book":
        show_remove_page()
    elif st.session_state.menu_option == "Search Books":
        show_search_page()
    elif st.session_state.menu_option == "View All Books":
        show_view_page()
    elif st.session_state.menu_option == "Statistics":
        show_stats_page()


def show_add_page():
    st.header("Add a New Book")
    with st.form("add_form"):
        title = st.text_input("Title*", help="Required field")
        author = st.text_input("Author*", help="Required field")
        year = st.number_input(
            "Publication Year*", min_value=1800, max_value=2025, value=2023
        )
        genre = st.text_input("Genre", "General", help="Leave as 'General' if unsure")
        read = st.checkbox("I've read this book")

        if st.form_submit_button("Add Book"):
            if title.strip() and author.strip():
                add_book(title.strip(), author.strip(), year, genre.strip(), read)
                st.success("Book added successfully!")
            else:
                st.warning("Please fill in all required fields (marked with *)")


def show_remove_page():
    st.header("Remove a Book")
    books = load_books()

    if not books:
        st.info("Your library is currently empty - no books to remove")
    else:
        title = st.text_input("Enter the exact book title to remove")

        if st.button("Remove Book"):
            if title.strip():
                initial_count = len(books)
                remove_book(title.strip())
                if len(load_books()) < initial_count:
                    st.success(f"Book '{title}' was removed successfully")
                else:
                    st.warning(f"No book found with title '{title}'")
            else:
                st.warning("Please enter a book title")


def show_search_page():
    st.header("Search Books")
    books = load_books()

    if not books:
        st.info("Your library is currently empty - no books to search")
    else:
        query = st.text_input("Search by book title or author name")

        if query.strip():
            results = search_books(query.strip())
            if results:
                st.write(f"Found {len(results)} matching book(s):")
                for book in results:
                    status = "✓ Read" if book["read_status"] else "✗ Unread"
                    st.write(
                        f"""
                    **{book['title']}**  
                    *by {book['author']}* ({book['year']})  
                    Genre: {book['genre']} | Status: {status}
                    """
                    )
                    st.write("---")
            else:
                st.info("No books found matching your search")


def show_view_page():
    st.header("Your Book Collection")
    books = load_books()

    if not books:
        st.info("Your library is currently empty - add some books to get started!")
    else:
        st.write(f"You have {len(books)} book(s) in your collection:")
        for i, book in enumerate(books, 1):
            status = "✓ Read" if book["read_status"] else "✗ Unread"
            st.write(
                f"""
            {i}. **{book['title']}**  
            *by {book['author']}* ({book['year']})  
            Genre: {book['genre']} | Status: {status}
            """
            )
            st.write("---")


def show_stats_page():
    st.header("Library Statistics")
    books = load_books()

    if not books:
        st.info("Your library is currently empty - no statistics to display")
    else:
        stats = get_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Books", stats["total"])
        with col2:
            st.metric("Read Percentage", f"{stats['read_percentage']:.1f}%")

        if stats["genres"]:
            st.subheader("Books by Genre")
            for genre, count in stats["genres"].items():
                st.write(f"- **{genre}**: {count} book(s)")


if __name__ == "__main__":
    initialize_data_file()  # Ensure file exists before starting
    main()
