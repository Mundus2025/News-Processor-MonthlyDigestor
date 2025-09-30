import pandas as pd
import itertools
import re
from collections import defaultdict
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
from dotenv import load_dotenv

# Load OpenAI API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API key is missing! Set OPENAI_API_KEY environment variable.")

try:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    raise ValueError(f"❌ Failed to initialize OpenAI client: {e}")

# Configuration
AI_VALIDATION_ENABLED = True  # Set to False to use legacy chaining
SIMILARITY_THRESHOLD = 0.25   # Initial candidate selection (slightly higher than before)
AI_CONFIDENCE_THRESHOLD = 0.7 # AI must be 70%+ confident stories are related
MAX_DAYS_APART = 7            # Stories more than 7 days apart are unlikely to be same story
BATCH_SIZE = 50               # Process AI validations in batches

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

def extract_date_from_string(date_string):
    """
    Extracts datetime object from date string like '13 February 2025'
    """
    try:
        return datetime.strptime(date_string, "%d %B %Y")
    except:
        return None

def days_between_articles(date1, date2):
    """
    Calculate days between two article dates
    """
    try:
        d1 = extract_date_from_string(date1)
        d2 = extract_date_from_string(date2)
        if d1 and d2:
            return abs((d2 - d1).days)
    except:
        pass
    return 999  # Return large number if can't parse dates

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

