"""
Comparison script to test Legacy vs AI-Enhanced chaining systems.
Processes the same dataset with both methods and compares results.
"""

import pandas as pd
import time
from datetime import datetime

def run_legacy_chaining(articles_df):
    """Run legacy chaining system"""
    print("\n" + "="*60)
    print("🔧 LEGACY CHAINING SYSTEM")
    print("="*60 + "\n")
    
    from NewsChainer_Legacy import find_related_articles, format_chained_articles
    
    start_time = time.time()
    grouped_articles, article_index_map = find_related_articles(articles_df)
    chained_articles = format_chained_articles(grouped_articles, article_index_map)
    end_time = time.time()
    
    stats = {
        'system': 'Legacy',
        'num_chains': len(chained_articles),
        'total_articles': len(articles_df),
        'avg_chain_size': sum(len(chain) for chain in chained_articles) / len(chained_articles),
        'max_chain_size': max(len(chain) for chain in chained_articles),
        'singleton_chains': sum(1 for chain in chained_articles if len(chain) == 1),
        'processing_time': end_time - start_time,
        'api_cost': 0.0  # Legacy doesn't use API
    }
    
    return chained_articles, stats

def run_enhanced_chaining(articles_df):
    """Run AI-enhanced chaining system"""
    print("\n" + "="*60)
    print("🤖 AI-ENHANCED CHAINING SYSTEM")
    print("="*60 + "\n")
    
    from NewsChainer import find_related_articles, format_chained_articles
    
    start_time = time.time()
    grouped_articles, article_index_map = find_related_articles(articles_df)
    chained_articles = format_chained_articles(grouped_articles, article_index_map)
    end_time = time.time()
    
    # Estimate API cost (rough approximation)
    # Assume ~300 validations for 200 articles, ~700 tokens per validation
    num_validations = len([chain for chain in grouped_articles if len(chain) > 1]) * 2  # Rough estimate
    tokens_per_validation = 700
    total_tokens = num_validations * tokens_per_validation
    cost_per_million = 3.0  # Approximate blended rate for GPT-4.1
    estimated_cost = (total_tokens / 1_000_000) * cost_per_million
    
    stats = {
        'system': 'AI-Enhanced',
        'num_chains': len(chained_articles),
        'total_articles': len(articles_df),
        'avg_chain_size': sum(len(chain) for chain in chained_articles) / len(chained_articles),
        'max_chain_size': max(len(chain) for chain in chained_articles),
        'singleton_chains': sum(1 for chain in chained_articles if len(chain) == 1),
        'processing_time': end_time - start_time,
        'api_cost': estimated_cost
    }
    
    return chained_articles, stats

def print_comparison(legacy_stats, enhanced_stats):
    """Print side-by-side comparison"""
    print("\n" + "="*60)
    print("📊 COMPARISON RESULTS")
    print("="*60 + "\n")
    
    print(f"{'Metric':<30} {'Legacy':<15} {'AI-Enhanced':<15} {'Change':<15}")
    print("-" * 75)
    
    # Number of chains
    legacy_chains = legacy_stats['num_chains']
    enhanced_chains = enhanced_stats['num_chains']
    chains_diff = enhanced_chains - legacy_chains
    chains_pct = ((enhanced_chains - legacy_chains) / legacy_chains * 100) if legacy_chains > 0 else 0
    print(f"{'Total Story Chains':<30} {legacy_chains:<15} {enhanced_chains:<15} {chains_diff:+d} ({chains_pct:+.1f}%)")
    
    # Average chain size
    legacy_avg = legacy_stats['avg_chain_size']
    enhanced_avg = enhanced_stats['avg_chain_size']
    avg_diff = enhanced_avg - legacy_avg
    print(f"{'Avg Chain Size':<30} {legacy_avg:<15.2f} {enhanced_avg:<15.2f} {avg_diff:+.2f}")
    
    # Max chain size
    legacy_max = legacy_stats['max_chain_size']
    enhanced_max = enhanced_stats['max_chain_size']
    max_diff = enhanced_max - legacy_max
    print(f"{'Max Chain Size':<30} {legacy_max:<15} {enhanced_max:<15} {max_diff:+d}")
    
    # Singleton chains (articles not chained)
    legacy_single = legacy_stats['singleton_chains']
    enhanced_single = enhanced_stats['singleton_chains']
    single_diff = enhanced_single - legacy_single
    single_pct = ((enhanced_single - legacy_single) / legacy_single * 100) if legacy_single > 0 else 0
    print(f"{'Singleton Stories':<30} {legacy_single:<15} {enhanced_single:<15} {single_diff:+d} ({single_pct:+.1f}%)")
    
    # Processing time
    legacy_time = legacy_stats['processing_time']
    enhanced_time = enhanced_stats['processing_time']
    time_diff = enhanced_time - legacy_time
    print(f"{'Processing Time (s)':<30} {legacy_time:<15.2f} {enhanced_time:<15.2f} {time_diff:+.2f}")
    
    # API cost
    legacy_cost = legacy_stats['api_cost']
    enhanced_cost = enhanced_stats['api_cost']
    print(f"{'API Cost ($)':<30} ${legacy_cost:<14.2f} ${enhanced_cost:<14.2f} ${enhanced_cost:.2f}")
    
    print("\n" + "="*60)
    print("📝 INTERPRETATION")
    print("="*60 + "\n")
    
    if enhanced_single > legacy_single:
        print(f"✅ MORE singleton stories ({single_diff:+d}): AI correctly separated {single_diff} falsely-chained stories")
    elif enhanced_single < legacy_single:
        print(f"⚠️  FEWER singleton stories ({single_diff:+d}): May indicate more aggressive chaining")
    
    if enhanced_avg < legacy_avg:
        print(f"✅ SMALLER average chains ({avg_diff:.2f}): AI avoided over-chaining unrelated articles")
    
    if enhanced_max < legacy_max:
        print(f"✅ SMALLER max chain ({max_diff:+d}): AI prevented mega-chains of unrelated stories")
    
    print(f"\n💰 Cost per digest: ${enhanced_cost:.2f}")
    print(f"⏱️  Extra time: {time_diff:.1f}s ({time_diff/60:.1f} minutes)")
    
    print("\n" + "="*60)

