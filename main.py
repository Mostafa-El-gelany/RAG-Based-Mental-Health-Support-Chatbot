import sys


def main():
	"""Launch the Streamlit app from the top-level UI entrypoint."""
	from pathlib import Path
	import subprocess

	app_path = Path(__file__).with_name("app.py")
	subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=False)


if __name__ == "__main__":
	main()