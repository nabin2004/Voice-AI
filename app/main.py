import pickle
import torch
import time
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from omegaconf import OmegaConf
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from fastapi.middleware.cors import CORSMiddleware
import nemo.collections.asr as nemo_asr
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from config import settings

# ------------------ Logging ------------------ #
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# ------------------ Paths ------------------ #
# PROJECT_ROOT = Path(__file__).resolve().parent
# TRIE_PICKLE_PATH = PROJECT_ROOT / "nepali_trie.pkl"
# ASR_MODEL_PATH = PROJECT_ROOT / "ASRmodel" / "indicconformer_stt_ne_hybrid_rnnt_large.nemo"
# GPT2_MODEL_PATH = PROJECT_ROOT / "GPT2"

ASR_MODEL_PATH = settings.asr_model_path
GPT2_MODEL_PATH = settings.gpt2_model_path
TRIE_PICKLE_PATH = settings.trie_pickle_path


# ------------------ Trie ------------------ #
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def is_word_spelled_correctly(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def suggest_words(self, prefix, max_suggestions=10):
        suggestions = []
        node = self.root
        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                return []

        def collect_words(node, current_word):
            if len(suggestions) >= max_suggestions:
                return
            if node.is_end_of_word:
                suggestions.append(current_word)
            for char, child in node.children.items():
                collect_words(child, current_word + char)

        collect_words(node, prefix)
        return suggestions

def load_trie(filename=TRIE_PICKLE_PATH):
    logger.info(f"Loading trie from {filename}...")
    class TrieUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            if name == "Trie":
                return Trie
            elif name == "TrieNode":
                return TrieNode
            return super().find_class(module, name)

    with open(filename, "rb") as f:
        trie = TrieUnpickler(f).load()
    return trie

trie = load_trie()
trie.insert("वाइज्याकमा")  # Optional example

# ------------------ FastAPI Setup ------------------ #
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# ------------------ Load Models ------------------ #
logger.info("Loading ASR model...")
asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.restore_from(str(ASR_MODEL_PATH))
asr_model.eval()
asr_model.to('cuda' if torch.cuda.is_available() else 'cpu')
asr_model.change_decoding_strategy(OmegaConf.create({"strategy": "greedy", "nbest": 5}))
asr_model.cur_decoder = "ctc"
logger.info("ASR model loaded.")

logger.info("Loading GPT-2 model...")
tokenizer = GPT2Tokenizer.from_pretrained(str(GPT2_MODEL_PATH))
gpt2_model = GPT2LMHeadModel.from_pretrained(str(GPT2_MODEL_PATH))
gpt2_model.eval()
gpt2_model.to('cuda' if torch.cuda.is_available() else 'cpu')
logger.info("GPT-2 loaded.")

# ------------------ GPT-2 Scoring ------------------ #
def score_with_gpt2(text):
    input_ids = tokenizer.encode(text, return_tensors='pt').to(gpt2_model.device)
    with torch.no_grad():
        output = gpt2_model(input_ids, labels=input_ids)
    return -output.loss.item()

def rank_with_gpt2(suggestions, context):
    if not suggestions:
        return ""
    best_word = suggestions[0]
    best_score = float("-inf")
    for word in suggestions:
        score = score_with_gpt2(' '.join(context + [word]))
        if score > best_score:
            best_score = score
            best_word = word
    return best_word

def correct_tokens(tokens):
    corrected_tokens = []
    for token in tokens:
        if trie.is_word_spelled_correctly(token):
            corrected_tokens.append(token)
        else:
            prefix = token[:2]
            suggestions = trie.suggest_words(prefix)
            best = rank_with_gpt2(suggestions, corrected_tokens)
            corrected_tokens.append(best)
    return ' '.join(corrected_tokens)

# ------------------ Pydantic Models ------------------ #
class TranscriptionResponse(BaseModel):
    transcription: str

class SpellCheckRequest(BaseModel):
    words: list[str]

class SpellCheckResponse(BaseModel):
    results: dict

class SuggestionRequest(BaseModel):
    word: str
    max_suggestions: int = 10

class SuggestionResponse(BaseModel):
    suggestions: list[str]

class CorrectionRequest(BaseModel):
    sentence: str

class CorrectionResponse(BaseModel):
    corrected: str

# ------------------ API Routes ------------------ #
@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    logger.info(f"Received audio: {file.filename}")
    audio_data = await file.read()

    with NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_data)
        tmp_path = tmp_file.name

    # Convert stereo to mono
    audio = AudioSegment.from_file(tmp_path)
    audio = audio.set_channels(1)
    audio.export(tmp_path, format="wav")

    output = asr_model.transcribe([tmp_path], language_id="ne")[0][0]
    tokens = output.split()
    corrected = correct_tokens(tokens)

    Path(tmp_path).unlink(missing_ok=True)
    return TranscriptionResponse(transcription=corrected)

@app.post("/spellcheck/", response_model=SpellCheckResponse)
async def spellcheck(request: SpellCheckRequest):
    results = {word: trie.is_word_spelled_correctly(word) for word in request.words}
    return SpellCheckResponse(results=results)

@app.post("/suggest/", response_model=SuggestionResponse)
async def suggest(request: SuggestionRequest):
    suggestions = trie.suggest_words(request.word, request.max_suggestions)
    return SuggestionResponse(suggestions=suggestions)

@app.post("/correct/", response_model=CorrectionResponse)
async def correct_text(request: CorrectionRequest):
    corrected = correct_tokens(request.sentence.strip().split())
    return CorrectionResponse(corrected=corrected)
