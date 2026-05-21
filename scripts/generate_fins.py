#!/usr/bin/env python3
"""
Génère blockMeshDict avec AILETTES RÉELLES
Code SIMPLE et FONCTIONNEL
"""

import os
from pathlib import Path

def create_blockmesh_with_fins(case_dir, h_fin_mm, s_fin_mm, case_name):
    """
    Crée un blockMeshDict avec ailettes rectangulaires
    
    Stratégie simple:
    - Diviser le canal en sections (inlet, ailettes, espacements, outlet)
    - Chaque section = un bloc hexahédral
    """
    
    # Paramètres (en mètres)
    L_ch = 0.1      # Longueur canal = 100mm
    H_ch = 0.01     # Hauteur canal = 10mm
    W_ch = 0.001    # Profondeur = 1mm (2D)
    e_fin = 0.001   # Épaisseur ailette = 1mm
    
    h_fin = h_fin_mm / 1000  # Convertir mm -> m
    s_fin = s_fin_mm / 1000  # Convertir mm -> m
    
    # Cas référence: juste un bloc
    if h_fin_mm == 0:
        mesh = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  www.openfoam.com
    \\\\  /    A nd           | Version:  v2106
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    (0 0 0)
    (0.1 0 0)
    (0.1 0.01 0)
    (0 0.01 0)
    (0 0 0.001)
    (0.1 0 0.001)
    (0.1 0.01 0.001)
    (0 0.01 0.001)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (100 20 1) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 3 7 4)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }
    wall_bottom
    {
        type wall;
        faces
        (
            (0 1 5 4)
        );
    }
    wall_top
    {
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }
    fins
    {
        type wall;
        faces ();
    }
    front
    {
        type empty;
        faces
        (
            (0 3 2 1)
        );
    }
    back
    {
        type empty;
        faces
        (
            (4 5 6 7)
        );
    }
);

