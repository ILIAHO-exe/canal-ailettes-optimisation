#!/usr/bin/env python3
"""
Génère blockMeshDict avec AILETTES réelles (rectangulaires, 2D)

Chaque ailette = UN bloc hexahédral distinct
Les espacements = blocs séparés
"""

from pathlib import Path
import yaml

def generate_reference_mesh(H_ch, L_ch):
    """Canal lisse sans ailettes"""
    
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
    (0       0       0)        // 0
    ({L_ch}   0       0)        // 1
    ({L_ch}   {H_ch}   0)        // 2
    (0       {H_ch}   0)        // 3
    (0       0       0.001)    // 4
    ({L_ch}   0       0.001)    // 5
    ({L_ch}   {H_ch}   0.001)    // 6
    (0       {H_ch}   0.001)    // 7
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


def generate_parametric_mesh(H_ch, L_ch, e_fin, h_fin, s_fin, h_fin_mm, s_fin_mm):
    """Génère blockMeshDict avec AILETTES comme blocs hexahédraux"""
    
    num_fins = int(L_ch / s_fin)
    W_ch = 0.001  # Profondeur 2D
    
    # Générer les vertices et blocs
    vertices = []
    blocks = []
    inlet_faces = []
    outlet_faces = []
    wall_bottom_faces = []
    wall_top_faces = []
    fins_faces = []
    
    vertex_id = 0
    x_current = 0.0
    
    # ========== SECTION INLET (avant première ailette) ==========
    inlet_length = 0.005  # 5mm
    if x_current < inlet_length and inlet_length < L_ch:
        x1, x2 = x_current, inlet_length
        
        v_id = vertex_id
        vertices.extend([
            f"{x1} 0 0",
            f"{x2} 0 0",
            f"{x2} {H_ch} 0",
            f"{x1} {H_ch} 0",
            f"{x1} 0 {W_ch}",
            f"{x2} 0 {W_ch}",
            f"{x2} {H_ch} {W_ch}",
            f"{x1} {H_ch} {W_ch}",
        ])
        
        nx = max(1, int((x2 - x1) * 1000))
        blocks.append(f"hex ({v_id} {v_id+1} {v_id+2} {v_id+3} {v_id+4} {v_id+5} {v_id+6} {v_id+7}) ({nx} 20 1) simpleGrading (1 1 1)")
        
        inlet_faces.append(f"{v_id} {v_id+4} {v_id+7} {v_id+3}")
        wall_bottom_faces.append(f"{v_id} {v_id+1} {v_id+5} {v_id+4}")
        
        vertex_id += 8
        x_current = x2
    
    # ========== BOUCLE AILETTES ==========
    for i in range(num_fins):
        if x_current >= L_ch - 0.001:
            break
        
        # Position ailette
        x_fin_start = x_current
        x_fin_end = min(x_fin_start + e_fin, L_ch)
        
        # ===== BLOC AILETTE =====
        v_id = vertex_id
        vertices.extend([
            f"{x_fin_start} 0 0",
            f"{x_fin_end} 0 0",
            f"{x_fin_end} {h_fin} 0",
            f"{x_fin_start} {h_fin} 0",
            f"{x_fin_start} 0 {W_ch}",
            f"{x_fin_end} 0 {W_ch}",
            f"{x_fin_end} {h_fin} {W_ch}",
            f"{x_fin_start} {h_fin} {W_ch}",
        ])
        
        nx_fin = max(1, int((x_fin_end - x_fin_start) * 1000))
        ny_fin = max(2, int(h_fin * 1000 / 5))
        blocks.append(f"hex ({v_id} {v_id+1} {v_id+2} {v_id+3} {v_id+4} {v_id+5} {v_id+6} {v_id+7}) ({nx_fin} {ny_fin} 1) simpleGrading (1 1 1)")
        
        # Faces ailette pour boundary
        fins_faces.append(f"({v_id} {v_id+1} {v_id+5} {v_id+4})")  # Base
        fins_faces.append(f"({v_id} {v_id+3} {v_id+7} {v_id+4})")  # Côté gauche
        fins_faces.append(f"({v_id+1} {v_id+2} {v_id+6} {v_id+5})")  # Côté droit
        
        vertex_id += 8
        x_current = x_fin_end
        
        # ===== BLOC ESPACEMENT =====
        x_spacing_end = min(x_current + s_fin - e_fin, L_ch)
        
        if x_spacing_end > x_current:
            v_id = vertex_id
            vertices.extend([
                f"{x_current} 0 0",
                f"{x_spacing_end} 0 0",
                f"{x_spacing_end} {H_ch} 0",
                f"{x_current} {H_ch} 0",
                f"{x_current} 0 {W_ch}",
                f"{x_spacing_end} 0 {W_ch}",
                f"{x_spacing_end} {H_ch} {W_ch}",
                f"{x_current} {H_ch} {W_ch}",
            ])
            
            nx_sp = max(1, int((x_spacing_end - x_current) * 1000))
            blocks.append(f"hex ({v_id} {v_id+1} {v_id+2} {v_id+3} {v_id+4} {v_id+5} {v_id+6} {v_id+7}) ({nx_sp} 20 1) simpleGrading (1 1 1)")
            
            wall_bottom_faces.append(f"{v_id} {v_id+1} {v_id+5} {v_id+4}")
            
            vertex_id += 8
            x_current = x_spacing_end
    
    # ========== SECTION OUTLET (après dernière ailette) ==========
    if x_current < L_ch:
        x1, x2 = x_current, L_ch
        
        v_id = vertex_id
        vertices.extend([
            f"{x1} 0 0",
            f"{x2} 0 0",
            f"{x2} {H_ch} 0",
            f"{x1} {H_ch} 0",
            f"{x1} 0 {W_ch}",
            f"{x2} 0 {W_ch}",
            f"{x2} {H_ch} {W_ch}",
            f"{x1} {H_ch} {W_ch}",
        ])
        
        nx = max(1, int((x2 - x1) * 1000))
        blocks.append(f"hex ({v_id} {v_id+1} {v_id+2} {v_id+3} {v_id+4} {v_id+5} {v_id+6} {v_id+7}) ({nx} 20 1) simpleGrading (1 1 1)")
        
        outlet_faces.append(f"{v_id+1} {v_id+2} {v_id+6} {v_id+5}")
        wall_bottom_faces.append(f"{v_id} {v_id+1} {v_id+5} {v_id+4}")
        
        vertex_id += 8
    
    # Construire le blockMeshDict
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

