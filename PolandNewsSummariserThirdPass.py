import pandas as pd
import openai
import os
import re
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

# Token limits and safety margins
MAX_CONTEXT_TOKENS = 1000000  # GPT-4.1 context window (1M tokens)
SAFE_CHUNK_TOKENS = 900000    # Safe chunk size with buffer for prompt overhead
                              # NOTE: Chunking effectively disabled for GPT-4.1's massive context window
                              # Set to lower value (e.g., 80000) to re-enable chunking if needed
TOKEN_ESTIMATE_RATIO = 4      # Rough estimate: 1 token ≈ 4 characters

def extract_numeric_day(date_string):
    """
    Extracts the numeric day from a date string like '13 February'.
    Assumes the format 'Day Month'.
    """
    try:
        return int(date_string.split(" ")[0])  # Extracts only the day as an integer
    except (ValueError, IndexError):
        return 0  # Fallback for unexpected formats

def format_dates(dates):
    """
    Ensures dates are consistently formatted as (1, 2, 3 February) in ascending order.
    """
    date_list = dates.split(", ")
    if not date_list:
        return ""

    # Extract numeric day values and sort them
    sorted_dates = sorted(date_list, key=extract_numeric_day)

    # Extract the month from the last date (e.g., "3 February")
    month = sorted_dates[-1].split(" ")[1] if " " in sorted_dates[-1] else "Unknown"

    # Extract only the numeric dates
    numeric_dates = [d.split(" ")[0] for d in sorted_dates]

    return f"({', '.join(numeric_dates)} {month})"

def estimate_tokens(text):
    """
    Rough estimation of token count: 1 token ≈ 4 characters.
    This is a conservative estimate for English text.
    """
    return len(str(text)) // TOKEN_ESTIMATE_RATIO

def chunk_merged_story(full_story, max_tokens=SAFE_CHUNK_TOKENS):
    """
    Split a merged story into chunks by article boundaries.
    Each chunk stays under max_tokens to avoid context window limits.
    
    Chunks are split at article boundaries (identified by date markers like "(1 February)").
    This preserves article integrity and chronological order.
    """
    # Pattern to match article boundaries: "(DD Month) Headline:"
    # Example: "(3 February) Polish Sejm debates new policy:"
    article_pattern = r'\n\n(?=\(\d{1,2}\s+\w+\))'
    
    # Split by article markers while preserving the markers
    articles = re.split(article_pattern, full_story)
    
    if not articles:
        return [full_story]
    
    chunks = []
    current_chunk = []
    current_token_count = 0
    
    for article in articles:
        article = article.strip()
        if not article:
            continue
            
        article_tokens = estimate_tokens(article)
        
        # If single article exceeds max_tokens, we need to split it further
        if article_tokens > max_tokens:
            # If current chunk has content, save it first
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_token_count = 0
            
            # Split large article by paragraphs
            paragraphs = article.split('\n\n')
            paragraph_chunk = []
            paragraph_tokens = 0
            
            for para in paragraphs:
                para_tokens = estimate_tokens(para)
                if paragraph_tokens + para_tokens > max_tokens and paragraph_chunk:
                    chunks.append('\n\n'.join(paragraph_chunk))
                    paragraph_chunk = [para]
                    paragraph_tokens = para_tokens
                else:
                    paragraph_chunk.append(para)
                    paragraph_tokens += para_tokens
            
            if paragraph_chunk:
                chunks.append('\n\n'.join(paragraph_chunk))
        
        # If adding this article would exceed limit, start new chunk
        elif current_token_count + article_tokens > max_tokens and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [article]
            current_token_count = article_tokens
        else:
            current_chunk.append(article)
            current_token_count += article_tokens
    
    # Add remaining content
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks if chunks else [full_story]

def get_summary_instructions(dates):
    """
    Determines the summary length instructions based on the number of attached dates.
    """
    num_dates = len(dates.split(", "))

    if num_dates == 1:
        return "Summarise the story in **1-2 sentences**."
    elif num_dates == 2:
        return "Summarise the story in **2-4 sentences**."
    else:
        return "Write a full paragraph summarising the story."

