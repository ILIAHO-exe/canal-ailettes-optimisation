#!/usr/bin/env python3
"""
Generate 21 optimization cases (1 reference + 20 parametric)
- 1 reference case WITHOUT fins
- 20 cases WITH fins: h_fin in [2,4,6,8] mm × s_fin in [2,4,6,8,10] mm

This script:
1. Creates directories for each case
2. Copies template constant/ and system/ files
3. Creates case_info.txt with parameters for each case
"""

import os
import shutil
from pathlib import Path
import yaml

def main():
    # Load simulation parameters
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract variable parameters
    h_fins = config['geometry']['h_fin']  # [2, 4, 6, 8]
    s_fins = config['geometry']['s_fin']  # [2, 4, 6, 8, 10]
    
    # Create cases directory
    cases_dir = Path('cases')
    cases_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("📊 GENERATING 21 OPTIMIZATION CASES")
    print("=" * 80)
    
    # CASE 0: REFERENCE (no fins)
    print("\n[00/21] Creating REFERENCE case (no fins)...")
    ref_case = cases_dir / "00_Reference_NoFins"
    ref_case.mkdir(exist_ok=True)
    
    # Copy constant and system directories
    shutil.copytree('template_constant', ref_case / 'constant', dirs_exist_ok=True)
    shutil.copytree('template_system', ref_case / 'system', dirs_exist_ok=True)
    
    # Create case info file
    with open(ref_case / 'case_info.txt', 'w') as f:
        f.write("REFERENCE CASE - NO FINS\n")
        f.write("h_fin = 0 mm\n")
        f.write("s_fin = 0 mm\n")
        f.write("Description: Channel without fins for baseline comparison\n")
    
    print(f"    Created: {ref_case}")
    
    # CASES 1-20: PARAMETRIC (with fins)
    case_num = 1
    for h_fin in h_fins:
        for s_fin in s_fins:
            case_name = f"{case_num:02d}_h{h_fin}_s{s_fin}"
            case_dir = cases_dir / case_name
            case_dir.mkdir(exist_ok=True)
            
            print(f"\n[{case_num:02d}/21] Creating case: h_fin={h_fin}mm, s_fin={s_fin}mm")
            
            # Copy constant and system directories
            shutil.copytree('template_constant', case_dir / 'constant', dirs_exist_ok=True)
            shutil.copytree('template_system', case_dir / 'system', dirs_exist_ok=True)
            
            # Create case info file
            with open(case_dir / 'case_info.txt', 'w') as f:
                f.write(f"PARAMETRIC CASE {case_num}\n")
                f.write(f"h_fin = {h_fin} mm\n")
                f.write(f"s_fin = {s_fin} mm\n")
                f.write(f"Description: Rectangular fins with height {h_fin}mm, spacing {s_fin}mm\n")
            
            print(f"    Created: {case_dir}")
            case_num += 1
    
    print("\n" + "=" * 80)
    print(" ALL 21 CASES CREATED SUCCESSFULLY!")
    print("=" * 80)
    print("\nNext step:")
    print("  python3 scripts/generate_blockMeshDict.py")

if __name__ == "__main__":
    main()
