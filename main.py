import os
import subprocess
import sys
from src.pipeline.workflow import run
def main():
	"""Launch the Streamlit app without importing project modules at module import time."""
	#app_path = os.path.join(os.path.dirname(__file__), "app.py")
	subprocess.run([sys.executable, "-m", "streamlit", "run"], check=False)


if __name__ == "__main__":
	run()