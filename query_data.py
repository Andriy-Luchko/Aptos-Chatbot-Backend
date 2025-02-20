import argparse
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found in environment variables")
    sys.exit(1)

#DB That Wipes when you run create_database.py
# CHROMA_PATH = "chroma"

#DB That has all the mdx's already stored
CHROMA_PATH = "AllDocsDB/chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context in a concise manner: {question}
"""

def query_groq(prompt, model_name="mixtral-8x7b-32768"):
    """Separate function to handle Groq API calls"""
    try:
        model = ChatGroq(
            model_name=model_name,
            groq_api_key=GROQ_API_KEY
        )
        return model.invoke(prompt)
    except Exception as e:
        available_models = [
            "mixtral-8x7b-32768",
            "llama2-70b-4096",
            "gemma-7b-it"
        ]
        error_msg = f"\nError accessing Groq API: {str(e)}"
        error_msg += "\n\nAvailable Groq models include:"
        for model in available_models:
            error_msg += f"\n- {model}"
        raise Exception(error_msg)

def query(query_text=""):
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Perform similarity search
    results = db.similarity_search_with_relevance_scores(query_text, k=3, score_threshold=.5)
    
    if not results:
        prompt = query_text
    else:
        # Build context from search results
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

    print("\nGenerated Prompt:", prompt)

    # Query Groq
    response_text = query_groq(prompt, model_name="mixtral-8x7b-32768")

    # Extract sources from metadata
    sources = [doc.metadata.get("source", "Unknown") for doc, _ in results]
    formatted_response = f"\nResponse:\n{response_text.content}\n\nSources: {sources}"
    return formatted_response
    
def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("query_text", type=str, help="The query text.")
        args = parser.parse_args()
        query_text = args.query_text
        print(query(query_text))
    except Exception as e:
        print(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()