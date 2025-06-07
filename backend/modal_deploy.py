import modal

# Use a more recent version of PyTorch that supports Python 3.12
image = modal.Image.debian_slim().pip_install(
    "transformers>=4.41.0",
    "torch>=2.2.0",  # Updated to a version available for Python 3.12
    "accelerate>=0.29.2",
    "sentencepiece>=0.2.0",
    "auto-gptq>=0.7.0"  # Added for better GGUF model support
)

app = modal.App("nexahealth-mistral", image=image)

LANGUAGE_PROMPTS = {
    "yoruba": "E jẹ́ AI itọju ilera fún Ariwa ati Guusu Ila-oorun Afirka. Dahun ni èdè Yorùbá.",
    "igbo": "Bụ AI ahụike maka Ndịda Ọwụwa Anyanwụ Africa. Zaa n'asụsụ Igbo.",
    "hausa": "Ke ne AI na kula da lafiya ga Arewacin Afirka. Amsa cikin Hausa.",
    "swahili": "Wewe ni AI ya afya kwa Afrika Mashariki na Kati. Jibu kwa Kiswahili.",
    "pidgin": "You be health AI for Nigeria. Answer in simple Nigerian Pidgin.",
    "english": "You are a medical AI for Africa. Respond in clear, simple English."
}


@app.function(
    gpu="A10G",
    timeout=300,
    min_containers=1
)
def generate_response(question: str, language: str = "english"):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Load model (this will cache after first run)
    model = AutoModelForCausalLM.from_pretrained(
        "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
        model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

    lang_prompt = LANGUAGE_PROMPTS.get(language.lower(), LANGUAGE_PROMPTS["english"])

    prompt = f"""<s>[INST] {lang_prompt}
    Provide accurate health information in 2-3 sentences.
    Question: {question} [/INST]"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.7,
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).replace(prompt, "")


@app.local_entrypoint()
def main(question: str, language: str = "english"):
    result = generate_response.remote(question, language)
    print(result)