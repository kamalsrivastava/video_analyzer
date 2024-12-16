import openai

openai.api_key = 'key'

def summarize_text(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=100,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Error in summarization"
