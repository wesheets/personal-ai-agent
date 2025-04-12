#!/bin/bash
echo "🧪 Running Promethios memory regression tests..."
newman run core_tests.postman_collection.json > postman_output.log

if grep -q "\"failures\": 0" postman_output.log; then
  echo "✅ All memory tests passed!"
else
  echo "❌ Memory regression detected! Check postman_output.log"
  exit 1
fi