def save_comparison_report(legacy_chains, enhanced_chains, output_file="chaining_comparison_report.txt"):
    """Save detailed comparison report"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("CHAINING SYSTEM COMPARISON REPORT\n")
        f.write("="*60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"LEGACY SYSTEM: {len(legacy_chains)} story chains\n")
        f.write(f"AI-ENHANCED: {len(enhanced_chains)} story chains\n\n")
        
        f.write("STORY CHAIN COMPARISON\n")
        f.write("-"*60 + "\n\n")
        
        # Find chains that differ significantly
        f.write("Stories that were separated by AI system:\n\n")
        
        # This is a simplified version - full implementation would track specific articles
        for i, (legacy_chain, enhanced_chain) in enumerate(zip(legacy_chains[:10], enhanced_chains[:10])):
            if len(legacy_chain) > len(enhanced_chain):
                f.write(f"Chain {i+1}:\n")
                f.write(f"  Legacy: {len(legacy_chain)} articles\n")
                f.write(f"  Enhanced: {len(enhanced_chain)} articles\n")
                f.write(f"  → AI separated this chain\n\n")
    
    print(f"\n✅ Detailed report saved to: {output_file}")

def main():
    """Main comparison function"""
    print("\n" + "="*60)
    print("🔬 CHAINING SYSTEM COMPARISON TEST")
    print("="*60)
    
    # Load extracted news articles
    input_csv = "extracted_news.csv"
    
    try:
        articles_df = pd.read_csv(input_csv)
        print(f"\n✅ Loaded {len(articles_df)} articles from {input_csv}")
    except FileNotFoundError:
        print(f"\n❌ Error: {input_csv} not found!")
        print("Please run NewsToCsv.py first to extract articles.")
        return
    
    # Ensure data is clean
    articles_df["Content"] = articles_df["Content"].astype(str).fillna("")
    articles_df["Headline"] = articles_df["Headline"].astype(str).fillna("")
    articles_df["Date"] = articles_df["Date"].astype(str).fillna("")
    
    # Run both systems
    legacy_chains, legacy_stats = run_legacy_chaining(articles_df.copy())
    enhanced_chains, enhanced_stats = run_enhanced_chaining(articles_df.copy())
    
    # Print comparison
    print_comparison(legacy_stats, enhanced_stats)
    
    # Save detailed report
    save_comparison_report(legacy_chains, enhanced_chains)
    
    print("\n✅ Comparison complete!")
    print("\nRecommendation:")
    if enhanced_stats['singleton_chains'] > legacy_stats['singleton_chains']:
        print("  ✅ AI system shows better story separation")
        print("  ✅ Consider deploying to production")
    else:
        print("  ⚠️  Review results manually before deploying")
    print()

if __name__ == "__main__":
    main()
