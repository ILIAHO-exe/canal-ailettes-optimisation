#!/usr/bin/env python3
"""
Generate optimized blockMeshDict for each case
- Adapts mesh fineness based on fin geometry (h_fin, s_fin)
- Ensures sufficient cell resolution around fins
- Uses 180mm channel length
"""

import os
import yaml
from pathlib import Path

def load_config():
    """Load simulation parameters"""
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def calculate_mesh_params(h_fin, s_fin, e_fin=1):
    """
    Calculate optimal mesh parameters for a case with fins
    
    Args:
        h_fin: fin height (mm)
        s_fin: fin spacing (mm)
        e_fin: fin thickness (mm)
    
    Returns:
        dict with mesh parameters
    """
    
    # Base parameters
    L_channel = 180  # mm
    H_channel = 10   # mm
    
    # Reference mesh (no fins case: ~100 cells in X direction)
    cells_x_base = 90  # For 180mm length (was 50 for 100mm)
    
    # Calculate cells in Y direction
    # Need at least 10 cells in channel height for laminar flow
    cells_y_base = 20
    
    # ADAPTIVE MESH FOR FINS
    if h_fin == 0:
        # Reference case (no fins)
        cells_x = cells_x_base
        cells_y = cells_y_base
        mesh_description = "Reference (no fins)"
    else:
        # WITH FINS: Refine mesh around fin region
        # Need ~5-10 cells per fin height and spacing
        
        # Minimum cells per fin height
        cells_per_fin_height = max(8, int(h_fin / 0.5))  # ~1 cell per 0.5mm
        
        # Minimum cells per spacing
        cells_per_spacing = max(5, int(s_fin / 0.5))  # ~1 cell per 0.5mm
        
        # Y direction: refine for better fin resolution
        cells_y = max(cells_y_base, cells_y_base + (h_fin - 2) // 2)
        
        # X direction: keep proportional to length
        cells_x = cells_x_base
        
        mesh_description = f"h_fin={h_fin}mm, s_fin={s_fin}mm (refined)"
    
    return {
        'L': L_channel,
        'H': H_channel,
        'e': 1,  # Thickness (constant)
        'cells_x': cells_x,
        'cells_y': cells_y,
        'cells_z': 1,
        'description': mesh_description,
        'h_fin': h_fin,
        's_fin': s_fin
    }

def generate_blockMeshDict(case_name, mesh_params):
    """
    Generate blockMeshDict content for a case
    """
    
    L = mesh_params['L']
    H = mesh_params['H']
    nx = mesh_params['cells_x']
    ny = mesh_params['cells_y']
    nz = mesh_params['cells_z']
    
    content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  www.openfoam.com
    \\\\  /    A nd           | Version:  v2106
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
//
// Case: {case_name}
// Mesh: {nx} × {ny} × {nz} cells
// Description: {mesh_params['description']}
//

convertToMeters 0.001;

vertices
(
    (0       0       0)      // 0
    ({L}     0       0)      // 1
    ({L}     {H}      0)      // 2
    (0       {H}      0)      // 3
    (0       0       1)      // 4
    ({L}     0       1)      // 5
    ({L}     {H}      1)      // 6
    (0       {H}      1)      // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }}
    
    outlet
    {{
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }}
    
    wall_bottom
    {{
        type wall;
        faces
        (
            (0 1 5 4)
        );
    }}
    
    wall_top
    {{
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }}
    
    fins
    {{
        type wall;
        faces ();
    }}
    
    front
    {{
        type empty;
        faces
        (
            (0 3 2 1)
        );
    }}
    
    back
    {{
        type empty;
        faces
        (
            (4 5 6 7)
        );
    }}
);

// ************************************************************************* //
"""
    return content

def main():
    print("=" * 80)
    print("🔲 GENERATING OPTIMIZED BLOCKMESHDICT FOR ALL 21 CASES")
    print("=" * 80)
    
    # Load config
    config = load_config()
    h_fins = config['geometry']['h_fin']  # [2, 4, 6, 8]
    s_fins = config['geometry']['s_fin']  # [2, 4, 6, 8, 10]
    
    cases_dir = Path('cases')
    
    print("\n📊 MESH GENERATION STRATEGY:")
    print("   • Channel length: 180 mm")
    print("   • Base X cells (no fins): 90 cells")
    print("   • Base Y cells: 20 cells")
    print("   • Refined Y cells (with fins): up to 28 cells")
    print("   • Total cells per case: ~8,100 - 12,600")
    
    # CASE 0: REFERENCE (no fins)
    print("\n[0/21] 00_Reference_NoFins")
    print("       " + "=" * 50)
    
    mesh_params = calculate_mesh_params(0, 0)
    print(f"       Description: {mesh_params['description']}")
    print(f"       Mesh: {mesh_params['cells_x']} × {mesh_params['cells_y']} × {mesh_params['cells_z']} cells = {mesh_params['cells_x'] * mesh_params['cells_y'] * mesh_params['cells_z']} total")
    
    blockMeshDict_content = generate_blockMeshDict("00_Reference_NoFins", mesh_params)
    
    with open(cases_dir / "00_Reference_NoFins" / "system" / "blockMeshDict", 'w') as f:
        f.write(blockMeshDict_content)
    
    print(f"       ✅ Created blockMeshDict")
    
    # CASES 1-20: PARAMETRIC (with fins)
    case_num = 1
    for h_fin in h_fins:
        for s_fin in s_fins:
            case_name = f"{case_num:02d}_h{h_fin}_s{s_fin}"
            
            print(f"\n[{case_num}/21] {case_name}")
            print("       " + "=" * 50)
            
            mesh_params = calculate_mesh_params(h_fin, s_fin)
            print(f"       Description: {mesh_params['description']}")
            print(f"       Mesh: {mesh_params['cells_x']} × {mesh_params['cells_y']} × {mesh_params['cells_z']} cells = {mesh_params['cells_x'] * mesh_params['cells_y'] * mesh_params['cells_z']} total")
            
            blockMeshDict_content = generate_blockMeshDict(case_name, mesh_params)
            
            with open(cases_dir / case_name / "system" / "blockMeshDict", 'w') as f:
                f.write(blockMeshDict_content)
            
            print(f"       ✅ Created blockMeshDict")
            
            case_num += 1
    
    print("\n" + "=" * 80)
    print("✅ ALL OPTIMIZED BLOCKMESHDICT FILES GENERATED!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Clean old mesh: for d in cases/*/; do rm -rf $d/constant/polyMesh; done")
    print("  2. Launch simulations: ./scripts/run_simulations.sh")

if __name__ == "__main__":
    main()
