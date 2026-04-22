#!/usr/bin/env bash
set -eo pipefail

REPO_DIR="$HOME/face_rec/repository/Snoop_bot"
FACE_REC_SCRIPT="$REPO_DIR/Face Recognition/facial_recognition_hardware.py"
FACE_STATE_SCRIPT="$REPO_DIR/face_state.py"
AUDIO_SCRIPT="$REPO_DIR/rosaudio.py"

HEADLESS=false

usage() {
    echo "Usage: $0 [--headless]"
    echo ""
    echo "  --headless   Run face recognition without the OpenCV GUI window."
    echo "               Use this when SSHing in or when no display is attached."
    exit 0
}

for arg in "$@"; do
    case "$arg" in
        --headless) HEADLESS=true ;;
        -h|--help)  usage ;;
        *)          echo "Unknown option: $arg"; usage ;;
    esac
done

PIDS=()

cleanup() {
    echo ""
    echo "[start_snoop_bot] Shutting down all nodes..."

    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "[start_snoop_bot]   Sending SIGINT to PID $pid"
            kill -INT "$pid"
        fi
    done

    echo "[start_snoop_bot] Waiting for nodes to exit (up to 10s)..."
    local deadline=$((SECONDS + 10))
    for pid in "${PIDS[@]}"; do
        while kill -0 "$pid" 2>/dev/null; do
            if (( SECONDS >= deadline )); then
                echo "[start_snoop_bot]   PID $pid did not exit in time, sending SIGKILL"
                kill -9 "$pid" 2>/dev/null
                break
            fi
            sleep 0.2
        done
    done

    echo "[start_snoop_bot] All nodes stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- Environment setup ---
echo "[start_snoop_bot] Sourcing ROS 2 Humble..."
source /opt/ros/humble/setup.bash

echo "[start_snoop_bot] Activating Python venv..."
source "$HOME/face_rec/bin/activate"

# --- Launch nodes ---
echo "[start_snoop_bot] Starting facial_recognition_hardware..."
if [ "$HEADLESS" = true ]; then
    SNOOP_HEADLESS=1 python3 "$FACE_REC_SCRIPT" &
else
    python3 "$FACE_REC_SCRIPT" &
fi
PIDS+=($!)

sleep 2

echo "[start_snoop_bot] Starting face_state..."
python3 "$FACE_STATE_SCRIPT" &
PIDS+=($!)

sleep 1

echo "[start_snoop_bot] Starting rosaudio..."
python3 "$AUDIO_SCRIPT" &
PIDS+=($!)

echo ""
echo "============================================="
echo "  Snoop Bot is running!"
echo "  Nodes: facial_recognition, face_state, audio"
if [ "$HEADLESS" = true ]; then
echo "  Mode:  HEADLESS (no GUI window)"
else
echo "  Mode:  GUI (press 'q' on video window to quit)"
fi
echo "  Press Ctrl+C to shut down gracefully"
echo "============================================="
echo ""

wait
