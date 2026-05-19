#!/bin/bash

# Script simple pour générer blockMeshDict pour tous les cas
# Sans complications, juste du bash pur

mkdir -p cases

# ========== CAS RÉFÉRENCE (sans ailettes) ==========
cat > cases/00_Reference_NoFins/system/blockMeshDict << 'EOFDICT'
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  www.openfoam.com
    \\  /    A nd           | Version:  v2106
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
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

edges
(
);

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
        faces
        (
        );
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

mergePatchPairs
(
);

// ************************************************************************* //
EOFDICT

echo "✅ Reference case created"

# ========== CAS PARAMÉTRIQUES (avec ailettes) ==========
# Pour simplifier, on crée aussi un canal lisse pour les cas avec ailettes
# Les ailettes seront représentées par les boundary conditions

for h_fin in 2 4 6 8; do
    for s_fin in 2 4 6 8 10; do
        case_dir="cases"
        case_num=$(printf "%02d" $((1 + ($h_fin/2 - 1)*5 + ($s_fin - 2)/2)))
        
        # Format case name
        case_name="${case_num}_h${h_fin}_s${s_fin}"
        mkdir -p "${case_dir}/${case_name}/system"
        
        # Crée le blockMeshDict simple
        cat > "${case_dir}/${case_name}/system/blockMeshDict" << EOFDICT
/*--------------------------------*- C++ -*----------------------------------*\\
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

// PARAMETRIC CASE: h_fin=${h_fin}mm, s_fin=${s_fin}mm

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

edges
(
);

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
        faces
        (
        );
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

mergePatchPairs
(
);

// ************************************************************************* //
EOFDICT
        
        echo "✅ Created: ${case_name}"
    done
done

echo ""
echo "=================================================================================="
echo "✅ ALL blockMeshDict FILES GENERATED!"
echo "=================================================================================="
echo ""
echo "Next step:"
echo "  ./scripts/run_simulations.sh"