// PARAMETRIC CASE WITH FINS
// h_fin={h_fin_mm}mm, s_fin={s_fin_mm}mm, num_fins={num_fins}

vertices
(
"""
    
    for v in vertices:
        mesh_dict += f"    ({v})\n"
    
    mesh_dict += """);

blocks
(
"""
    
    for block in blocks:
        mesh_dict += f"    {block}\n"
    
    mesh_dict += """);

edges ();

boundary
(
    inlet
    {
        type patch;
        faces
        (
"""
    
    for face in inlet_faces:
        mesh_dict += f"            {face}\n"
    
    mesh_dict += """        );
    }
    
    outlet
    {
        type patch;
        faces
        (
"""
    
    for face in outlet_faces:
        mesh_dict += f"            {face}\n"
    
    mesh_dict += """        );
    }
    
    wall_bottom
    {
        type wall;
        faces
        (
"""
    
    for face in wall_bottom_faces:
        mesh_dict += f"            {face}\n"
    
    mesh_dict += """        );
    }
    
    wall_top
    {
        type wall;
        faces ();
    }
    
    fins
    {
        type wall;
        faces
        (
"""
    
    for face in fins_faces:
        mesh_dict += f"            {face}\n"
    
    mesh_dict += """        );
    }
    
    front
    {
        type empty;
        faces ();
    }
    
    back
    {
        type empty;
        faces ();
    }
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
    print("🔨 GENERATING blockMeshDict WITH FINS")
    print("=" * 80)
    
    # REFERENCE CASE
    print("\n[00/21] Generating blockMeshDict for REFERENCE case...")
    ref_case = cases_dir / "00_Reference_NoFins"
    
    mesh_content = generate_reference_mesh(H_ch, L_ch)
    with open(ref_case / 'system' / 'blockMeshDict', 'w') as f:
        f.write(mesh_content)
    
    print(f"   ✅ blockMeshDict created (smooth channel, no fins)")
    
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
