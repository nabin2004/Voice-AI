# Welcome to Voice AI

<!-- For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files. -->


Here’s a concise and structured **documentation** for your FastAPI-based Nepali speech correction service:

---

# 📘 Nepali Voice AI API – Documentation

This application provides a FastAPI-based interface for **Nepali speech-to-text transcription** and **GPT-2 powered spell correction**. It integrates an ASR model, a GPT-2 model, and a Trie-based spell checker.

---

## 📦 Main Components

### 1. **ASR (Automatic Speech Recognition)**

* Uses a pretrained [NeMo](https://github.com/NVIDIA/NeMo) ASR model for Nepali (`.nemo` file).
* Transcribes `.wav` audio to text.

### 2. **Trie Spell Checker**

* A pickled custom Trie data structure is used to:

  * Check if a word is spelled correctly.
  * Suggest likely completions for a prefix.

### 3. **GPT-2 Language Model**

* A fine-tuned Nepali GPT-2 model is used to rank suggestions based on sentence context.
* Helps pick the most plausible word from the suggestions.

---

## 🚀 API Endpoints

### `POST /transcribe/`

**Transcribe Nepali audio and auto-correct spelling.**

**Request:**

* `file`: `.wav` audio file (can be stereo; internally converted to mono)

**Response:**

```json
{
  "transcription": "corrected sentence"
}
```

---

### `POST /spellcheck/`

**Check if a list of words are spelled correctly.**

**Request:**

```json
{
  "words": ["नेपाल", "वाइज्याकमा"]
}
```

**Response:**

```json
{
  "results": {
    "नेपाल": true,
    "वाइज्याकमा": true
  }
}
```

---

### `POST /suggest/`

**Suggest words based on prefix using Trie.**

**Request:**

```json
{
  "word": "का",
  "max_suggestions": 5
}
```

**Response:**

```json
{
  "suggestions": ["काठमाडौँ", "कार्यालय", "कारण", ...]
}
```

---

### `POST /correct/`

**Correct a manually entered Nepali sentence using GPT-2 ranking.**

**Request:**

```json
{
  "sentence": "काठमाण्डौ एक ठुलो शहर हो"
}
```

**Response:**

```json
{
  "corrected": "काठमाडौँ एक ठुलो शहर हो"
}
```

---

## 🧠 How Spell Correction Works

1. Each token is checked in the Trie.
2. If misspelled:

   * Top suggestions are generated based on prefix.
   * GPT-2 ranks each suggestion in context.
3. The highest-scoring suggestion replaces the word.

---
