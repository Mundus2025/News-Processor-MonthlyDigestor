import pandas as pd
import itertools
import re
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    """
    Cleans and normalizes text by removing punctuation, converting to lowercase, and keeping only meaningful words.
    Handles NaN, None, and non-string values gracefully.
    """
    # Handle NaN, None, and non-string values
    if text is None or text == "":
        return ""
    
    # Handle pandas NaN and numpy NaN
    try:
        if pd.isna(text):
            return ""
    except (TypeError, ValueError):
        pass
    
    # Convert to string if it's not already
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ""
    
    # Final check - if empty after conversion
    if not text or text == "nan" or text == "None":
        return ""
    
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text

def extract_keywords(text, num_keywords=5):
    """
    Extracts key terms from the article using TF-IDF vectorization.
    Returns a set of top `num_keywords` important words from the text.
    Handles empty or invalid text gracefully.
    """
    # Handle empty or invalid text
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return set()
    
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_array = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]

        # Get top keyword indices sorted by score
        top_indices = tfidf_scores.argsort()[-num_keywords:]
        keywords = {feature_array[i] for i in top_indices}
        
        return keywords
    except Exception as e:
        print(f"⚠️ Warning: Could not extract keywords from text: {e}")
        return set()

def find_related_articles(articles_df, similarity_threshold=0.2):
    """
    Finds and groups related articles based on keyword overlap and similarity scores.
    Handles missing or invalid data gracefully.
    """
    grouped_articles = []
    used_articles = set()
    
    # Ensure required columns exist and handle missing data
    required_columns = ["Headline", "Content"]
    for col in required_columns:
        if col not in articles_df.columns:
            raise ValueError(f"Required column '{col}' not found in articles data")
        # Fill NaN values with empty strings
        articles_df[col] = articles_df[col].fillna("")
        # Ensure all values are strings
        articles_df[col] = articles_df[col].astype(str)
    
    print(f"🔍 Processing {len(articles_df)} articles for chaining...")
    
    # Preprocess headlines and content
    articles_df["Processed_Headline"] = articles_df["Headline"].apply(preprocess_text)
    articles_df["Processed_Content"] = articles_df["Content"].apply(preprocess_text)
    
    # Extract keywords from each article
    articles_df["Keywords"] = articles_df["Processed_Content"].apply(extract_keywords)
    
    # Create a mapping of articles by index
    article_index_map = {i: row for i, row in articles_df.iterrows()}
    
    # Compute similarity between articles
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(articles_df["Processed_Content"])
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Group related articles
    for i, row in articles_df.iterrows():
        if i in used_articles:
            continue

        group = [i]
        used_articles.add(i)
        
        for j, similarity_score in enumerate(similarity_matrix[i]):
            if j != i and j not in used_articles and similarity_score >= similarity_threshold:
                group.append(j)
                used_articles.add(j)

        grouped_articles.append(group)

    return grouped_articles, article_index_map

def format_chained_articles(grouped_articles, article_index_map):
    """
    Formats grouped articles into structured output.
    """
    chained_results = []

    for group in grouped_articles:
        grouped_news = []
        for index in sorted(group):  # Sort by chronological order
            article = article_index_map[index]
            grouped_news.append({
                "Date": article["Date"],
                "Headline": article["Headline"],
                "Content": article["Content"]
            })
        
        chained_results.append(grouped_news)

    return chained_results

def save_chained_articles(chained_articles, output_filename="chained_news.csv"):
    """
    Saves the chained articles into a structured CSV file.
    """
    flattened_data = []

    for group_id, group in enumerate(chained_articles, start=1):
        for article in group:
            flattened_data.append([group_id, article["Date"], article["Headline"], article["Content"]])

    df = pd.DataFrame(flattened_data, columns=["Story Group ID", "Date", "Headline", "Content"])
    df.to_csv(output_filename, index=False, encoding="utf-8")

    print(f"\n✅ Chained news articles saved to {output_filename}\n")

def main():
    """
    Main function that runs when the script is executed directly.
    This function is not called when the script is imported.
    """
    # Load extracted news articles
    input_csv = "extracted_news.csv"
    articles_df = pd.read_csv(input_csv)
    
    # 🔥 Ensure 'Content' column is always a string and replace NaN with empty string
    articles_df["Content"] = articles_df["Content"].astype(str).fillna("")

    # Identify related articles based on keywords & similarity
    grouped_articles, article_index_map = find_related_articles(articles_df)

    # Format results
    chained_articles = format_chained_articles(grouped_articles, article_index_map)

    # Save results
    save_chained_articles(chained_articles, "chained_news.csv")

if __name__ == "__main__":
    main()
