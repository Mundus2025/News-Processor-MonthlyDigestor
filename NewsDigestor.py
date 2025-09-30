import pandas as pd
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import openai
from dotenv import load_dotenv

# Load OpenAI API key from .env file or environment
load_dotenv()  # Load from .env file if it exists (local development)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API key is missing! Set OPENAI_API_KEY environment variable.")

# OpenAI client setup with error handling
try:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    raise ValueError(f"❌ Failed to initialize OpenAI client: {e}")

# Category definitions
categories = {
    "Security & Defence": ["NATO", "military", "war", "defence", "Swedish Armed Forces", "cyberattack", "intelligence"],
    "Foreign Relations & International Aid": ["UN", "international", "diplomacy", "foreign policy", "aid", "embassy"],
    "Sweden in the EU": ["EU", "European Union", "Brussels", "regulation", "directive"],
    "Domestic News": ["Swedish government", "Riksdag", "policy", "social", "healthcare", "education"],
    "Law & Order": ["crime", "police", "justice", "court", "gangs", "law"],
    "Education & Research": ["university", "research", "education", "students", "school"],
    "Energy": ["nuclear", "wind power", "energy policy", "electricity", "power grid"],
    "Climate & The Green Transition": ["emissions", "climate change", "green technology", "sustainability"],
    "Business News & Economy": ["economy", "inflation", "GDP", "business", "market", "finance"],
    "Sweden's Economic Trends": ["economic trends", "GDP growth", "Riksbank", "inflation", "monetary policy"],
    "Business News: Key Developments": ["business developments", "corporate news", "mergers", "acquisitions", "market trends"],
    "Green Industry": ["renewable energy", "sustainability", "green investments", "carbon neutral", "eco-friendly"],
    "Reporting Season": ["earnings reports", "financial results", "quarterly earnings", "stock performance", "revenue projections"],
    "Copyright & Disclaimer": ["copyright", "disclaimer", "terms and conditions", "legal", "intellectual property"]
}

# List of months to exclude from bolding
EXCLUDED_WORDS = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
}

def preprocess_text(text):
    """Removes punctuation, lowercases text, and normalizes spacing."""
    text = re.sub(r"[^\w\s]", "", text.lower())
    return text

def train_classifier(training_files):
    """Trains a Naïve Bayes classifier using multiple labeled datasets."""
    dataframes = [pd.read_excel(file) for file in training_files]
    df = pd.concat(dataframes, ignore_index=True)
    
    if "Category" not in df.columns:
        raise ValueError("Training data must include a 'Category' column.")
    
    df["Processed"] = df["Summary"].apply(preprocess_text)
    X = df["Processed"]
    y = df["Category"]
    classifier = make_pipeline(CountVectorizer(ngram_range=(1,2)), MultinomialNB())
    classifier.fit(X, y)
    return classifier

def categorize_story_ml(classifier, summary):
    """Uses trained classifier to categorize summaries with confidence filtering."""
    processed_text = preprocess_text(summary)
    probabilities = classifier.predict_proba([processed_text])[0]
    max_prob = max(probabilities)
    predicted_category = classifier.classes_[np.argmax(probabilities)]
    
    if max_prob < 0.6:  # Threshold for confidence filtering
        return "Miscellaneous"
    return predicted_category

def compute_similarity(stories):
    """Computes similarity scores and refines category assignments."""
    vectorizer = TfidfVectorizer(ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform(stories)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

def categorize_with_llm(summary, initial_category):
    """
    Uses GPT-4.1 to refine the category of a news summary.
    Takes in the second-stage categorization's assigned category and evaluates whether it fits the final report categories.
    """
    categories_list = [
        "Security & Defence",
        "Foreign Relations & International Aid",
        "Sweden in the EU",
        "Domestic News",
        "Law & Order",
        "Education & Research",
        "Climate & The Green Transition",
        "Energy",
        "Sweden's Economic Trends",
        "Business News: Key Developments",
        "Green Industry",
        "Reporting Season"
    ]

    try:
        response = client.chat.completions.create(  # ✅ Use global client
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert news categorizer ensuring accurate classification of news stories."},
                {"role": "user", "content": f"Here is a news summary:\n\n{summary}\n\n"
                                             f"The machine learning system initially classified it as: {initial_category}.\n"
                                             f"Choose the most appropriate category from this list: {', '.join(categories_list)}.\n"
                                             f"Reply ONLY with the category name, without explanation."}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        # ✅ Correct way to access the response (as an object)
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ Error in LLM categorization: {e}")
        return initial_category  # Fallback to the ML-assigned category

def refine_category_assignment(df):
    """Adjusts categorization based on similarity scores."""
    similarities = compute_similarity(df["Summary"])
    for idx, row in df.iterrows():
        best_fit_category = row["Category"]
        best_score = 0
        for category in categories.keys():
            category_indices = df[df["Category"] == category].index
            if not category_indices.empty:
                avg_similarity = np.mean(similarities[idx, category_indices])
                if avg_similarity > best_score:
                    best_score = avg_similarity
                    best_fit_category = category
        df.at[idx, "Refined Category"] = best_fit_category
        
         # Apply LLM refinement to finalize category
        final_category = categorize_with_llm(row["Summary"], best_fit_category)
        df.at[idx, "Refined Category"] = final_category
        
    return df

def generate_monthly_digest(input_excel, output_md, training_files):
    df = pd.read_excel(input_excel)
    classifier = train_classifier(training_files)
    df["Category"] = df["Summary"].apply(lambda x: categorize_story_ml(classifier, x))
    df = refine_category_assignment(df)
    
    # Initialize digest sections without category labels in stories
    digest_sections = {category: [] for category in categories.keys()}
    digest_sections["Miscellaneous"] = []
    
    # Add stories without category headlines
    for _, row in df.iterrows():
        formatted_story = f"{row['Summary']}\n"
        digest_sections[row["Refined Category"]].append(formatted_story)
    
    # Define the fixed category order
    category_order = [
        "Security & Defence",
        "Foreign Relations & International Aid",
        "Sweden in the EU",
        "Domestic News",
        "Law & Order",
        "Education & Research",
        "Energy",
        "Climate & The Green Transition",
        "Business News & Economy",
        "Sweden's Economic Trends",
        "Business News: Key Developments",
        "Green Industry",
        "Reporting Season",
        "Copyright & Disclaimer"
    ]
    
    # Write to markdown file with sorted stories within each category
    with open(output_md, "w", encoding="utf-8") as md_file:
        md_file.write("# News\n\n")
        
        # Process categories in fixed order
        for category in category_order:
            if category in digest_sections and digest_sections[category]:
                md_file.write(f"## {category}\n\n")
                
                # Sort stories within category by length in descending order
                sorted_stories = sorted(
                    digest_sections[category],
                    key=len,
                    reverse=True
                )
                
                # Write sorted stories
                for story in sorted_stories:
                    md_file.write(story + "\n")

def main():
    """
    Main function that runs when the script is executed directly.
    This function is not called when the script is imported.
    """
    # 🔧 Update these paths as needed
    input_excel = "summarised_stories.xlsx"
    output_md = "Monthly_News_Digest.md"
    training_files = ["training_data.xlsx"]  # Add your training data files here
    
    generate_monthly_digest(input_excel, output_md, training_files)

if __name__ == "__main__":
    main()


