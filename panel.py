import streamlit as st
from src.usecases.search import SearchQuery
from time import time


st.title("NEO-IR Search Panel")
st.subheader("Search documents using TF-IDF and Cosine Similarity.")

query = st.text_input("Enter your search query:")

page_size = st.selectbox("Results per page:", [5, 10, 20, 50], index=1)
page = st.number_input("Page number:", min_value=1, value=1, step=1)

search_query = SearchQuery()

if st.button("Search"):
    if query.strip():
        start_time = time()

        results = search_query.main(query=query, page=page, page_size=page_size)

        elapsed_time = time() - start_time

        st.success(f"Time token: {elapsed_time:.2f} seconds.")

        if results:
            for result in results:
                st.divider()
                st.text(f"{result['title']}")
                st.text(f"(Similarity: {result['similarity']:.4f})")
                st.write(f"[Read more]({result['url']})")
        else:
            st.warning("No results found!")
    else:
        st.error("Please enter a search query.")
