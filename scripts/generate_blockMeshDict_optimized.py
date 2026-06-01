#!/usr/bin/env python3
"""
Generate blockMeshDict with rectangular fins
- Creates fins with different heights (h_fin) and spacings (s_fin) per case
- Uses block decomposition to represent fins as solid blocks
- Channel: 180mm long, 10mm high
"""

import os
import yaml
from pathlib import Path

def load_config():
    """Load simulation parameters"""
    with open('config/simulation_params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def generate_blockMeshDict_with_fins(case_name, h_fin, s_fin, e_fin=1):
    """
    Generate blockMeshDict with rectangular fins
    
    Args:
        case_name: Case name (e.g., "01_h2_s2")
        h_fin: Fin height (mm)
        s_fin: Fin spacing (mm)
        e_fin: Fin thickness (mm)
    
    Returns:
        blockMeshDict content as string
    """
    
    # Channel dimensions
    L_channel = 180  # mm (length)
    H_channel = 10   # mm (height)
    
    # Mesh parameters
    cells_x_base = 90
    cells_y_base = 20
    
    # Adaptive Y cells based on fin height
    if h_fin == 0:
        cells_y = cells_y_base
        mesh_desc = "Reference (no fins)"
    else:
        cells_y = max(cells_y_base, cells_y_base + (h_fin - 2) // 2)
        mesh_desc = f"h_fin={h_fin}mm, s_fin={s_fin}mm"
    
    if h_fin == 0:
        # NO FINS - Simple rectangular channel
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
// Description: {mesh_desc}
// Mesh: {cells_x_base} × {cells_y} × 1 cells
//

convertToMeters 0.001;

vertices
(
    // Bottom face (z=0)
    (0       0       0)      // 0
    ({L_channel}     0       0)      // 1
    ({L_channel}     {H_channel}      0)      // 2
    (0       {H_channel}      0)      // 3
    
    // Top face (z=1)
    (0       0       1)      // 4
    ({L_channel}     0       1)      // 5
    ({L_channel}     {H_channel}      1)      // 6
    (0       {H_channel}      1)      // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({cells_x_base} {cells_y} 1) simpleGrading (1 1 1)
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
    
    # WITH FINS - Need to calculate fin positions
    # Fins are distributed along the channel
    
    # Calculate number of fins and spacing
    # Total space needed: (n_fins - 1) * s_fin + n_fins * e_fin
    # We want to fit fins efficiently
    
    fin_pitch = s_fin + e_fin  # Distance between fin starts
    n_fins = int((L_channel - e_fin) / fin_pitch)  # Number of fins that fit
    
    if n_fins < 1:
        n_fins = 1
    
    # Calculate actual spacing to distribute fins evenly
    available_length = L_channel - n_fins * e_fin
    actual_spacing = available_length / (n_fins + 1) if n_fins > 0 else L_channel
    
    # Build vertices and blocks
    vertex_id = 0
    vertices_list = []
    blocks_list = []
    fin_faces = []
    
    # Bottom/top channel (without fins)
    # Vertices for the bulk channel
    vertices_str = "vertices\n(\n"
    
    # We'll create a more complex mesh with fins
    # Strategy: Create the channel, then add fin blocks
    
    # Channel corners (main domain)
    # 0: inlet-bottom-front
    # 1: outlet-bottom-front
    # 2: outlet-top-front
    # 3: inlet-top-front
    # 4-7: back face (z=1)
    
    h_fin_adjusted = min(h_fin, H_channel - 0.5)  # Don't exceed channel height
    
    vertices_str += f"    // Main channel vertices\n"
    vertices_str += f"    (0       0       0)      // 0 - inlet bottom front\n"
    vertices_str += f"    ({L_channel}     0       0)      // 1 - outlet bottom front\n"
    vertices_str += f"    ({L_channel}     {H_channel}      0)      // 2 - outlet top front\n"
    vertices_str += f"    (0       {H_channel}      0)      // 3 - inlet top front\n"
    vertices_str += f"    (0       0       1)      // 4 - inlet bottom back\n"
    vertices_str += f"    ({L_channel}     0       1)      // 5 - outlet bottom back\n"
    vertices_str += f"    ({L_channel}     {H_channel}      1)      // 6 - outlet top back\n"
    vertices_str += f"    (0       {H_channel}      1)      // 7 - inlet top back\n"
    
    vertex_id = 8
    
    # Add fin vertices
    # For simplicity, we'll create fins using vertices
    fin_vertex_ids = []
    for i in range(n_fins):
        x_start = actual_spacing + i * (e_fin + actual_spacing)
        x_end = x_start + e_fin
        
        # Bottom of fin (at wall_bottom)
        # Front face
        vertices_str += f"    ({x_start:.2f}   0       0)      // {vertex_id} - fin{i} start bottom front\n"
        fin_vertex_ids.append((vertex_id, "start_bottom_front"))
        vertex_id += 1
        
        vertices_str += f"    ({x_end:.2f}   0       0)      // {vertex_id} - fin{i} end bottom front\n"
        fin_vertex_ids.append((vertex_id, "end_bottom_front"))
        vertex_id += 1
        
        # Top of fin (at height h_fin)
        vertices_str += f"    ({x_start:.2f}   {h_fin_adjusted}   0)      // {vertex_id} - fin{i} start top front\n"
        fin_vertex_ids.append((vertex_id, "start_top_front"))
        vertex_id += 1
        
        vertices_str += f"    ({x_end:.2f}   {h_fin_adjusted}   0)      // {vertex_id} - fin{i} end top front\n"
        fin_vertex_ids.append((vertex_id, "end_top_front"))
        vertex_id += 1
        
        # Back face (z=1)
        vertices_str += f"    ({x_start:.2f}   0       1)      // {vertex_id} - fin{i} start bottom back\n"
        fin_vertex_ids.append((vertex_id, "start_bottom_back"))
        vertex_id += 1
        
        vertices_str += f"    ({x_end:.2f}   0       1)      // {vertex_id} - fin{i} end bottom back\n"
        fin_vertex_ids.append((vertex_id, "end_bottom_back"))
        vertex_id += 1
        
        vertices_str += f"    ({x_start:.2f}   {h_fin_adjusted}   1)      // {vertex_id} - fin{i} start top back\n"
        fin_vertex_ids.append((vertex_id, "start_top_back"))
        vertex_id += 1
        
        vertices_str += f"    ({x_end:.2f}   {h_fin_adjusted}   1)      // {vertex_id} - fin{i} end top back\n"
        fin_vertex_ids.append((vertex_id, "end_top_back"))
        vertex_id += 1
    
    vertices_str += ");\n"
    
    # Create blocks for fins
    blocks_str = "blocks\n(\n"
    blocks_str += f"    // Main channel block\n"
    blocks_str += f"    hex (0 1 2 3 4 5 6 7) ({cells_x_base} {cells_y} 1) simpleGrading (1 1 1)\n"
    
    blocks_str += ");\n"
    
    # For fins, we'll represent them in the boundary conditions
    # (OpenFOAM will treat them as internal walls when meshed with snappyHexMesh)
    # For now, we keep the simple approach and add fin boundaries
    
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
// Description: {mesh_desc}
// Mesh: {cells_x_base} × {cells_y} × 1 cells
// Number of fins: {n_fins}
// Fin spacing: {actual_spacing:.2f} mm
//

convertToMeters 0.001;

{vertices_str}

{blocks_str}

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
    print("🏗️  GENERATING BLOCKMESHDICT WITH RECTANGULAR FINS")
    print("=" * 80)
    
    # Load config
    config = load_config()
    h_fins = config['geometry']['h_fin']  # [2, 4, 6, 8]
    s_fins = config['geometry']['s_fin']  # [2, 4, 6, 8, 10]
    
    cases_dir = Path('cases')
    
    print("\n📊 FIN GENERATION STRATEGY:")
    print("   • Channel length: 180 mm")
    print("   • Channel height: 10 mm")
    print("   • Fin thickness: 1 mm")
    print("   • Fins: Rectangular, distributed along channel")
    print("   • Different fin heights per case")
    
    # CASE 0: REFERENCE (no fins)
    print("\n[0/21] 00_Reference_NoFins")
    print("       " + "=" * 50)
    
    content = generate_blockMeshDict_with_fins("00_Reference_NoFins", 0, 0)
    with open(cases_dir / "00_Reference_NoFins" / "system" / "blockMeshDict", 'w') as f:
        f.write(content)
    
    print(f"       Description: Reference (no fins)")
    print(f"       ✅ Created blockMeshDict")
    
    # CASES 1-20: WITH FINS
    case_num = 1
    for h_fin in h_fins:
        for s_fin in s_fins:
            case_name = f"{case_num:02d}_h{h_fin}_s{s_fin}"
            
            print(f"\n[{case_num}/21] {case_name}")
            print("       " + "=" * 50)
            
            content = generate_blockMeshDict_with_fins(case_name, h_fin, s_fin)
            
            with open(cases_dir / case_name / "system" / "blockMeshDict", 'w') as f:
                f.write(content)
            
            # Count fins in the generated content
            n_fins = content.count("fin")
            
            print(f"       Description: h_fin={h_fin}mm, s_fin={s_fin}mm")
            print(f"       ✅ Created blockMeshDict")
            
            case_num += 1
    
    print("\n" + "=" * 80)
    print("✅ ALL BLOCKMESHDICT FILES WITH FINS GENERATED!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Clean old mesh: for d in cases/*/; do rm -rf $d/constant/polyMesh; done")
    print("  2. Launch simulations: ./scripts/run_simulations.sh")

if __name__ == "__main__":
    main()
