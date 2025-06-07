import modal

app = modal.App("nexahealth-mistral")

# Language-specific instructions
LANGUAGE_PROMPTS = {
    "yoruba": "E jẹ́ AI itọju ilera fún Ariwa ati Guusu Ila-oorun Afirka. Dahun ni èdè Yorùbá.",
    "igbo": "Bụ AI ahụike maka Ndịda Ọwụwa Anyanwụ Africa. Zaa n'asụsụ Igbo.",
    "hausa": "Ke ne AI na kula da lafiya ga Arewacin Afirka. Amsa cikin Hausa.",
    "swahili": "Wewe ni AI ya afya kwa Afrika Mashariki na Kati. Jibu kwa Kiswahili.",
    "english": "You are a medical AI for Africa. Respond in clear, simple English."
}


@app.function(
    gpu="A10G",
    timeout=300,
    min_containers=1  # Changed from keep_warm to min_containers
)
def run_mistral(question: str, language: str = "english"):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(
        "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
        model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

    lang_prompt = LANGUAGE_PROMPTS.get(language.lower(), LANGUAGE_PROMPTS["english"])

    prompt = f"""<s>[INST] {lang_prompt}
    Provide accurate, culturally appropriate health information.
    Answer in 2-3 short sentences maximum.

    Question: {question} [/INST]"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.7,
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).replace(prompt, "")


# New way to expose web endpoints in Modal
@app.local_entrypoint()
def main(question: str, language: str = "english"):
    language = language.lower()
    if language not in LANGUAGE_PROMPTS:
        language = "english"
    result = run_mistral.remote(question, language)
    print(result)