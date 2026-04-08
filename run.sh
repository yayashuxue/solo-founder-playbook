#!/bin/bash
# Run pipeline steps

PYTHON="${PYTHON:-python3}"

case "$1" in
  "step1")
    $PYTHON step1_get_video_urls.py
    ;;
  "step2")
    $PYTHON step2_get_transcripts.py
    ;;
  "step3")
    $PYTHON step3_analyze_chapters.py "${@:2}"
    ;;
  "step4")
    $PYTHON step4_summarize_and_refine.py "${@:2}"
    ;;
  "step5")
    $PYTHON step5_extract_patterns.py "${@:2}"
    ;;
  "all")
    $PYTHON run_all.py
    ;;
  *)
    echo "Usage: bash run.sh [step1|step2|step3|step4|step5|all]"
    ;;
esac