def generate_summary_for_chunk(headlines, chunk_content, dates, chunk_index, total_chunks):
    """
    Generate a summary for a single chunk of a story.
    """
    summary_instruction = get_summary_instructions(dates)
    
    # Adjust instruction if this is a multi-chunk story
    if total_chunks > 1:
        summary_instruction = f"This is part {chunk_index + 1} of {total_chunks} of a larger story. {summary_instruction}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a professional news summariser writing in British English and past tense. "
                                              "Your summaries must always be fully complete and must never be cut off. "
                                              "Ensure all spelling follows British English conventions, such as using 's' instead of 'z' in words like 'realised' "
                                              "and spelling 'defence' with a 'c'."},
                {"role": "user", "content": f"{summary_instruction} Ensure the summary is concise and well-structured.\n\n"
                                            f"📝 Headlines: {headlines}\n\n📜 Story Content:\n{chunk_content}\n\n"
                                            f"🛑 The summary **must** be factual, clear, and complete."}
            ],
            max_tokens=3000,
            temperature=0.2,
            stop=["###"]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ Error generating summary for chunk {chunk_index + 1}/{total_chunks}: {e}")
        return f"[Summary unavailable for chunk {chunk_index + 1}]"

def combine_chunk_summaries(headlines, chunk_summaries, dates):
    """
    Combine multiple chunk summaries into a single coherent summary.
    """
    combined_text = "\n\n".join([f"Part {i+1}: {summary}" for i, summary in enumerate(chunk_summaries)])
    
    summary_instruction = get_summary_instructions(dates)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a professional news editor writing in British English and past tense. "
                                              "Combine the following summaries into ONE coherent, flowing summary."},
                {"role": "user", "content": f"{summary_instruction} Combine these partial summaries into a single, coherent narrative:\n\n"
                                            f"{combined_text}\n\n"
                                            f"Create a unified summary that captures the complete story arc without mentioning 'parts'."}
            ],
            max_tokens=3000,
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ Error combining chunk summaries: {e}")
        # Fallback: just concatenate the summaries
        return " ".join(chunk_summaries)

def generate_summary(headlines, full_story, dates):
    """
    Uses OpenAI's ChatGPT API to generate a complete, structured summary.
    Automatically chunks large stories to avoid context window limits.
    """
    # Estimate total tokens (including prompt overhead)
    story_tokens = estimate_tokens(full_story)
    headlines_tokens = estimate_tokens(headlines)
    prompt_overhead = 1000  # Approximate tokens for system prompt and formatting
    
    total_estimated_tokens = story_tokens + headlines_tokens + prompt_overhead
    
    # If under safe limit, process normally
    if total_estimated_tokens < SAFE_CHUNK_TOKENS:
        summary_instruction = get_summary_instructions(dates)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a professional news summariser writing in British English and past tense. "
                                                  "Your summaries must always be fully complete and must never be cut off. "
                                                  "Ensure all spelling follows British English conventions, such as using 's' instead of 'z' in words like 'realised' "
                                                  "and spelling 'defence' with a 'c'."},
                    {"role": "user", "content": f"{summary_instruction} Ensure the summary is concise and well-structured.\n\n"
                                                f"📝 Headlines: {headlines}\n\n📜 Full Story:\n{full_story}\n\n"
                                                f"🛑 The summary **must** be factual, clear, and use the provided token limit."}
                ],
                max_tokens=3000,
                temperature=0.2,
                stop=["###"]
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ Error generating summary: {e}")
            return "Summary unavailable"
    
    # Story is too large - chunk it
    print(f"   📊 Large story detected (~{total_estimated_tokens:,} tokens). Chunking for processing...")
    
    chunks = chunk_merged_story(full_story)
    print(f"   ✂️  Split into {len(chunks)} chunks")
    
    # Generate summary for each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"   🔄 Processing chunk {i+1}/{len(chunks)}...")
        chunk_summary = generate_summary_for_chunk(headlines, chunk, dates, i, len(chunks))
        chunk_summaries.append(chunk_summary)
    
    # If only one chunk (edge case), return it directly
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    
    # Combine chunk summaries into final summary
    print(f"   🔗 Combining {len(chunk_summaries)} chunk summaries...")
    final_summary = combine_chunk_summaries(headlines, chunk_summaries, dates)
    
    return final_summary

