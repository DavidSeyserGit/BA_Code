#!/bin/bash

# Number of times to run the geneticAlgorithm.py script
NUM_RUNS=3

# Loop to call the program multiple times with different parameters
for ((i=1; i<=NUM_RUNS; i++))
do
  echo "Running iteration $i..."

  if [ $i -eq 1 ]; then
    python3.12 geneticAlgorithm.py -a openai -m gpt-3.5-turbo -p /mnt/d/test_ws -pf example1.txt -g 200 -b publisher -v &
  elif [ $i -eq 2 ]; then
    python3.12 geneticAlgorithm.py -a ollama -m llama3 -p /mnt/d/test_ws -pf example1.txt -g 200 -b publisher -v &
  elif [ $i -eq 3 ]; then
    python3.12 geneticAlgorithm.py -a ollama -m phi3 -p /mnt/d/test_ws -pf example1.txt -g 200 -b publisher -v &
  fi

  PID=$!

  # Monitor the program's output for the completion message
  while kill -0 $PID 2>/dev/null; do
    if tail -f /proc/$PID/fd/1 2>/dev/null | grep -q "Operation took"; then
      kill -SIGINT $PID
      wait $PID
      echo "Iteration $i completed and stopped."
      break
    fi
  done

  # Small delay before starting the next iteration (optional)
  sleep 2
done

echo "All iterations completed."