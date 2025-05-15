import gradio as gr
import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def transcribe_audio(audio):
    if audio is None:
        return "❌ No audio provided."
    try:
        if not os.path.exists(audio):
            return "❌ Audio file not found."

        with open(audio, "rb") as audio_file:
            response = requests.post(f"{BASE_URL}/transcribe/", files={"file": audio_file})

        if response.status_code == 200:
            return response.json().get("transcription", "❌ No transcription returned.")
        else:
            return f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

with gr.Blocks(title="Nepali Speech to Text") as demo:
    gr.Markdown("## 🎙️ Nepali Speech-to-Text Interface")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Record Audio")
            record_audio = gr.Audio(type="filepath", sources=["microphone"], label="Record Audio")

            gr.Markdown("### Upload Audio")
            upload_audio = gr.Audio(type="filepath", sources=["upload"], label="Upload Audio")

            submit_btn = gr.Button("SUBMIT", size="lg", variant="primary")
            clear_btn = gr.Button("CLEAR", size="lg", variant="secondary")

        with gr.Column(scale=1):
            gr.Markdown("### 📝 Output")
            output_text = gr.Textbox(lines=20, label="Transcription", placeholder="Output will appear here...")

    def process(audio1, audio2):
        return transcribe_audio(audio1 or audio2)

    submit_btn.click(fn=process, inputs=[upload_audio, record_audio], outputs=output_text)
    clear_btn.click(lambda: (None, None, ""), inputs=[], outputs=[upload_audio, record_audio, output_text])

demo.launch(share=True)
