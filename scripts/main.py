import re
from speech_to_text import run_stt  # you’ll add this function to speech_to_text.py
from mistral import query_mistral
from glucose import plot_glucose, simulate_cumulative_glucose, display_calculus
from datetime import datetime, timedelta
import numpy as np
import warnings
from urllib3.exceptions import NotOpenSSLWarning

def main():
    warnings.simplefilter("ignore", NotOpenSSLWarning)

    event_log = []
    simulated_now = datetime.now()
    while True:
        input("\nPress enter to start listening...\n")
        print("Now listening for the next five seconds...")
        transcript = run_stt()
        print("Heard:", transcript)
        if "skip forward one hour" in transcript.lower():
            simulated_now += timedelta(hours=1)
            print("Skipped forward one hour. Current simulated time:", simulated_now.strftime('%H:%M:%S'))
            continue
        structured_data = query_mistral(transcript)
        print("Parsed:", structured_data)
        if not structured_data or (structured_data["carbs"] is None and structured_data["activity"] is None):
            print("I couldn't recognize this input. Skipping this event.")
            continue
        event_log.append({
            "timestamp": simulated_now,
            "carbs": structured_data["carbs"],
            "activity": structured_data["activity"],
            "duration": structured_data["duration"]
        })

        # Runs actual code
        times, glucose_levels = simulate_cumulative_glucose(event_log)
        display_calculus(glucose_levels, times)

if __name__ == "__main__":
    main()