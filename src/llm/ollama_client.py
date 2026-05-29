import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llama3"


def generate_response(
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1200
) -> str:

    payload = {

        "model": MODEL_NAME,

        "prompt": prompt,

        "stream": False,

        "options": {

            "temperature": temperature,

            "num_predict": max_tokens
        }
    }

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        generated_text = data.get(
            "response",
            ""
        )

        return generated_text.strip()

    except requests.exceptions.Timeout:

        return (
            "ERROR: Ollama request timed out."
        )

    except requests.exceptions.ConnectionError:

        return (
            "ERROR: Could not connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.HTTPError as e:

        return (
            f"ERROR: Ollama HTTP error: {e}"
        )

    except Exception as e:

        return (
            f"ERROR: Unexpected Ollama failure: {e}"
        )
    

# # test
# if __name__ == "__main__":

#     test_prompt = """

# You are a zoning assistant.

# Question:
# What is FAR?

# Answer briefly.
# """

#     response = generate_response(
#         prompt=test_prompt
#     )

#     print("\n=== MODEL RESPONSE ===\n")

#     print(response)