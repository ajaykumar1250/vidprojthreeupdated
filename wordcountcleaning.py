import pandas as pd
import re
import json
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.stem import PorterStemmer

# Load the CSV
df = pd.read_csv('/The-Office-Lines-Cleaned.csv') 

# Set up stemmer and stopwords
stemmer = PorterStemmer()
stopwords_set = set(ENGLISH_STOP_WORDS)

# Add common filler words to the stopwords list explicitly
filler_words = {"uh", "umm", "ah", "huh", "oh", "like", "well", "okay", "yeah", "alright", "mmhmm"}
stopwords_set.update(filler_words)

# Normalize speaker names
def clean_speaker_name(name):
    name = name.strip()
    name = name.replace("\\", "").replace("/", "").replace("\"", "").replace("'", "")
    return name

# Tokenize and clean a line
def clean_and_stem_line(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    filtered = [word for word in tokens if word not in stopwords_set]
    stemmed = [stemmer.stem(word) for word in filtered]
    return stemmed

# Dictionary to hold final speaker -> season -> word counts
speaker_season_word_counts = defaultdict(lambda: defaultdict(Counter))

# Process each line
for _, row in df.iterrows():
    raw_speakers = str(row['speaker'])
    season = str(row['season'])
    line = str(row['line'])

    # Normalize speaker names
    raw_speakers = clean_speaker_name(raw_speakers)

    # Split combined speakers (based on "+" or "and")
    if '+' in raw_speakers:
        speakers = raw_speakers.split('+')
    elif ' and ' in raw_speakers.lower():
        speakers = re.split(r'\band\b', raw_speakers, flags=re.IGNORECASE)
    else:
        speakers = [raw_speakers]

    speakers = [s.strip() for s in speakers if s.strip()]

    words = clean_and_stem_line(line)

    # Update word counts for each speaker and season
    for speaker in speakers:
        speaker_season_word_counts[speaker][season].update(words)
        speaker_season_word_counts[speaker]['all'].update(words)

# Convert Counters to dicts for JSON serialization
final_output = {
    speaker: {season: dict(words.most_common(100)) for season, words in seasons.items()}
    for speaker, seasons in speaker_season_word_counts.items()
}

# Save the final output to a JSON file
output_path = 'speaker_season_word_counts_post_processed.json'  # Specify the desired output path
with open(output_path, 'w') as f:
    json.dump(final_output, f)

print(f"Word counts saved to {output_path}")
