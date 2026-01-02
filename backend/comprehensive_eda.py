"""
Comprehensive Exploratory Data Analysis (EDA) for IntelliRate ML Training Datasets
Generates individual visualizations and detailed statistical analysis
All graphs are saved as separate PNG files

Usage: python comprehensive_eda.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Create output directory
output_dir = Path("eda_results")
output_dir.mkdir(exist_ok=True)


def save_plot(filename, dpi=300):
    """Helper function to save plots"""
    output_path = output_dir / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    print(f"  ✓ Saved: {filename}")
    plt.close()


def print_section_header(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_subsection(title):
    """Print formatted subsection"""
    print(f"\n{'─'*80}")
    print(f"  {title}")
    print(f"{'─'*80}")


# ============================================================================
# ABUSE DETECTION DATASET EDA
# ============================================================================

def analyze_abuse_detection(df):
    """Comprehensive EDA for abuse detection dataset"""
    print_section_header("📊 ABUSE DETECTION DATASET - EXPLORATORY DATA ANALYSIS")
    
    # ========== BASIC INFO ==========
    print_subsection("1. Dataset Overview")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"\nColumns: {list(df.columns)}")
    print(f"Data Types:\n{df.dtypes}")
    
    # ========== CLASS DISTRIBUTION ==========
    print_subsection("2. Class Distribution")
    class_counts = df['label'].value_counts()
    for label, count in class_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {label.capitalize()}: {count:,} ({pct:.2f}%)")
    
    # Plot class distribution
    plt.figure(figsize=(10, 6))
    colors = ['#2ecc71', '#e74c3c']
    plt.bar(class_counts.index, class_counts.values, color=colors, alpha=0.7, edgecolor='black')
    plt.title('Class Distribution - Abuse Detection Dataset', fontweight='bold', fontsize=16)
    plt.xlabel('Class', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    for i, (label, count) in enumerate(class_counts.items()):
        plt.text(i, count + 100, f'{count:,}\n({count/len(df)*100:.1f}%)', 
                ha='center', fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    save_plot('01_abuse_class_distribution.png')
    
    # ========== STATISTICAL SUMMARY ==========
    print_subsection("3. Statistical Summary (Numeric Features)")
    numeric_df = df.drop('label', axis=1)
    print(numeric_df.describe().round(4))
    
    # Save statistical summary by class
    print_subsection("4. Summary Statistics by Class")
    for label in ['normal', 'abusive']:
        print(f"\n{label.upper()}:")
        print(df[df['label'] == label].drop('label', axis=1).describe().round(4))
    
    # ========== MISSING VALUES ==========
    print_subsection("5. Missing Values Check")
    missing = df.isnull().sum()
    print(f"Total missing values: {missing.sum()}")
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("✓ No missing values found!")
    
    # ========== FEATURE DISTRIBUTIONS ==========
    print_subsection("6. Individual Feature Distributions")
    features = [col for col in df.columns if col != 'label']
    
    for feature in features:
        plt.figure(figsize=(12, 6))
        
        # Plot histograms for both classes
        normal_data = df[df['label'] == 'normal'][feature]
        abusive_data = df[df['label'] == 'abusive'][feature]
        
        plt.hist(normal_data, bins=40, alpha=0.6, label='Normal', 
                color='#2ecc71', edgecolor='black', density=True)
        plt.hist(abusive_data, bins=40, alpha=0.6, label='Abusive', 
                color='#e74c3c', edgecolor='black', density=True)
        
        plt.title(f'Distribution: {feature.replace("_", " ").title()}', 
                 fontweight='bold', fontsize=16)
        plt.xlabel(feature.replace('_', ' ').title(), fontsize=12)
        plt.ylabel('Density', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(alpha=0.3)
        
        # Add statistics
        stats_text = f'Normal: μ={normal_data.mean():.2f}, σ={normal_data.std():.2f}\n'
        stats_text += f'Abusive: μ={abusive_data.mean():.2f}, σ={abusive_data.std():.2f}'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=10)
        
        save_plot(f'02_abuse_dist_{feature}.png')
    
    # ========== BOX PLOTS ==========
    print_subsection("7. Box Plots by Class")
    for feature in features:
        plt.figure(figsize=(10, 6))
        
        data_to_plot = [df[df['label'] == 'normal'][feature],
                       df[df['label'] == 'abusive'][feature]]
        
        bp = plt.boxplot(data_to_plot, labels=['Normal', 'Abusive'], patch_artist=True,
                        showmeans=True, meanline=True)
        
        # Color the boxes
        colors = ['#2ecc71', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        plt.title(f'Box Plot: {feature.replace("_", " ").title()} by Class', 
                 fontweight='bold', fontsize=16)
        plt.ylabel(feature.replace('_', ' ').title(), fontsize=12)
        plt.xlabel('Class', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        save_plot(f'03_abuse_boxplot_{feature}.png')
    
    # ========== CORRELATION ANALYSIS ==========
    print_subsection("8. Correlation Matrix")
    corr_matrix = numeric_df.corr()
    print(corr_matrix.round(4))
    
    # Correlation heatmap
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.3f', 
               cmap='coolwarm', center=0, square=True,
               linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Feature Correlation Heatmap - Abuse Detection', 
             fontweight='bold', fontsize=16)
    save_plot('04_abuse_correlation_heatmap.png')
    
    # ========== PAIRWISE RELATIONSHIPS ==========
    print_subsection("9. Generating Pairwise Scatter Plots")
    # Select key features for pairplot
    key_features = ['requests_per_minute', 'error_rate_percentage', 
                   'ip_reputation_score', 'label']
    
    if all(f in df.columns for f in key_features):
        pairplot = sns.pairplot(df[key_features], hue='label', 
                               palette={'normal': '#2ecc71', 'abusive': '#e74c3c'},
                               diag_kind='kde', plot_kws={'alpha': 0.6})
        pairplot.fig.suptitle('Pairwise Feature Relationships', y=1.02, fontweight='bold', fontsize=16)
        save_plot('05_abuse_pairplot.png', dpi=200)
    
    # ========== STATISTICAL TESTS ==========
    print_subsection("10. Statistical Tests (Normal vs Abusive)")
    print("\nT-Test Results (testing for significant differences):")
    print(f"{'Feature':<30} {'t-statistic':<15} {'p-value':<15} {'Significant?'}")
    print("-" * 65)
    
    for feature in features:
        normal_vals = df[df['label'] == 'normal'][feature]
        abusive_vals = df[df['label'] == 'abusive'][feature]
        t_stat, p_val = stats.ttest_ind(normal_vals, abusive_vals)
        significant = "YES ***" if p_val < 0.001 else "YES **" if p_val < 0.01 else "YES *" if p_val < 0.05 else "NO"
        print(f"{feature:<30} {t_stat:<15.4f} {p_val:<15.6f} {significant}")
    
    print("\n✓ Abuse Detection EDA Complete!")


# ============================================================================
# RATE LIMIT OPTIMIZATION DATASET EDA
# ============================================================================

def analyze_rate_limit(df):
    """Comprehensive EDA for rate limit optimization dataset"""
    print_section_header("📊 RATE LIMIT OPTIMIZATION DATASET - EXPLORATORY DATA ANALYSIS")
    
    # ========== BASIC INFO ==========
    print_subsection("1. Dataset Overview")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"\nColumns: {list(df.columns)}")
    print(f"Data Types:\n{df.dtypes}")
    
    # ========== TIER DISTRIBUTION ==========
    print_subsection("2. Tier Distribution")
    tier_counts = df['tier_name'].value_counts()
    for tier, count in tier_counts.items():
        pct = (count / len(df)) * 100
        avg_limit = df[df['tier_name'] == tier]['optimal_limit'].mean()
        print(f"  {tier.capitalize()}: {count:,} ({pct:.2f}%) - Avg Optimal: {avg_limit:.1f} req/min")
    
    # Tier distribution bar chart
    plt.figure(figsize=(10, 6))
    colors = ['#3498db', '#9b59b6', '#e67e22']
    plt.bar(tier_counts.index, tier_counts.values, color=colors, alpha=0.7, edgecolor='black')
    plt.title('Tier Distribution - Rate Limit Dataset', fontweight='bold', fontsize=16)
    plt.xlabel('Tier', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    for i, (tier, count) in enumerate(tier_counts.items()):
        plt.text(i, count + 50, f'{count:,}\n({count/len(df)*100:.1f}%)', 
                ha='center', fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    save_plot('06_rate_tier_distribution.png')
    
    # Tier pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%',
           colors=colors, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title('Tier Distribution (Percentage)', fontweight='bold', fontsize=16)
    save_plot('07_rate_tier_pie.png')
    
    # ========== STATISTICAL SUMMARY ==========
    print_subsection("3. Statistical Summary")
    numeric_df = df.select_dtypes(include=[np.number])
    print(numeric_df.describe().round(4))
    
    print_subsection("4. Summary by Tier")
    for tier in df['tier_name'].unique():
        print(f"\n{tier.upper()}:")
        tier_data = df[df['tier_name'] == tier].select_dtypes(include=[np.number])
        print(tier_data.describe().round(4))
    
    # ========== MISSING VALUES ==========
    print_subsection("5. Missing Values Check")
    missing = df.isnull().sum()
    print(f"Total missing values: {missing.sum()}")
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("✓ No missing values found!")
    
    # ========== OPTIMAL LIMIT BY TIER ==========
    print_subsection("6. Optimal Limit Distribution by Tier")
    
    plt.figure(figsize=(12, 6))
    tier_order = ['free', 'premium', 'enterprise']
    data_to_plot = [df[df['tier_name'] == tier]['optimal_limit'] for tier in tier_order]
    
    bp = plt.boxplot(data_to_plot, labels=[t.capitalize() for t in tier_order], 
                    patch_artist=True, showmeans=True, meanline=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    plt.title('Optimal Limit Distribution by Tier', fontweight='bold', fontsize=16)
    plt.xlabel('Tier', fontsize=12)
    plt.ylabel('Optimal Limit (requests/min)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    save_plot('08_rate_optimal_limit_boxplot.png')
    
    # ========== SCATTER PLOTS ==========
    print_subsection("7. Feature Relationships")
    
    # Historical requests vs optimal limit
    plt.figure(figsize=(12, 7))
    for tier, color in zip(['free', 'premium', 'enterprise'], colors):
        tier_data = df[df['tier_name'] == tier]
        plt.scatter(tier_data['historical_avg_requests'], 
                   tier_data['optimal_limit'],
                   alpha=0.6, s=50, color=color, label=tier.capitalize(), edgecolors='black')
    
    plt.title('Historical Requests vs Optimal Limit', fontweight='bold', fontsize=16)
    plt.xlabel('Historical Average Requests (req/min)', fontsize=12)
    plt.ylabel('Optimal Limit (req/min)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('09_rate_historical_vs_optimal.png')
    
    # Behavioral consistency vs optimal limit
    plt.figure(figsize=(12, 7))
    for tier, color in zip(['free', 'premium', 'enterprise'], colors):
        tier_data = df[df['tier_name'] == tier]
        plt.scatter(tier_data['behavioral_consistency'], 
                   tier_data['optimal_limit'],
                   alpha=0.6, s=50, color=color, label=tier.capitalize(), edgecolors='black')
    
    plt.title('Behavioral Consistency vs Optimal Limit', fontweight='bold', fontsize=16)
    plt.xlabel('Behavioral Consistency (0-1)', fontsize=12)
    plt.ylabel('Optimal Limit (req/min)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('10_rate_consistency_vs_optimal.png')
    
    # ========== DISTRIBUTIONS BY TIER ==========
    print_subsection("8. Behavioral Consistency Distribution")
    
    plt.figure(figsize=(12, 6))
    for tier, color in zip(['free', 'premium', 'enterprise'], colors):
        tier_data = df[df['tier_name'] == tier]['behavioral_consistency']
        plt.hist(tier_data, bins=30, alpha=0.5, label=tier.capitalize(), 
                color=color, edgecolor='black', density=True)
    
    plt.title('Behavioral Consistency Distribution by Tier', fontweight='bold', fontsize=16)
    plt.xlabel('Behavioral Consistency (0-1)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('11_rate_consistency_distribution.png')
    
    # ========== CORRELATION ANALYSIS ==========
    print_subsection("9. Correlation Matrix")
    corr_matrix = numeric_df.corr()
    print(corr_matrix.round(4))
    
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.3f',
               cmap='coolwarm', center=0, square=True,
               linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Feature Correlation Heatmap - Rate Limit Optimization', 
             fontweight='bold', fontsize=16)
    save_plot('12_rate_correlation_heatmap.png')
    
    # ========== BASE LIMIT VS OPTIMAL LIMIT ==========
    plt.figure(figsize=(12, 7))
    for tier, color in zip(['free', 'premium', 'enterprise'], colors):
        tier_data = df[df['tier_name'] == tier]
        plt.scatter(tier_data['base_limit'], tier_data['optimal_limit'],
                   alpha=0.6, s=50, color=color, label=tier.capitalize(), edgecolors='black')
    
    # Add diagonal line (base = optimal)
    min_val = df[['base_limit', 'optimal_limit']].min().min()
    max_val = df[['base_limit', 'optimal_limit']].max().max()
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Base = Optimal')
    
    plt.title('Base Limit vs Optimal Limit', fontweight='bold', fontsize=16)
    plt.xlabel('Base Limit (req/min)', fontsize=12)
    plt.ylabel('Optimal Limit (req/min)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('13_rate_base_vs_optimal.png')
    
    print("\n✓ Rate Limit Optimization EDA Complete!")


# ============================================================================
# TRAFFIC FORECASTING DATASET EDA
# ============================================================================

def analyze_traffic_forecast(df):
    """Comprehensive EDA for traffic forecasting dataset"""
    print_section_header("📊 TRAFFIC FORECASTING DATASET - EXPLORATORY DATA ANALYSIS")
    
    # ========== BASIC INFO ==========
    print_subsection("1. Dataset Overview")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Date Range: {df['ds'].min()} to {df['ds'].max()}")
    print(f"Frequency: 5-minute intervals")
    print(f"Total Days: {(df['ds'].max() - df['ds'].min()).days}")
    print(f"\nColumns: {list(df.columns)}")
    
    # ========== STATISTICAL SUMMARY ==========
    print_subsection("2. Traffic Statistics")
    print(f"Mean Requests: {df['y'].mean():.2f}")
    print(f"Median Requests: {df['y'].median():.2f}")
    print(f"Std Dev: {df['y'].std():.2f}")
    print(f"Min: {df['y'].min()}")
    print(f"Max: {df['y'].max()}")
    print(f"Range: {df['y'].max() - df['y'].min()}")
    print(f"Coefficient of Variation: {(df['y'].std() / df['y'].mean()):.4f}")
    
    print("\nQuantiles:")
    for q in [0.25, 0.50, 0.75, 0.90, 0.95, 0.99]:
        print(f"  {q*100:.0f}th percentile: {df['y'].quantile(q):.2f}")
    
    # ========== MISSING VALUES ==========
    print_subsection("3. Missing Values Check")
    missing = df.isnull().sum()
    print(f"Total missing values: {missing.sum()}")
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("✓ No missing values found!")
    
    # ========== FULL TIME SERIES ==========
    print_subsection("4. Complete Time Series")
    
    plt.figure(figsize=(16, 6))
    plt.plot(df['ds'], df['y'], linewidth=0.7, alpha=0.8, color='#3498db')
    plt.title('Complete Traffic Time Series (30 Days)', fontweight='bold', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Request Count', fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('14_traffic_timeseries_full.png')
    
    # ========== SINGLE DAY PATTERN ==========
    print_subsection("5. Single Day Pattern")
    
    first_day = df['ds'].dt.date.iloc[0]
    single_day = df[df['ds'].dt.date == first_day].copy()
    single_day['time_of_day'] = single_day['hour'] + single_day['ds'].dt.minute / 60
    
    plt.figure(figsize=(14, 6))
    plt.plot(single_day['time_of_day'], single_day['y'], marker='o', 
            markersize=4, linewidth=1.5, color='#e74c3c')
    plt.title(f'Single Day Traffic Pattern ({first_day})', fontweight='bold', fontsize=16)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Request Count', fontsize=12)
    plt.xticks(range(0, 25, 2))
    plt.grid(alpha=0.3)
    save_plot('15_traffic_single_day.png')
    
    # ========== HOURLY PATTERN ==========
    print_subsection("6. Average Hourly Pattern")
    
    hourly_avg = df.groupby('hour')['y'].agg(['mean', 'std', 'min', 'max'])
    print("\nHourly Statistics:")
    print(hourly_avg.round(2))
    
    plt.figure(figsize=(14, 7))
    plt.bar(hourly_avg.index, hourly_avg['mean'], alpha=0.7, 
           color='#2ecc71', edgecolor='black', label='Mean')
    plt.errorbar(hourly_avg.index, hourly_avg['mean'], yerr=hourly_avg['std'],
                fmt='none', ecolor='red', capsize=4, alpha=0.6, label='± Std Dev')
    
    plt.title('Average Hourly Traffic Pattern', fontweight='bold', fontsize=16)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Average Request Count', fontsize=12)
    plt.xticks(range(0, 24))
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    save_plot('16_traffic_hourly_average.png')
    
    # ========== DAY OF WEEK PATTERN ==========
    print_subsection("7. Day of Week Pattern")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = df.groupby('day_of_week')['y'].agg(['mean', 'std']).reindex(day_order)
    print("\nDaily Statistics:")
    print(daily_stats.round(2))
    
    plt.figure(figsize=(12, 7))
    colors_day = ['#3498db']*5 + ['#e74c3c']*2
    plt.bar(range(7), daily_stats['mean'], color=colors_day, alpha=0.7, edgecolor='black')
    plt.errorbar(range(7), daily_stats['mean'], yerr=daily_stats['std'],
                fmt='none', ecolor='black', capsize=4, alpha=0.6)
    
    plt.title('Average Traffic by Day of Week', fontweight='bold', fontsize=16)
    plt.xlabel('Day', fontsize=12)
    plt.ylabel('Average Request Count', fontsize=12)
    plt.xticks(range(7), [d[:3] for d in day_order])
    plt.grid(axis='y', alpha=0.3)
    
    # Add text annotations
    for i, (day, val) in enumerate(zip(day_order, daily_stats['mean'])):
        plt.text(i, val + 5, f'{val:.1f}', ha='center', fontweight='bold', fontsize=10)
    
    save_plot('17_traffic_day_of_week.png')
    
    # ========== WEEKEND VS WEEKDAY ==========
    print_subsection("8. Weekend vs Weekday Analysis")
    
    weekday_data = df[df['is_weekend'] == 0]['y']
    weekend_data = df[df['is_weekend'] == 1]['y']
    
    print(f"Weekday Average: {weekday_data.mean():.2f}")
    print(f"Weekend Average: {weekend_data.mean():.2f}")
    print(f"Difference: {weekday_data.mean() - weekend_data.mean():.2f} ({((weekday_data.mean() - weekend_data.mean())/weekend_data.mean()*100):.1f}%)")
    
    # T-test
    t_stat, p_val = stats.ttest_ind(weekday_data, weekend_data)
    print(f"\nT-test: t={t_stat:.4f}, p={p_val:.6f}")
    print(f"Statistically significant: {'YES' if p_val < 0.05 else 'NO'}")
    
    plt.figure(figsize=(10, 7))
    bp = plt.boxplot([weekday_data, weekend_data], labels=['Weekday', 'Weekend'],
                     patch_artist=True, showmeans=True, meanline=True)
    
    bp['boxes'][0].set_facecolor('#3498db')
    bp['boxes'][1].set_facecolor('#e74c3c')
    for box in bp['boxes']:
        box.set_alpha(0.6)
    
    plt.title('Weekday vs Weekend Traffic Comparison', fontweight='bold', fontsize=16)
    plt.ylabel('Request Count', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    save_plot('18_traffic_weekday_vs_weekend.png')
    
    # ========== DISTRIBUTION ==========
    print_subsection("9. Traffic Distribution")
    
    plt.figure(figsize=(12, 7))
    plt.hist(df['y'], bins=50, color='#9b59b6', alpha=0.7, edgecolor='black')
    plt.axvline(df['y'].mean(), color='red', linestyle='--', linewidth=2, 
               label=f"Mean: {df['y'].mean():.1f}")
    plt.axvline(df['y'].median(), color='green', linestyle='--', linewidth=2,
               label=f"Median: {df['y'].median():.1f}")
    
    plt.title('Request Count Distribution', fontweight='bold', fontsize=16)
    plt.xlabel('Request Count', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('19_traffic_distribution.png')
    
    # ========== AUTOCORRELATION ==========
    print_subsection("10. Autocorrelation Analysis")
    
    from pandas.plotting import autocorrelation_plot
    
    plt.figure(figsize=(14, 6))
    autocorrelation_plot(df['y'])
    plt.title('Traffic Autocorrelation Plot', fontweight='bold', fontsize=16)
    plt.xlabel('Lag (5-minute intervals)', fontsize=12)
    plt.ylabel('Autocorrelation', fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('20_traffic_autocorrelation.png')
    
    # ========== HEATMAP: HOUR VS DAY ==========
    print_subsection("11. Traffic Heatmap (Hour vs Day of Week)")
    
    pivot_data = df.pivot_table(values='y', index='hour', 
                                columns='day_of_week', aggfunc='mean')
    pivot_data = pivot_data[day_order]
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd', 
               cbar_kws={'label': 'Average Request Count'})
    plt.title('Traffic Heatmap: Hour of Day vs Day of Week', fontweight='bold', fontsize=16)
    plt.xlabel('Day of Week', fontsize=12)
    plt.ylabel('Hour of Day', fontsize=12)
    save_plot('21_traffic_heatmap.png')
    
    # ========== ROLLING STATISTICS ==========
    print_subsection("12. Rolling Statistics (24-hour window)")
    
    # Calculate rolling mean and std (288 intervals = 24 hours)
    df['rolling_mean'] = df['y'].rolling(window=288, center=True).mean()
    df['rolling_std'] = df['y'].rolling(window=288, center=True).std()
    
    plt.figure(figsize=(16, 7))
    plt.plot(df['ds'], df['y'], alpha=0.3, linewidth=0.5, label='Original', color='gray')
    plt.plot(df['ds'], df['rolling_mean'], linewidth=2, label='24h Rolling Mean', color='#e74c3c')
    plt.fill_between(df['ds'], 
                     df['rolling_mean'] - df['rolling_std'],
                     df['rolling_mean'] + df['rolling_std'],
                     alpha=0.3, color='#e74c3c', label='± 1 Std Dev')
    
    plt.title('Traffic with 24-Hour Rolling Statistics', fontweight='bold', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Request Count', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)
    save_plot('22_traffic_rolling_stats.png')
    
    print("\n✓ Traffic Forecasting EDA Complete!")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main EDA execution pipeline"""
    print("\n" + "="*80)
    print("  IntelliRate ML Training Datasets - Comprehensive EDA")
    print("  All graphs generated individually as PNG files")
    print("="*80)
    
    data_dir = Path("training_data")
    
    # Check if data files exist
    required_files = {
        "abuse": "abuse_detection_training_data.csv",
        "rate": "rate_limit_optimization_training_data.csv",
        "traffic": "traffic_forecasting_training_data.csv"
    }
    
    for name, file in required_files.items():
        if not (data_dir / file).exists():
            print(f"\n❌ Error: {file} not found!")
            print("   Please run 'python generate_training_datasets.py' first.")
            return
    
    print("\n✓ All data files found. Starting comprehensive EDA...\n")
    
    # Load datasets
    print("📂 Loading datasets...")
    abuse_df = pd.read_csv(data_dir / required_files['abuse'])
    rate_df = pd.read_csv(data_dir / required_files['rate'])
    traffic_df = pd.read_csv(data_dir / required_files['traffic'])
    traffic_df['ds'] = pd.to_datetime(traffic_df['ds'])
    print("✓ All datasets loaded successfully!\n")
    
    # Run EDA for each dataset
    analyze_abuse_detection(abuse_df)
    analyze_rate_limit(rate_df)
    analyze_traffic_forecast(traffic_df)
    
    # Final summary
    print_section_header("✅ EDA COMPLETE - SUMMARY")
    print(f"\nOutput Directory: {output_dir.absolute()}")
    print("\nTotal visualizations generated: 22 individual PNG files")
    print("\n📊 Generated Files:")
    
    all_files = sorted(output_dir.glob("*.png"))
    for i, file in enumerate(all_files, 1):
        size_mb = file.stat().st_size / 1024 / 1024
        print(f"  {i:2d}. {file.name:<50} ({size_mb:.2f} MB)")
    
    print("\n" + "="*80)
    print("  All statistical analyses printed above")
    print("  All graphs saved as individual PNG files")
    print("  Ready for use in reports, presentations, or documentation")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
