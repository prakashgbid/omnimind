#!/bin/bash
# Test OSA with interactive commands

echo "Testing OSA Claude-style interface..."
echo ""

# Create a test input file
cat > /tmp/osa_test_input.txt << 'EOF'
Write a simple hello world function
exit
EOF

# Run OSA with test input
python3 osa < /tmp/osa_test_input.txt

echo ""
echo "Test complete!"