def generate_headline(headlines, full_story):
    """
    Uses OpenAI to generate a merged headline summarising the key event.
    Automatically handles large stories by using chunked summaries instead of full content.
    """
    # Estimate tokens
    story_tokens = estimate_tokens(full_story)
    headlines_tokens = estimate_tokens(headlines)
    prompt_overhead = 500
    
    total_estimated_tokens = story_tokens + headlines_tokens + prompt_overhead
    
    # If story is manageable, use it directly
    if total_estimated_tokens < SAFE_CHUNK_TOKENS:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert news summariser writing in British English."},
                    {"role": "user", "content": f"Generate a concise, professional news headline summarising the following merged news story:\n\n"
                                                f"Headlines: {headlines}\n\nFull Story:\n{full_story}"}
                ],
                max_tokens=300,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ Error generating headline: {e}")
            return "Headline unavailable"
    
    # Story is too large - create condensed version for headline generation
    print(f"   📊 Large story detected for headline generation. Creating condensed version...")
    
    chunks = chunk_merged_story(full_story)
    
    # Extract just the key information from each chunk (first paragraph of each article)
    condensed_parts = []
    for chunk in chunks:
        # Get first 500 characters of each chunk as a teaser
        condensed_parts.append(chunk[:500] + "...")
    
    condensed_story = "\n\n".join(condensed_parts)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert news summariser writing in British English."},
                {"role": "user", "content": f"Generate a concise, professional news headline summarising this ongoing story:\n\n"
                                            f"Headlines: {headlines}\n\n"
                                            f"Story Overview (condensed):\n{condensed_story}\n\n"
                                            f"Create ONE headline that captures the overall narrative arc."}
            ],
            max_tokens=300,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ Error generating headline for large story: {e}")
        # Fallback: use first headline from the list
        first_headline = headlines.split(" | ")[0] if " | " in headlines else headlines
        return first_headline[:150]  # Truncate if too long

def summarise_merged_stories(input_csv="merged_stories_poland.csv", output_csv="summarised_stories_poland.csv", output_excel="summarised_stories_poland.xlsx"):
    """
    Reads the merged news stories CSV, generates summaries and headlines using ChatGPT,
    appends dates manually, and saves results in a structured format.
    """
    df = pd.read_csv(input_csv)

    summaries = []
    for _, row in df.iterrows():
        story_group_id = row["Story Group ID"]
        dates = row["Dates"]
        headlines = row["Headlines"]
        full_story = row["Merged Content"]

        print(f"📝 Processing Story Group {story_group_id}...")

        # Generate AI-based headline & summary
        merged_headline = generate_headline(headlines, full_story)
        summary = generate_summary(headlines, full_story, dates)

        # Append the manually formatted date at the end of the summary
        formatted_date = format_dates(dates)
        summary += f" {formatted_date}"

        summaries.append([story_group_id, merged_headline, summary, formatted_date])

    # Convert to DataFrame
    summary_df = pd.DataFrame(summaries, columns=["Story Group ID", "Merged Headline", "Summary", "Dates"])

    # Save to CSV
    summary_df.to_csv(output_csv, index=False, encoding="utf-8")

    # Save to Excel
    summary_df.to_excel(output_excel, index=False)

    print(f"\n✅ Summarised stories saved to {output_csv} and {output_excel}\n")

def main():
    summarise_merged_stories()

if __name__ == "__main__":
    main() 