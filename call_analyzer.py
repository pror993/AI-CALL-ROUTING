import speech_recognition as sr
import spacy
import re
from textblob import TextBlob
import librosa
from transformers import pipeline
import warnings
import numpy as np
from keybert import KeyBERT
warnings.filterwarnings("ignore")


class CallAnalyzer:
    def __init__(self):
        print("Initializing Call Analyzer...")
        self.nlp = spacy.load("en_core_web_sm")
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True,
        )
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

    def analyze(self, text, audio_path, region=None):
        """
        Perform combined text and audio analysis.

        Args:
            text (str): Transcribed text from the audio call.
            audio_path (str): Path to the audio file.
            region (str, optional): Region for region-specific sentiment adjustments.

        Returns:
            dict: Combined analysis results.
        """
        # Analyze Text
        text_analysis = self.analyze_text(text, region)

        # Analyze Audio Features
        audio_features = self.extract_audio_features(audio_path)

        # Combine Sentiment and Audio Features
        combined_sentiment = self.analyze_combined_sentiment(
            text_analysis["sentiment"], audio_features
        )

        # Integrate combined sentiment into the result
        text_analysis["sentiment"] = combined_sentiment
        text_analysis["audio_features"] = audio_features

        return text_analysis

    def analyze_combined_sentiment(self, text_sentiment, audio_features):
        """
        Combine text sentiment and audio features to refine sentiment analysis.

        Args:
            text_sentiment (str): Sentiment determined from the text ("Positive", "Neutral", or "Negative").
            audio_features (dict): Extracted audio features.

        Returns:
            str: Refined overall sentiment.
        """
        # Audio thresholds for sentiment refinement
        loudness_threshold = 0.02  # Example RMS energy threshold
        calmness_threshold = 0.1  # Example zero-crossing rate threshold

        # Start with text sentiment
        final_sentiment = text_sentiment

        # Adjust sentiment based on audio features
        if audio_features["rms_energy"] > loudness_threshold:
            # Loud speech might indicate frustration or urgency
            if text_sentiment == "Neutral":
                final_sentiment = "Negative"
        elif audio_features["zero_crossing_rate"] < calmness_threshold:
            # Calm speech might indicate positivity or neutrality
            if text_sentiment == "Negative":
                final_sentiment = "Neutral"

        return final_sentiment

    def analyze_text(self, text, region=None):
        """
        Analyze the transcription for:
        - Sentiment (Text-Based)
        - Urgency
        - Intent
        - Metadata (Name, Purpose, Claim ID)
        """
        if not text.strip():
            return {
                "sentiment": "Neutral",
                "urgency": "Unknown",
                "intent": "Unknown",
                "metadata": {"name": None, "purpose": None, "claim_id": None},
            }

        # Sentiment Analysis
        sentiment = self.analyze_sentiment(text, region)

        # Urgency Detection
        urgency = self.detect_urgency(text)

        # Intent Detection
        intent = "Claim Inquiry" if "claim" in text.lower() else "General Inquiry"

        # Metadata Extraction
        name = self.extract_name(text)
        purpose = self.extract_purpose(text)
        claim_id = self.extract_claim_id(text)

        return {
            "sentiment": sentiment,
            "urgency": urgency,
            "intent": intent,
            "metadata": {"name": name, "purpose": purpose, "claim_id": claim_id},
        }

    def analyze_sentiment(self, text, region=None):
        """
        Perform sentiment analysis using TextBlob and region-specific adjustments.
        """
        sentiment, _ = self.analyze_sentiment_and_emotion(text)

        # Modify sentiment using region (if specified)
        if region:
            if region.lower() in ["north", "east"]:
                sentiment = "Neutral" if sentiment == "Negative" else sentiment

        return sentiment

    def analyze_sentiment_and_emotion(self, text):
        """
        Analyze sentiment and emotion from the text.
        """
        if not text.strip():
            return "Neutral", "neutral"

        sentiment = "Neutral"
        polarity = TextBlob(text).sentiment.polarity

        # Determine sentiment based on polarity
        if polarity > 0.2:
            sentiment = "Positive"
        elif polarity < -0.2:
            sentiment = "Negative"

        # Emotion Detection
        emotion = "neutral"
        try:
            emotions = self.emotion_classifier(text)[0]
            if max(emotions, key=lambda x: x["score"])["score"] > 0.3:
                emotion = max(emotions, key=lambda x: x["score"])["label"]
        except Exception:
            pass

        return sentiment, emotion

    def detect_urgency(self, text):
        """
        Detect urgency levels based on keywords.
        """
        urgency_levels = {
            "high": {"urgent", "emergency", "immediate", "critical", "as soon as possible"},
            "medium": {"important", "priority", "soon"},
            "low": {"later", "whenever", "at your convenience"},
        }

        words = set(re.findall(r'\b\w+\b', text.lower()))  # Extract words more reliably
        scores = {level: sum(1 for word in words if word in keywords) for level, keywords in urgency_levels.items()}

        max_score = max(scores.values())
        if max_score == 0:
            return "low"  # Explicit default if no urgency words are found

        # Return the highest urgency level (if multiple levels have the same score, return the more urgent one)
        return max((level for level, score in scores.items() if score == max_score), key=lambda x: ["low", "medium", "high"].index(x))

    def extract_audio_features(self, audio_path):
        """
        Extract audio features using librosa.
        """
        y, sr = librosa.load(audio_path, sr=None)

        return {
            "duration_seconds": librosa.get_duration(y=y, sr=sr),
            "sample_rate": sr,
            "rms_energy": librosa.feature.rms(y=y).mean(),
            "zero_crossing_rate": librosa.feature.zero_crossing_rate(y=y).mean(),
            "mfccs_mean": librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1).tolist(),
        }

    def extract_name(self, text):
        """
        Extract a name from the transcription, if mentioned.
        """
        patterns = [
            r"\b(?:my\s*name\s*is|i\'m|im)\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b",
            r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*speaking\b",
            r"\b(?:this\s*is)\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b",
        ]
        names = {ent.text for ent in self.nlp(text).ents if ent.label_ == "PERSON"}
        for pattern in patterns:
            names.update(match.group(1).capitalize() for match in re.finditer(pattern, text, re.IGNORECASE))
        return list(names)

    

    def extract_purpose(self, text):
        """
        Extract the type of claim mentioned in the call transcription using spaCy dependency parsing and KeyBERT.
        """
        doc = self.nlp(text)

        # Predefined common claim types
        claim_types = {
            "death claim": ["death claim", "life insurance claim", "funeral claim"],
            "health claim": ["medical claim", "health claim", "hospital bill claim"],
            "auto claim": ["car insurance claim", "vehicle damage claim", "auto claim"],
            "property claim": ["home insurance claim", "fire damage claim", "property claim"],
            "disability claim": ["disability claim", "long-term disability claim"],
            "accident claim": ["accident claim", "injury claim", "workplace injury claim"],
        }

        # Extract phrases using dependency parsing
        extracted_phrases = set()
        for token in doc:
            if token.text.lower() == "claim" and token.head:
                phrase = f"{token.head.text.lower()} claim"
                extracted_phrases.add(phrase)

        # Use KeyBERT for additional keyword extraction
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=3)
        extracted_phrases.update([kw[0].lower() for kw in keywords])

        # Match extracted phrases to known claim types
        detected_claim_type = None
        for claim_category, keywords in claim_types.items():
            if any(phrase in extracted_phrases for phrase in keywords):
                detected_claim_type = claim_category
                break  # Stop at the first match

        return detected_claim_type if detected_claim_type else "general inquiry"


    def extract_claim_id(self, text):
        """
        Extract a claim ID if mentioned in the transcription.
        """
        patterns = [
            r"\b(?:claim\s*(?:id|number|#)\s*is\s*(\d+))\b",
            r"\b(?:claim\s*(?:id|number|#)\s*(\d+))\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def analyze_language_proficiency(self, text):
        if not text.strip():
            return "Unknown"
        words = text.split()
        if not words:
            return "Unknown"

        blob = TextBlob(text)
        avg_word_length = np.mean([len(word) for word in words])
        lexical_diversity = len(set(w.lower() for w in words)) / len(words)
        try:
            grammar_accuracy = 1 - (len(set(text) - set(str(blob.correct()))) / len(text))
        except:
            grammar_accuracy = 0.5

        score = avg_word_length * 0.2 + lexical_diversity * 0.4 + grammar_accuracy * 0.4
        return "Advanced" if score > 0.8 else "Intermediate" if score > 0.6 else "Basic" if score > 0.4 else "Beginner"
