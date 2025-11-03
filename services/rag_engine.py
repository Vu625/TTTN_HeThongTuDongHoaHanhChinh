#Chứa các hàm Numpy để Vector Search, Similarity Search (Custom RAG).
import os
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from pathlib import Path

LAW_DIR = Path("data/db/law_texts")

def load_law_texts():
    texts = []
    for file in LAW_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            texts.append((file.name, f.read()))
    return texts

def build_vector_store():
    texts = load_law_texts()
    docs = [t[1] for t in texts]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(docs)
    return texts, vectorizer, vectors

def retrieve_relevant_text(query, vectorizer, vectors, texts, top_k=1):
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, vectors).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]
    results = [(texts[i][0], texts[i][1], similarities[i]) for i in top_indices]
    return results

def generate_answer(query):
    texts, vectorizer, vectors = build_vector_store()
    results = retrieve_relevant_text(query, vectorizer, vectors, texts)
    if not results:
        return "Xin lỗi, tôi không tìm thấy quy định phù hợp."
    filename, content, score = results[0]
    return f"📘 Theo **{filename}**:\n\n{content.strip()}\n\n(Độ liên quan: {score:.2f})"