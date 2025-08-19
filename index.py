from __future__ import annotations

import streamlit as st
from streamlit_option_menu import option_menu

from app.ui.layout import render_top_nav, apply_global_styles
from app.pages.chatbot import chatbot_interface_ui, manage_collections_ui
from app.pages.pdf_to_mongo import pdf_to_mongodb_page
from app.pages.mongo_audit import edit_mongodb_document
from app.pages.mongo_viewer import db_image_page
from app.pages.finance_hub import business_metrics_dashboard


def main():
    # --- PAGE CONFIGURATION ---
    st.set_page_config(page_title="EnterRAG", page_icon="💼", layout="centered")

    # --- MAIN PAGE CONFIGURATION ---
    st.title("EnterRAG 💼")
    st.write("*Talk to your Enterprise Documents 📄, Receive Insights: AI. Unlocked.*")
    st.write(':blue[***Powered by LangChain***]')

    # Initialize current page once to avoid widget state glitches
    if "page" not in st.session_state:
        st.session_state.page = "AI Chatbot"

    # ---- NAVIGATION MENU -----
    selected = option_menu(
        menu_title=None,
        options=["Info", "About"],
        icons=["bi bi-info-square", "bi bi-globe"],  # https://icons.getbootstrap.com
        orientation="horizontal",
    )

    # Custom CSS for buttons
    st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #0E1117;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        color : black
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation with a compact, icon-based menu
    with st.sidebar:
        st.title("Navigation")

        page_options = [
            "AI Chatbot",
            "Manage Collections",
            "Store PDF to MongoDB",
            "Audit Data on MongoDB",
            "View MongoDB Documents",
            "Strategic Financial Intelligence Hub",
        ]

        # Icons for each page (Bootstrap Icons)
        page_icons = [
            "chat-dots",
            "folder",
            "cloud-upload",
            "pencil-square",
            "table",
            "bar-chart",
        ]

        # Determine current index
        try:
            current_index = page_options.index(st.session_state.page)
        except ValueError:
            current_index = 0

        selected_page = option_menu(
            menu_title=None,
            options=page_options,
            icons=page_icons,
            menu_icon="list",
            default_index=current_index,
            orientation="vertical",
            styles={
                "container": {"padding": "0", "background-color": "rgba(0,0,0,0)"},
                "icon": {"color": "#4EA8DE", "font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "padding": "8px 10px",
                    "margin": "3px 0",
                    "border-radius": "6px",
                    "color": "#FAFAFA",
                },
                "nav-link-selected": {"background-color": "#2b2b2b"},
            },
        )
        # Rerun only when the selection changes to ensure single-click navigation
        prev_page = st.session_state.page
        if selected_page != prev_page:
            st.session_state.page = selected_page
            try:
                st.rerun()
            except Exception:
                # For older Streamlit versions
                st.experimental_rerun()

    if selected == "About":
        with st.expander("What technologies power this application?"):
            st.markdown(''' 
    This application is built using several powerful technologies:
    
    - **Streamlit**: A Python framework for building interactive web apps with ease. It's used to create the user interface for this application.
    - **OpenAI**: We use OpenAI's models for natural language processing and embeddings. OpenAI's GPT-4 handles the conversational AI capabilities.
    - **ChromaDB**: A vector database for efficient storage and retrieval of document embeddings. Chroma helps in managing and querying large sets of documents, making it easy to retrieve relevant information.
    - **PyPDF2**: A Python library to extract text from PDF documents, which are uploaded by the user to create collections.
    - **NumPy**: A core library for numerical computations, used to handle embeddings and similarity calculations efficiently.
    - **MongoDB**: A NoSQL database used to store structured data extracted from PDFs.

    These technologies together provide a seamless way to upload, manage, and query documents, enabling users to chat with their documents and get insightful answers based on the contents.
    ''')
        with st.expander("How does the AI interact with documents?"):
            st.markdown(''' 
    The AI interacts with your documents using a combination of **document embeddings** and **semantic search**:

    - **Document Embedding**: Each document you upload is processed to create an embedding (a numerical representation) of its content. This is done using OpenAI's embeddings model, which converts the textual content into a vector.
    - **ChromaDB**: After embedding the documents, the vectors are stored in **ChromaDB**, a database optimized for storing and querying these embeddings. When you ask a question, the AI searches the embeddings for the most relevant documents or document chunks.
    - **Semantic Search**: Using cosine similarity, the AI compares your query's embedding to the stored document embeddings to find the closest matches. This allows the AI to understand context and return highly relevant answers.
    - **GPT-4**: Once the AI identifies relevant documents, it uses **OpenAI's GPT-4** to generate detailed responses by providing the context from these documents.
    - **MongoDB**: Structured data extracted from PDFs is stored in MongoDB, allowing for efficient querying and retrieval of specific information.

    This combination of techniques allows the AI to provide accurate, context-aware responses, making it easier to extract meaningful insights from your documents.
    ''')
        with st.expander("What are the core features of this application?"):
            st.markdown(''' 
    The application offers a range of features designed to help you interact with and manage your documents:

    - **Manage Collections**: You can create, modify, and delete collections of documents. Collections are groups of PDF files that you upload, which are then indexed for searching and querying.
    - **AI Chatbot Interface**: Once you have a collection, you can chat with your documents using the AI chatbot. The chatbot uses the uploaded documents to answer questions, extract insights, and assist with tasks like summarization, analysis, and more.
    - **Document Upload & Chunking**: The app allows you to upload multiple PDF documents, which are automatically processed, chunked into smaller pieces, and stored for efficient querying.
    - **Semantic Search**: By leveraging **OpenAI embeddings** and **ChromaDB**, the AI can search your documents semantically, not just through keyword matching, giving you context-aware responses.
    - **Real-Time Chatting**: Interact with the AI in real-time as it streams responses, allowing for a more engaging and conversational experience.
    - **MongoDB Integration**: Extract structured data from PDFs and store it in MongoDB for efficient retrieval and querying.

    These features make it simple to manage large volumes of documents and extract meaningful insights with minimal effort. Whether for research, business analysis, or personal use, this tool helps you maximize the value of your documents.
    ''')

    # Initialize session state for page if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "AI Chatbot"

    if st.session_state.page == "AI Chatbot":
        if selected == "Info":
            with st.expander("What is this page?"):
                st.markdown('''
    The **AI Chatbot** page allows you to interact with your uploaded documents and ask questions about their contents. 

    Here's how it works:

    - Once you have uploaded your documents and created a collection in the **"Manage Collections"** page, you can use the AI Chatbot to **ask questions** related to those documents.
    - The chatbot uses **Embedding-based Retrieval-Augmented Generation (RAG)** techniques, where it searches for relevant content from the documents you uploaded and generates accurate answers using GPT-based models (like GPT-4).
    - The AI will try to find **relevant sections or chunks of text** from your documents that answer your query. It then combines these with its own knowledge to create a useful response.

    Whether you're looking for specific information, insights, or performing document-based queries, the AI Chatbot helps you quickly extract answers and knowledge from your documents.
    ''')
            with st.expander("What are the pre-requisites to chat?"):
                st.markdown('''
    In order to use the AI Chatbot, you must first **create a collection** in the **"Manage Collections"** page. Here's how you can do it:

    1. **Go to the "Manage Collections" page** from the Sidebar.
    2. **Click on "Add Collection"**, where you can upload your documents (PDF files).
    3. **Submit** the files, and they will be processed to create a collection.
    4. Once your collection is created, come back to the **"AI Chatbot"** page, select your collection from the dropdown, and you're ready to start chatting with your documents!

    You can interact with the chatbot, ask questions, and retrieve insights based on the content of your uploaded documents.

    **Important Notes:**
    - Ensure that your documents are in PDF format for easy upload.
    - The more diverse and rich your collection is, the better the AI will be at answering your questions.
    ''')
            with st.expander("Try a Demo Run Now"):
                st.markdown('''
    Here's how you can run a Demo of the application:

    1. **Download any one of the collections** from below: Google, Meta, or Netflix.
    2. **Unzip the collection**, revealing the appropriate PDF files.
    3. **Upload the files** in the "Add Collection" section of the **"Manage Collections"** page.
    4. Come back to the **"AI Chatbot"** page, select your collection, and **start chatting** with your documents!

    This demo allows you to quickly see how the AI can interact with your documents and provide insights. Just follow the simple steps and you're ready to start!

    Enjoy exploring the demo and interact with the content!
    ''')
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button('Google'):
                        st.write("[Download file](https://www.dropbox.com/scl/fi/cx2t9w5t4uapv9mkwb1uc/Google.zip?rlkey=mldpxflx01kpbi82b3j4y99zx&st=0ok4jawz&dl=1)")
                with col2:
                    if st.button('Meta'):
                        st.write("[Download file](https://www.dropbox.com/scl/fi/h4145xifvhf39t5ojdx2i/Meta.zip?rlkey=v80pwcxm129b7sunnrzk5cula&st=oemj80a0&dl=1)")
                with col3:
                    if st.button('Netflix'):
                        st.write("[Download file](https://www.dropbox.com/scl/fi/savy5gl5e5kc4ar0rxd9g/Netflix.zip?rlkey=ugotzhrucw6uflgz0leli0g9o&st=nk3p3ze5&dl=1)")
                
        chatbot_interface_ui()

    elif st.session_state.page == "Manage Collections":
        if selected == "Info":
            with st.expander("What is this page?"):
                st.markdown('''
    This page allows you to manage your document collections. 
    You can perform various actions such as:

    - **Add new collections**: Upload documents and create collections of your enterprise data.
    - **Modify collections**: Add new files to existing collections or remove files from them.
    - **Delete collections**: Remove entire collections from the system when they are no longer needed.

    Use this page to organize and manage your documents before interacting with the AI Chatbot for insights.
    ''')
            with st.expander("What is a collection?"):
                st.markdown('''
    A **collection** is a group of documents that you can upload and organize in the system. It acts as a container for your data and enables you to interact with the documents through the AI chatbot.

    In this app, we use **ChromaDB** to store and manage collections. Here's a brief overview of how collections work:

    1. **Embedding documents**: 
       - When you upload a document, we extract its text and break it down into smaller chunks (called *chunks*).
       - Each chunk is then converted into an **embedding** using OpenAI's embeddings model. An embedding is a numerical representation of the content in that chunk, which allows us to compare and retrieve relevant information efficiently.
    
    2. **ChromaDB**:
       - ChromaDB is a vector database that stores these embeddings and allows for **similarity search**. When you ask a question, the AI looks for the most relevant document chunks by comparing the embeddings of the question and the document chunks.
       - This process ensures that the AI provides you with the most contextually relevant information when responding to your queries.

    3. **Retrieving Context**:
       - When you interact with the AI chatbot, it uses these embeddings to find the most similar chunks of information from the collection. This is known as **retrieval-augmented generation** (RAG). The AI then combines the context from these chunks to generate accurate and insightful responses.
    
    By organizing your documents into collections, you make it easier for the AI to fetch relevant information and assist you in extracting insights from your data.
    ''')

        manage_collections_ui()

    elif st.session_state.page == "Store PDF to MongoDB":
        if selected == "Info":
            with st.expander("What is this page?"):
                st.markdown('''
    This page allows you to convert your PDF documents to structured data stored in MongoDB. 
    Here's what you can do:

    - Upload a PDF file
    - Extract important information from the PDF using AI
    - Store the extracted structured data in MongoDB
    - View the stored data

    This feature enables you to convert unstructured PDF data into a structured format stored in a NoSQL database, 
    which can be useful for further analysis or integration with other data systems.
    ''')
        pdf_to_mongodb_page()
    
    elif st.session_state.page == "Audit Data on MongoDB":
        if selected == "Info":
            with st.expander("What is this page?"):
                st.markdown('''
This page allows you to view and edit the audit data stored in MongoDB. Here's what you can do:

1. **View Audit Data**: See a table of all the audit data extracted from your PDF documents and stored in MongoDB.

2. **Select and Edit Documents**: Choose a specific document from the table to view its details and make changes.

3. **AI-Assisted Editing**: Describe the changes you want to make in natural language, and our AI will generate the appropriate edit commands.

4. **Apply Changes**: Review the AI-generated edit commands and apply them directly to update the MongoDB document.

This feature enables you to:
- Easily review the structured data extracted from your PDFs
- Make precise adjustments to the stored information
- Correct any errors or update outdated information
- Maintain the accuracy and relevance of your audit data over time

By combining the power of MongoDB for data storage with AI-assisted editing, we provide a user-friendly interface for managing complex document structures without requiring deep technical knowledge of databases or JSON manipulation.

Remember to review any AI-generated changes carefully before applying them to ensure they match your intended modifications.
        ''')
        edit_mongodb_document()

    elif st.session_state.page == "View MongoDB Documents":
        if selected == "Info":
            with st.expander("What is this page?"):
                st.markdown('''
This page displays the documents stored in MongoDB as tables. 
Each document is presented in a tabular format for easy viewing, 
with an option to see the raw JSON data. 
Use this page to quickly review and verify the structured data 
extracted from your PDF documents.
''')
        db_image_page()
    
    elif st.session_state.page == "Strategic Financial Intelligence Hub":
        if selected == "Info":
            with st.expander("What is this page?"):
                st.markdown('''
    This page provides a comprehensive Strategic Financial Intelligence Hub. Here's what you can do:

    1. **Upload Financial Reports**: You can upload PDF files containing financial reports.
    2. **View Key Metrics**: The dashboard displays four key financial metrics:
       - Total Revenue with year-over-year growth
       - Operating Profit with Operating Margin
       - Net Income with Earnings Per Share (EPS)
       - Key Business Segment Revenue with growth percentage
    3. **Interactive Graphs**: The page generates interactive graphs based on the uploaded data, including:
       - Revenue Trends
       - Profit Margins
       - Segment Performance
       - Earnings Per Share (EPS) Trend
    4. **AI-Powered Analysis**: The dashboard uses OpenAI's API to extract and structure financial data from the uploaded PDFs.

    This dashboard helps you quickly visualize and understand key financial metrics and trends from your company's reports.
    ''')
        business_metrics_dashboard()


if __name__ == "__main__":
    main()