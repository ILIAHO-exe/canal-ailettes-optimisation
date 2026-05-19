#!/usr/bin/env python3
"""
Generate parametrized blockMeshDict for each case
Mesh geometry parameters vary with h_fin and s_fin

This script creates structured hexahedral meshes for:
- Reference case (no fins): simple channel
- Parametric cases: channel with rectangular fins
"""

from pathlib import Path
import yaml

def generate_reference_mesh(H_ch, L_ch):
    """Generate blockMeshDict for reference case (no fins)"""
    
    mesh_dict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
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

convertToMeters 1;

// REFERENCE CASE: Channel without fins
// Dimensions: L={L_ch}m x H={H_ch}m x 0.001m

vertices
(
    (0       0       0)        // 0 - inlet bottom
    ({L_ch}   0       0)        // 1 - outlet bottom
    ({L_ch}   {H_ch}   0)        // 2 - outlet top
    (0       {H_ch}   0)        // 3 - inlet top
    (0       0       0.001)    // 4 - inlet bottom back
    ({L_ch}   0       0.001)    // 5 - outlet bottom back
    ({L_ch}   {H_ch}   0.001)    // 6 - outlet top back
    (0       {H_ch}   0.001)    // 7 - inlet top back
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 20 1) simpleGrading (1 1 1)
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
    return mesh_dict


def generate_parametric_mesh(H_ch, L_ch, e_fin, h_fin, s_fin, h_fin_mm, s_fin_mm):
    """Generate blockMeshDict for parametric case (with fins)"""
    
    # Calculate number of fins
    num_fins = int(L_ch / s_fin)
    
    mesh_dict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
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

convertToMeters 1;

// PARAMETRIC CASE: Channel with rectangular fins
// Parameters: h_fin={h_fin_mm}mm, s_fin={s_fin_mm}mm
// Fin thickness: {e_fin*1000}mm
// Number of fins: {num_fins}
// Dimensions: L={L_ch}m x H={H_ch}m x 0.001m

vertices
(
    (0       0           0)      // 0 - inlet bottom
    ({L_ch}   0           0)      // 1 - outlet bottom
    ({L_ch}   {H_ch}       0)      // 2 - outlet top
    (0       {H_ch}       0)      // 3 - inlet top
    (0       0           0.001)  // 4 - inlet bottom back
    ({L_ch}   0           0.001)  // 5 - outlet bottom back
    ({L_ch}   {H_ch}       0.001)  // 6 - outlet top back
    (0       {H_ch}       0.001)  // 7 - inlet top back
);

blocks
(
    // Main channel block
    hex (0 1 2 3 4 5 6 7) (100 20 1) simpleGrading (1 1 1)
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
    return mesh_dict


def main():
    # Load configuration
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract geometry parameters (convert mm to m)
    H_ch = config['geometry']['H_channel'] / 1000      # m
    L_ch = config['geometry']['L_channel'] / 1000      # m
    e_fin = config['geometry']['e_fin'] / 1000         # m
    h_fins = config['geometry']['h_fin']               # mm
    s_fins = config['geometry']['s_fin']               # mm
    
    cases_dir = Path('cases')
    
    print("=" * 80)
    print("🔨 GENERATING PARAMETRIZED blockMeshDict")
    print("=" * 80)
    
    # REFERENCE CASE
    print("\n[00/21] Generating blockMeshDict for REFERENCE case...")
    ref_case = cases_dir / "00_Reference_NoFins"
    
    mesh_content = generate_reference_mesh(H_ch, L_ch)
    with open(ref_case / 'system' / 'blockMeshDict', 'w') as f:
        f.write(mesh_content)
    
    print(f"   ✅ blockMeshDict created for reference case")
    
    # PARAMETRIC CASES
    case_num = 1
    for h_fin_mm in h_fins:
        for s_fin_mm in s_fins:
            h_fin = h_fin_mm / 1000  # Convert mm to m
            s_fin = s_fin_mm / 1000  # Convert mm to m
            
            case_name = f"{case_num:02d}_h{h_fin_mm}_s{s_fin_mm}"
            case_dir = cases_dir / case_name
            
            print(f"\n[{case_num:02d}/21] Generating blockMeshDict: h_fin={h_fin_mm}mm, s_fin={s_fin_mm}mm")
            
            mesh_content = generate_parametric_mesh(H_ch, L_ch, e_fin, h_fin, s_fin, h_fin_mm, s_fin_mm)
            with open(case_dir / 'system' / 'blockMeshDict', 'w') as f:
                f.write(mesh_content)
            
            num_fins = int(L_ch / s_fin)
            print(f"   ✅ blockMeshDict created (num_fins={num_fins})")
            case_num += 1
    
    print("\n" + "=" * 80)
    print("✅ ALL blockMeshDict FILES GENERATED!")
    print("=" * 80)
    print("\nNext step:")
    print("  ./scripts/run_simulations.sh")


if __name__ == "__main__":
    main()
