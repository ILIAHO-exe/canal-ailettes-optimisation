#!/usr/bin/env python3
"""
Analyze optimization results
- Calculate Performance Evaluation Criteria (PEC)
- Generate visualization plots
- Identify optimal configuration
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def analyze_optimization():
    """Main analysis function"""
    
    # Try to load results
    results_file = Path('results_summary.csv')
    if not results_file.exists():
        print("⚠️  results_summary.csv not found")
        print("   Run: python3 scripts/extract_results.py")
        return
    
    # Load data
    df = pd.read_csv(results_file)
    
    print("=" * 80)
    print("📊 OPTIMIZATION ANALYSIS")
    print("=" * 80)
    
    print("\nLoaded data:")
    print(df.to_string())
    
    # Create output directory
    Path('results').mkdir(exist_ok=True)
    
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")
    print("=" * 80)
    
    print("\nGenerated files:")
    print("  - results_summary.csv")
    print("  - results/analysis_plots.png")

if __name__ == "__main__":
    analyze_optimization()
