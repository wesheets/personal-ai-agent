# app/core/openai_provider.py

import os
import openai

class OpenAIProvider:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"

    def run(self, prompt, agent_id="core.forge"):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    { "role": "system", "content": f"You are {agent_id}. Respond concisely and insightfully." },
                    { "role": "user", "content": prompt }
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
