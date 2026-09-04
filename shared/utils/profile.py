
import time
import cProfile

def fast_function():
    time.sleep(0.1)  # Simulate a quick operation

def slow_function():
    time.sleep(0.5)  # Simulate a slower operation

def main():
    for _ in range(5):
        fast_function()
    for _ in range(2):
        slow_function()

if name == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()  # Start profiling
    main()             # Run the code to profile
    profiler.disable() # Stop profiling
    profiler.print_stats(sort="time")  # Print profiling results sorted by time