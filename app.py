from fastapi import FastAPI
from pydantic import BaseModel
from model import predict_food
from nutrition_utils import get_nutrition, calculate_risk
import base64
from PIL import Image
import io

app = FastAPI()

class FoodRequest(BaseModel):
    food: str | None = None
    image: str | None = None


@app.post("/analyze-food")
def analyze_food(request: FoodRequest):

    # Case 1: user typed food
    if request.food:
        food = request.food

    # Case 2: image uploaded
    elif request.image:

        # image_bytes = base64.b64decode(request.image)
        image_data = request.image

        if "," in image_data:
            image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        food = predict_food(image)
        food = food.replace("_", " ")
        print("Predicted food:", food)

    else:
        return {"error": "No food input provided"}

    nutrition = get_nutrition(food)

    if nutrition is None:
        return {"error": "Food not found"}

    risk, reasons = calculate_risk(nutrition)

    return {
        "food_detected": food,
        "nutrition": {
            "calories": round(nutrition["Caloric Value"],2),
            "fat": round(nutrition["Fat"],2),
            "saturated_fat": round(nutrition["Saturated Fats"],2),
            "sugar": round(nutrition["Sugars"],2),
            "sodium": round(nutrition["Sodium"]*1000,2)
        },
        "heart_health_risk": risk,
        "reasons": reasons
    }