// ************************************************************************* //
"""
        return mesh
    
    # CAS AVEC AILETTES
    num_fins = int(L_ch / s_fin)
    
    vertices = []
    blocks = []
    inlet_faces = []
    outlet_faces = []
    wall_bottom_faces = []
    fins_faces = []
    
    vertex_id = 0
    x_pos = 0.0
    
    # ===== SECTION INLET =====
    inlet_width = 0.005  # 5mm avant première ailette
    if inlet_width < L_ch:
        v0 = vertex_id
        vertices.extend([
            (0, 0, 0),
            (inlet_width, 0, 0),
            (inlet_width, H_ch, 0),
            (0, H_ch, 0),
            (0, 0, W_ch),
            (inlet_width, 0, W_ch),
            (inlet_width, H_ch, W_ch),
            (0, H_ch, W_ch),
        ])
        blocks.append(f"hex ({v0} {v0+1} {v0+2} {v0+3} {v0+4} {v0+5} {v0+6} {v0+7}) (5 20 1) simpleGrading (1 1 1)")
        inlet_faces.append((v0, v0+3, v0+7, v0+4))
        wall_bottom_faces.append((v0, v0+1, v0+5, v0+4))
        vertex_id += 8
        x_pos = inlet_width
    
    # ===== BOUCLE AILETTES =====
    for i in range(num_fins):
        if x_pos >= L_ch - 0.001:
            break
        
        # Position ailette
        x_fin_start = x_pos
        x_fin_end = min(x_fin_start + e_fin, L_ch)
        
        # Bloc AILETTE
        v0 = vertex_id
        vertices.extend([
            (x_fin_start, 0, 0),
            (x_fin_end, 0, 0),
            (x_fin_end, h_fin, 0),
            (x_fin_start, h_fin, 0),
            (x_fin_start, 0, W_ch),
            (x_fin_end, 0, W_ch),
            (x_fin_end, h_fin, W_ch),
            (x_fin_start, h_fin, W_ch),
        ])
        
        nx_fin = max(1, int((x_fin_end - x_fin_start) * 1000))
        ny_fin = max(1, int(h_fin * 1000 / 5))
        blocks.append(f"hex ({v0} {v0+1} {v0+2} {v0+3} {v0+4} {v0+5} {v0+6} {v0+7}) ({nx_fin} {ny_fin} 1) simpleGrading (1 1 1)")
        
        # Faces ailette
        fins_faces.append((v0, v0+1, v0+5, v0+4))      # Base
        fins_faces.append((v0, v0+3, v0+7, v0+4))      # Côté gauche
        fins_faces.append((v0+1, v0+2, v0+6, v0+5))    # Côté droit
        
        vertex_id += 8
        x_pos = x_fin_end
        
        # Bloc ESPACEMENT
        x_sp_end = min(x_pos + (s_fin - e_fin), L_ch)
        
        if x_sp_end > x_pos:
            v0 = vertex_id
            vertices.extend([
                (x_pos, 0, 0),
                (x_sp_end, 0, 0),
                (x_sp_end, H_ch, 0),
                (x_pos, H_ch, 0),
                (x_pos, 0, W_ch),
                (x_sp_end, 0, W_ch),
                (x_sp_end, H_ch, W_ch),
                (x_pos, H_ch, W_ch),
            ])
            
            nx_sp = max(1, int((x_sp_end - x_pos) * 1000))
            blocks.append(f"hex ({v0} {v0+1} {v0+2} {v0+3} {v0+4} {v0+5} {v0+6} {v0+7}) ({nx_sp} 20 1) simpleGrading (1 1 1)")
            
            wall_bottom_faces.append((v0, v0+1, v0+5, v0+4))
            
            vertex_id += 8
            x_pos = x_sp_end
    
    # ===== SECTION OUTLET =====
    if x_pos < L_ch:
        v0 = vertex_id
        vertices.extend([
            (x_pos, 0, 0),
            (L_ch, 0, 0),
            (L_ch, H_ch, 0),
            (x_pos, H_ch, 0),
            (x_pos, 0, W_ch),
            (L_ch, 0, W_ch),
            (L_ch, H_ch, W_ch),
            (x_pos, H_ch, W_ch),
        ])
        
        nx_out = max(1, int((L_ch - x_pos) * 1000))
        blocks.append(f"hex ({v0} {v0+1} {v0+2} {v0+3} {v0+4} {v0+5} {v0+6} {v0+7}) ({nx_out} 20 1) simpleGrading (1 1 1)")
        
        outlet_faces.append((v0+1, v0+2, v0+6, v0+5))
        wall_bottom_faces.append((v0, v0+1, v0+5, v0+4))
        
        vertex_id += 8
    
    # Construire le blockMeshDict
    mesh = f"""/*--------------------------------*- C++ -*----------------------------------*\\
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
    location    "system";
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

// {case_name}: h_fin={h_fin_mm}mm, s_fin={s_fin_mm}mm, num_fins={num_fins}

vertices
(
"""
    
    for v in vertices:
        mesh += f"    ({v[0]} {v[1]} {v[2]})\n"
    
    mesh += """);

blocks
(
"""
    
    for block in blocks:
        mesh += f"    {block}\n"
    
    mesh += """);

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
        mesh += f"            ({face[0]} {face[1]} {face[2]} {face[3]})\n"
    
    mesh += """        );
    }
    outlet
    {
        type patch;
        faces
        (
"""
    
    for face in outlet_faces:
        mesh += f"            ({face[0]} {face[1]} {face[2]} {face[3]})\n"
    
    mesh += """        );
    }
    wall_bottom
    {
        type wall;
        faces
        (
"""
    
    for face in wall_bottom_faces:
        mesh += f"            ({face[0]} {face[1]} {face[2]} {face[3]})\n"
    
    mesh += """        );
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
        mesh += f"            ({face[0]} {face[1]} {face[2]} {face[3]})\n"
    
    mesh += """        );
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
    
    return mesh


def main():
    cases_base = Path("cases")
    
    print("=" * 80)
    print("🔧 GENERATING blockMeshDict WITH REAL FINS")
    print("=" * 80)
    
    # Cas référence
    print("\n[00/21] Reference case (no fins)...")
    ref_case = cases_base / "00_Reference_NoFins"
    ref_case.mkdir(parents=True, exist_ok=True)
    (ref_case / "system").mkdir(exist_ok=True)
    
    mesh = create_blockmesh_with_fins(str(ref_case), 0, 0, "Reference")
    with open(ref_case / "system" / "blockMeshDict", "w") as f:
        f.write(mesh)
    
    print("    Reference case created")
    
    # Cas paramétriques
    h_fins = [2, 4, 6, 8]
    s_fins = [2, 4, 6, 8, 10]
    case_num = 1
    
    for h_fin in h_fins:
        for s_fin in s_fins:
            case_name = f"{case_num:02d}_h{h_fin}_s{s_fin}"
            case_dir = cases_base / case_name
            case_dir.mkdir(parents=True, exist_ok=True)
            (case_dir / "system").mkdir(exist_ok=True)
            
            print(f"[{case_num:02d}/20] Creating {case_name}...")
            
            mesh = create_blockmesh_with_fins(str(case_dir), h_fin, s_fin, case_name)
            with open(case_dir / "system" / "blockMeshDict", "w") as f:
                f.write(mesh)
            
            print(f"       {case_name} created")
            case_num += 1
    
    print("\n" + "=" * 80)
    print(" ALL blockMeshDict WITH FINS GENERATED!")
    print("=" * 80)
    print("\nNext step:")
    print("  ./scripts/run_simulations.sh")


if __name__ == "__main__":
    main()