def validate_article_pair_with_ai(article1, article2):
    """
    Uses GPT-4.1 to determine if two articles are about the same story.
    Returns a confidence score (0.0 to 1.0) and reasoning.
    """
    try:
        prompt = f"""You are an expert news analyst. Determine if these two articles are about the SAME NEWS STORY or different stories.

Article 1:
Date: {article1['Date']}
Headline: {article1['Headline']}
Content: {article1['Content'][:500]}...

Article 2:
Date: {article2['Date']}
Headline: {article2['Headline']}
Content: {article2['Content'][:500]}...

Are these articles about the SAME ongoing news story, or are they about DIFFERENT stories?

Consider:
- Are they reporting on the same event/development?
- Do they involve the same key people/organizations?
- Are they part of the same narrative arc?
- Similar topics alone don't mean same story (e.g., two different crimes are different stories)

Respond in this exact format:
SAME_STORY: [yes/no]
CONFIDENCE: [0.0-1.0]
REASON: [one sentence explanation]"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert news analyst who determines if articles are about the same story."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1  # Low temperature for consistent decisions
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse response
        same_story = "yes" in result.split("SAME_STORY:")[1].split("\n")[0].lower()
        confidence_str = result.split("CONFIDENCE:")[1].split("\n")[0].strip()
        confidence = float(re.search(r'0\.\d+|1\.0', confidence_str).group())
        reason = result.split("REASON:")[1].strip() if "REASON:" in result else "No reason provided"
        
        return {
            'same_story': same_story,
            'confidence': confidence,
            'reason': reason
        }
        
    except Exception as e:
        print(f"⚠️ Error in AI validation: {e}")
        # Fallback to neutral response
        return {
            'same_story': False,
            'confidence': 0.5,
            'reason': f"AI validation error: {str(e)}"
        }

def find_candidate_pairs(articles_df, similarity_threshold=SIMILARITY_THRESHOLD):
    """
    Stage 1: Find candidate article pairs using traditional methods.
    Fast initial filtering before AI validation.
    """
    print(f"🔍 Stage 1: Finding candidate pairs from {len(articles_df)} articles...")
    
    candidates = []
    
    # Ensure required columns exist and handle missing data
    required_columns = ["Headline", "Content", "Date"]
    for col in required_columns:
        if col not in articles_df.columns:
            raise ValueError(f"Required column '{col}' not found in articles data")
        articles_df[col] = articles_df[col].fillna("")
        articles_df[col] = articles_df[col].astype(str)
    
    # Preprocess text
    articles_df["Processed_Headline"] = articles_df["Headline"].apply(preprocess_text)
    articles_df["Processed_Content"] = articles_df["Content"].apply(preprocess_text)
    articles_df["Keywords"] = articles_df["Processed_Content"].apply(extract_keywords)
    
    # Compute similarity
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(articles_df["Processed_Content"])
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Find candidate pairs
    for i in range(len(articles_df)):
        for j in range(i + 1, len(articles_df)):
            similarity_score = similarity_matrix[i][j]
            
            # Quick filters for candidates
            if similarity_score >= similarity_threshold:
                article_i = articles_df.iloc[i]
                article_j = articles_df.iloc[j]
                
                # Date proximity check
                days_apart = days_between_articles(article_i['Date'], article_j['Date'])
                
                # Keyword overlap check
                keywords_i = article_i['Keywords']
                keywords_j = article_j['Keywords']
                keyword_overlap = len(keywords_i & keywords_j) if keywords_i and keywords_j else 0
                
                # Calculate composite score for ranking candidates
                composite_score = similarity_score * (1.0 - (days_apart / 30.0)) * (1.0 + keyword_overlap * 0.1)
                
                candidates.append({
                    'index_i': i,
                    'index_j': j,
                    'similarity': similarity_score,
                    'days_apart': days_apart,
                    'keyword_overlap': keyword_overlap,
                    'composite_score': composite_score
                })
    
    # Sort candidates by composite score (best candidates first)
    candidates.sort(key=lambda x: x['composite_score'], reverse=True)
    
    print(f"   ✅ Found {len(candidates)} candidate pairs")
    print(f"   📊 Will validate top pairs with AI...")
    
    return candidates, articles_df

def validate_candidates_with_ai(candidates, articles_df, max_validations=None):
    """
    Stage 2: Use AI to validate if candidate pairs are truly the same story.
    Returns list of validated pairs with confidence scores.
    """
    if not AI_VALIDATION_ENABLED:
        print("   ⚠️ AI validation disabled, using all candidates")
        return [(c['index_i'], c['index_j']) for c in candidates]
    
    validated_pairs = []
    
    # Limit validations if specified
    candidates_to_validate = candidates[:max_validations] if max_validations else candidates
    
    print(f"🤖 Stage 2: AI validating {len(candidates_to_validate)} candidate pairs...")
    
    for idx, candidate in enumerate(candidates_to_validate):
        if (idx + 1) % 10 == 0:
            print(f"   🔄 Validated {idx + 1}/{len(candidates_to_validate)} pairs...")
        
        i = candidate['index_i']
        j = candidate['index_j']
        
        article_i = articles_df.iloc[i].to_dict()
        article_j = articles_df.iloc[j].to_dict()
        
        # AI validation
        validation = validate_article_pair_with_ai(article_i, article_j)
        
        # Accept if AI is confident they're the same story
        if validation['same_story'] and validation['confidence'] >= AI_CONFIDENCE_THRESHOLD:
            validated_pairs.append((i, j))
            print(f"   ✅ Pair {i}-{j}: SAME STORY (confidence: {validation['confidence']:.2f}) - {validation['reason'][:50]}...")
        else:
            print(f"   ❌ Pair {i}-{j}: DIFFERENT (confidence: {validation['confidence']:.2f}) - {validation['reason'][:50]}...")
    
    print(f"   ✅ AI validated {len(validated_pairs)} pairs as same story")
    
    return validated_pairs

def build_story_chains(validated_pairs, articles_df):
    """
    Stage 3: Build story chains from validated pairs using union-find.
    """
    print(f"🔗 Stage 3: Building story chains from validated pairs...")
    
    # Union-find data structure
    parent = {i: i for i in range(len(articles_df))}
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            parent[root_y] = root_x
    
    # Union all validated pairs
    for i, j in validated_pairs:
        union(i, j)
    
    # Group articles by their root
    groups = defaultdict(list)
    for i in range(len(articles_df)):
        root = find(i)
        groups[root].append(i)
    
    # Convert to list of lists
    story_chains = list(groups.values())
    
    print(f"   ✅ Created {len(story_chains)} story chains")
    print(f"   📊 Average chain size: {sum(len(chain) for chain in story_chains) / len(story_chains):.1f} articles")
    
    return story_chains

def find_related_articles(articles_df, use_ai_validation=AI_VALIDATION_ENABLED):
    """
    Main function: Three-stage intelligent article chaining.
    
    Stage 1: Find candidates using TF-IDF similarity
    Stage 2: Validate candidates with AI 
    Stage 3: Build story chains from validated pairs
    """
    print(f"\n{'='*60}")
    print(f"🚀 AI-ENHANCED ARTICLE CHAINING")
    print(f"{'='*60}\n")
    
    # Stage 1: Find candidates
    candidates, articles_df = find_candidate_pairs(articles_df)
    
    # Stage 2: AI validation
    if use_ai_validation and candidates:
        validated_pairs = validate_candidates_with_ai(candidates, articles_df)
    else:
        # Fallback to accepting top candidates without AI
        validated_pairs = [(c['index_i'], c['index_j']) for c in candidates[:100]]
    
    # Stage 3: Build chains
    if validated_pairs:
        story_chains = build_story_chains(validated_pairs, articles_df)
    else:
        # No validated pairs, treat each article as its own story
        story_chains = [[i] for i in range(len(articles_df))]
        print("   ⚠️ No validated pairs, each article is its own story")
    
    # Create article index map
    article_index_map = {i: row for i, row in articles_df.iterrows()}
    
    print(f"\n{'='*60}")
    print(f"✅ CHAINING COMPLETE")
    print(f"   📊 {len(story_chains)} story chains created")
    print(f"   📄 {len(articles_df)} total articles processed")
    print(f"{'='*60}\n")
    
    return story_chains, article_index_map

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
    
    # Ensure 'Content' column is always a string and replace NaN with empty string
    articles_df["Content"] = articles_df["Content"].astype(str).fillna("")

    # Identify related articles using AI-enhanced chaining
    grouped_articles, article_index_map = find_related_articles(articles_df)

    # Format results
    chained_articles = format_chained_articles(grouped_articles, article_index_map)

    # Save results
    save_chained_articles(chained_articles, "chained_news.csv")

if __name__ == "__main__":
    main()
