import argparse

def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_unique_vocab(text):
    words = text.split() 
    # unique_words = sorted(set(words))
    unique_words = set(words)
    return unique_words

def save_vocab(words, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for word in words:
            f.write(word + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract unique Nepali vocab from corpus (no tokenization).")
    parser.add_argument("corpus", type=str, help="Path to the input text corpus file")
    parser.add_argument("output", type=str, help="Path to the output vocab file")
    args = parser.parse_args()

    text = load_corpus(args.corpus)
    vocab = extract_unique_vocab(text)
    # print(vocab[:200])
    save_vocab(vocab, args.output)
    print(f"✅ Saved {len(vocab)} unique words to {args.output}")
