import os

from dotenv import load_dotenv
from flask import Flask, render_template, request
from google import genai


load_dotenv()

app = Flask(__name__)

cuisines = [
    "",
    "Italian",
    "Mexican",
    "Chinese",
    "Indian",
    "Japanese",
    "Thai",
    "French",
    "Mediterranean",
    "American",
    "Greek",
]

dietary_restrictions = [
    "Gluten-Free",
    "Dairy-Free",
    "Vegan",
    "Pescatarian",
    "Nut-Free",
    "Kosher",
    "Halal",
    "Low-Carb",
    "Organic",
    "Locally Sourced",
]

languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Japanese": "ja",
    "Korean": "ko",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Dutch": "nl",
    "Swedish": "sv",
    "Turkish": "tr",
    "Greek": "el",
    "Hebrew": "he",
    "Hindi": "hi",
    "Indonesian": "id",
    "Thai": "th",
    "Filipino": "tl",
    "Vietnamese": "vi",
}

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


@app.route("/")
def index():
    return render_template(
        "index.html",
        cuisines=cuisines,
        dietary_restrictions=dietary_restrictions,
        languages=languages,
    )


@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    ingredients = request.form.getlist("ingredient")
    ingredients = [ingredient.strip() for ingredient in ingredients if ingredient.strip()]
    selected_cuisine = request.form.get("cuisine")
    selected_restrictions = request.form.getlist("restrictions")
    selected_language = request.form.get("language")

    if len(ingredients) != 3:
        return render_template(
            "recipe.html",
            recipe="<p>Kindly provide exactly 3 ingredients.</p>",
        )

    if client is None:
        return render_template(
            "recipe.html",
            recipe="<p>GEMINI_API_KEY가 .env 파일에 설정되어 있지 않습니다.</p>",
        )

    prompt = f"""
    Craft a recipe in HTML using {', '.join(ingredients)}.
    Ensure the recipe ingredients appear at the top,
    followed by the step-by-step instructions.
    Use only simple HTML tags such as h2, h3, p, ul, ol, li, and strong.
    Do not include markdown code fences.
    """

    if selected_language:
        prompt += f"\nWrite the recipe in {selected_language}."
    else:
        prompt += "\nWrite the recipe in Korean."

    if selected_cuisine:
        prompt += f"\nThe cuisine should be {selected_cuisine}."

    if selected_restrictions:
        prompt += (
            "\nThe recipe should have the following restrictions: "
            f"{', '.join(selected_restrictions)}."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        recipe = response.text
    except Exception as e:
        recipe = f"<p>Error generating recipe: {str(e)}</p>"

    return render_template("recipe.html", recipe=recipe)


if __name__ == "__main__":
    app.run(debug=True)
