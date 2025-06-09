
import requests
import json
import re

FOOD_CARB_MAP = {
    "ham sandwich": 30,
    "pizza": 30,
    "orange juice": 25,
    "cereal": 40,
    "toast": 15,
    "banana": 27,
    "apple": 20,
}

def estimate_carbs(food_text: str):
    """Return approximate carbs from a local lookup table; None if unknown."""
    text = food_text.lower()
    for key, val in FOOD_CARB_MAP.items():
        if key in text:
            return val
    return None

def get_carbs_from_food(food_name: str):
    """
    Query USDA FoodData Central for carbohydrate grams of the first matching item.
    Requires an API key — replace the placeholder below.
    Returns None on failure or if not found.
    """
    api_key = "4jjjO5TbwSjNlUaywuqhxfhuSuOsaQv9oOZ7dj9S"  
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    try:
        r = requests.get(
            search_url,
            params={
                "query": food_name,
                "api_key": api_key,
                "pageSize": 1,
            },
            timeout=5,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        items = data.get("foods", [])
        if not items:
            return None
        for nutrient in items[0].get("foodNutrients", []):
            if nutrient.get("nutrientName") == "Carbohydrate, by difference":
                return nutrient.get("value")
    except Exception:
        pass
    return None
    
# --------------------------------------------------------------------------

def query_mistral(transcript):
    url = 'http://localhost:11434/api/generate'
    prompt = f"""
    Extract structured data from the sentence below. Clearly follow these rules:

    - ONLY fill in "carbs" if the sentence explicitly mentions carbs OR describes food. Estimate carbs accurately for described foods. If there's no explicit mention of food or carbs, set "carbs" to null.

    - ONLY fill in "activity" and "duration" if physical exercise (e.g., run, walk, bike) and duration/time are explicitly mentioned. If exercise is not clearly mentioned, set both "activity" and "duration" to null.

    - NEVER assume default values. Be precise and conservative.

    Examples:
    Sentence: 'I ate 30 grams of carbs'
    Response: {{"carbs": 30, "activity": null, "duration": null}}

    Sentence: 'I ran for 20 minutes'
    Response: {{"carbs": null, "activity": "run", "duration": 20}}

    Sentence: 'I had a ham sandwich'
    Response: {{"carbs": 30, "activity": null, "duration": null}}

    Now, the actual sentence to parse:
    '{transcript}'

    Respond strictly in JSON format as shown in examples above.
    """
    
    response = requests.post(url, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    
    text = response.json()["response"]

    # Try to find JSON inside the response
    try:
        json_match = re.search(r'{.*}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            # ------------------------------------------------------------------
            # If the model didn't supply carbs but a food appears present,
            # try local estimate first, then USDA lookup.
            if result.get("carbs") is None:
                est = estimate_carbs(transcript)
                if est is not None:
                    result["carbs"] = est
                else:
                    api_est = get_carbs_from_food(transcript)
                    if api_est is not None:
                        result["carbs"] = api_est
            # ------------------------------------------------------------------
            return result
        else:
            print("⚠️ The model couldn't find a valid input.")
            print("Response was:", text)
            return {}
    except Exception as e:
        print("⚠️ Error parsing JSON:", e)
        print("Response was:", text)
        return {}
