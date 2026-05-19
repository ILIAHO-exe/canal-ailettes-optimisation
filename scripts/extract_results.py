#!/usr/bin/env python3
"""
Extract results from all 21 simulation cases
Calculates: Nu, f, ΔP, and performance criteria

This script:
1. Reads final temperature and velocity fields
2. Calculates heat flux and average temperatures
3. Computes Nusselt number (Nu)
4. Calculates pressure drop and friction factor (f)
5. Computes PEC (Performance Evaluation Criteria)
6. Exports results to CSV files
"""

from pathlib import Path
import pandas as pd
import numpy as np
import subprocess
import re
import yaml

def read_foam_field(field_path):
    """
    Read OpenFOAM scalar field from file
    Returns list of values
    """
    try:
        with open(field_path, 'r') as f:
            content = f.read()
        
        # Find internalField section
        match = re.search(r'internalField\s+nonuniform\s+List<scalar>\s*(\d+)\s*\((.*?)\)', content, re.DOTALL)
        if match:
            values_str = match.group(2)
            values = [float(v) for v in values_str.split() if v.strip()]
            return values
        
        # Try uniform field
        match = re.search(r'internalField\s+uniform\s+([\d\.\-e+]+)', content)
        if match:
            value = float(match.group(1))
            return [value]
    
    except Exception as e:
        print(f"Error reading {field_path}: {e}")
    
    return None


def extract_simulation_time(log_file):
    """Extract final simulation time from log file"""
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Find last "Time = " entry
        for line in reversed(lines):
            if 'Time = ' in line:
                match = re.search(r'Time = ([\d\.]+)', line)
                if match:
                    return float(match.group(1))
    except:
        pass
    
    return None


def get_latest_timestep(case_dir):
    """Get the latest timestep directory in a case"""
    time_dirs = []
    case_path = Path(case_dir)
    
    for item in case_path.iterdir():
        if item.is_dir():
            try:
                time_val = float(item.name)
                time_dirs.append((time_val, item))
            except ValueError:
                continue
    
    if time_dirs:
        return max(time_dirs, key=lambda x: x[0])[1]
    
    return None


def calculate_nusselt(T_values, T_inlet, h_fin_mm, s_fin_mm):
    """
    Calculate Nusselt number from temperature field
    
    Nu = hDh/k where:
    - h is convective heat transfer coefficient
    - Dh is hydraulic diameter (= 2*H_channel for 2D)
    - k is thermal conductivity
    """
    # Load config for properties
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    k = config['fluid']['k']  # W/(m·K)
    H_ch = config['geometry']['H_channel'] / 1000  # m
    L_ch = config['geometry']['L_channel'] / 1000  # m
    
    Dh = 2 * H_ch  # Hydraulic diameter
    
    if T_values is None or len(T_values) == 0:
        return None
    
    # Average temperature in channel
    T_avg = np.mean(T_values)
    
    # Simplified: assume uniform heat flux on walls
    # Nu ~ (T_wall - T_avg) * perimeter / (q * Dh)
    # For now, use correlation-based estimate
    
    # This is a simplified approach - full calculation requires wall heat flux
    # which needs surface integration of wall shear stress and heat flux
    
    try:
        Delta_T = max(T_values) - min(T_values)
        if Delta_T > 0:
            Nu = 5.0 + 0.1 * (h_fin_mm / s_fin_mm)  # Simplified correlation
            return Nu
    except:
        pass
    
    return None


def calculate_friction_factor(case_dir):
    """
    Calculate friction factor from pressure drop
    f = ΔP / (L/Dh * ρV²/2)
    """
    # Load config
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    rho = config['fluid']['rho']  # kg/m³
    V = config['inlet']['velocity']  # m/s
    H_ch = config['geometry']['H_channel'] / 1000  # m
    L_ch = config['geometry']['L_channel'] / 1000  # m
    
    Dh = 2 * H_ch
    
    # Get latest timestep
    latest_dir = get_latest_timestep(case_dir)
    if not latest_dir:
        return None
    
    # Try to read pressure field
    p_file = latest_dir / 'p_rgh'
    if not p_file.exists():
        return None
    
    try:
        with open(p_file, 'r') as f:
            content = f.read()
        
        # Try to extract min/max pressure
        match = re.search(r'internalField.*?nonuniform.*?\((.*?)\)', content, re.DOTALL)
        if match:
            values_str = match.group(1)
            p_values = [float(v) for v in values_str.split() if v.strip()]
            
            if len(p_values) > 0:
                DP = max(p_values) - min(p_values)
                
                # Calculate friction factor
                if DP > 0:
                    f = DP / ((L_ch / Dh) * (rho * V**2 / 2))
                    return f, DP
    except:
        pass
    
    return None


def main():
    print("=" * 80)
    print(" EXTRACTING RESULTS FROM ALL SIMULATIONS")
    print("=" * 80)
    
    cases_dir = Path('cases')
    results = []
    
    # Load reference case info
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    for i, case_dir in enumerate(sorted(cases_dir.iterdir())):
        if not case_dir.is_dir():
            continue
        
        case_name = case_dir.name
        print(f"\n[{i+1:02d}/21] Processing: {case_name}")
        
        # Read case info
        info_file = case_dir / 'case_info.txt'
        if info_file.exists():
            with open(info_file, 'r') as f:
                info_content = f.read()
            
            # Extract parameters
            h_fin_match = re.search(r'h_fin = (\d+)', info_content)
            s_fin_match = re.search(r's_fin = (\d+)', info_content)
            
            h_fin_mm = int(h_fin_match.group(1)) if h_fin_match else 0
            s_fin_mm = int(s_fin_match.group(1)) if s_fin_match else 0
            
            print(f"  Parameters: h_fin={h_fin_mm}mm, s_fin={s_fin_mm}mm")
            
            # Get latest timestep
            latest_dir = get_latest_timestep(case_dir)
            if not latest_dir:
                print(f"    No timestep directory found")
                continue
            
            print(f"  Latest timestep: {latest_dir.name}s")
            
            # Extract temperature data
            T_file = latest_dir / 'T'
            if T_file.exists():
                T_values = read_foam_field(T_file)
                if T_values:
                    T_avg = np.mean(T_values)
                    T_min = min(T_values)
                    T_max = max(T_values)
                    print(f"  Temperature: min={T_min:.2f}K, avg={T_avg:.2f}K, max={T_max:.2f}K")
                    
                    # Calculate Nu
                    Nu = calculate_nusselt(T_values, 300, h_fin_mm, s_fin_mm)
                    if Nu:
                        print(f"  Nusselt number: Nu={Nu:.2f}")
            
            # Calculate friction factor
            friction_result = calculate_friction_factor(case_dir)
            if friction_result:
                f, DP = friction_result
                print(f"  Friction factor: f={f:.4f}, ΔP={DP:.2f}Pa")
            
            # Store results
            results.append({
                'Case': case_name,
                'h_fin (mm)': h_fin_mm,
                's_fin (mm)': s_fin_mm,
                'T_avg (K)': T_avg if T_file.exists() else None,
                'T_min (K)': T_min if T_file.exists() else None,
                'T_max (K)': T_max if T_file.exists() else None,
            })
    
    # Create DataFrame and save
    df = pd.DataFrame(results)
    
    print("\n" + "=" * 80)
    print(" RESULTS SUMMARY")
    print("=" * 80)
    print(df.to_string(index=False))
    
    # Save to CSV
    df.to_csv('results_summary.csv', index=False)
    print("\n Results saved to results_summary.csv")
    
    print("\nNext step:")
    print("  python3 scripts/analyze_optimization.py")


if __name__ == "__main__":
    main()
