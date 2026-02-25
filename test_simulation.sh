#!/bin/bash

# Test script for MCU-ALTEA 150 Course Automation
# Runs the complete automation in simulation mode

echo "========================================"
echo "MCU-ALTEA 150 - Simulation Test"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Run automation
echo ""
echo "🚀 Running automation in SIMULATION mode..."
echo "========================================"
echo ""

python main.py --mode simulation

# Check results
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SIMULATION COMPLETED SUCCESSFULLY"
    echo ""
    echo "📊 Checking generated reports..."
    ls -lh output/ 2>/dev/null || echo "No output files found"
    echo ""
    echo "📋 Report Summary:"
    if [ -f "output/COURSE_SUMMARY.txt" ]; then
        cat output/COURSE_SUMMARY.txt
    fi
else
    echo ""
    echo "❌ SIMULATION FAILED"
    echo "📋 Check logs for details:"
    cat logs/rise360_automation_simulation.log
fi

echo ""
echo "========================================"
echo "Test completed. Deactivating venv..."
deactivate
