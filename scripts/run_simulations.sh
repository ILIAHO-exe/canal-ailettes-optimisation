#!/bin/bash

################################################################################
# Launch all 21 OpenFOAM simulations
# - Creates mesh for each case
# - Runs buoyantBoussinesqPimpleFoam solver
# - Logs all output
################################################################################

echo ""
echo "=================================="
echo "🚀 LAUNCHING ALL 21 SIMULATIONS"
echo "=================================="
echo ""
echo "Start time: $(date)"
echo ""

cases_dir="cases"
total_cases=$(ls -d $cases_dir/*/ 2>/dev/null | wc -l)
current_case=1

# Counter for successful/failed cases
success=0
failed=0

for case_path in $cases_dir/*/; do
    case_name=$(basename "$case_path")
    
    echo ""
    echo "[$current_case/$total_cases] Processing: $case_name"
    echo "========================================"
    
    cd "$case_path"
    
    # Create the mesh
    echo "  📐 Creating mesh with blockMesh..."
    blockMesh > log.blockMesh 2>&1
    
    if [ $? -ne 0 ]; then
        echo "  ❌ Mesh generation FAILED!"
        echo "    Error details:"
        tail -10 log.blockMesh | sed 's/^/    /'
        failed=$((failed + 1))
        cd ../..
        current_case=$((current_case + 1))
        continue
    fi
    
    # Count cells
    num_cells=$(grep "Number of cells" log.blockMesh | awk '{print $NF}')
    echo "  ✅ Mesh created: $num_cells cells"
    
    # Run simulation
    echo "  ▶️  Starting simulation with buoyantBoussinesqPimpleFoam..."
    buoyantBoussinesqPimpleFoam > log.simulation 2>&1
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Simulation completed successfully"
        success=$((success + 1))
        
        # Check if steady state reached
        final_time=$(grep "^Time = " log.simulation | tail -1 | awk '{print $3}')
        echo "    Final time: $final_time s"
    else
        echo "  ❌ Simulation FAILED"
        echo "    Error details (last 20 lines):"
        tail -20 log.simulation | sed 's/^/    /'
        failed=$((failed + 1))
    fi
    
    cd ../..
    current_case=$((current_case + 1))
done

echo ""
echo "=================================="
echo "✅ ALL SIMULATIONS COMPLETED!"
echo "=================================="
echo ""
echo "Summary:"
echo "  ✅ Successful: $success / $total_cases"
echo "  ❌ Failed: $failed / $total_cases"
echo ""
echo "End time: $(date)"
echo ""
echo "Next step:"
echo "  python3 scripts/extract_results.py"
echo ""
