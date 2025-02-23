import pandas as pd

CSV_FILE = "backend/transcripts.csv"


def count_words_in_csv(csv_file):
    """Counts all words in the Transcript column."""
    df = pd.read_csv(csv_file)
    total_words = df["Transcript"].dropna().apply(lambda x: len(x.split())).sum()
    print(f"Total word count in the Transcript column: {total_words}")


if __name__ == "__main__":
    count_words_in_csv(CSV_FILE)
