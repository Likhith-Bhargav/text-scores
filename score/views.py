# views.py
from django.http import JsonResponse
from .education_model import EducationModel
from .toxicity_model import ToxicityModel
from django.shortcuts import render
from .forms import ScoreInputForm
import logging

# Initialize models once (to avoid reloading them for every request)
education_model = EducationModel()
toxicity_model = ToxicityModel()

# Initialize logging
logger = logging.getLogger(__name__)

def home(request):
    if request.method == 'POST':
        form = ScoreInputForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['text']

            # Get scores from models
            edu_score = education_model.get_score(input_text)['score']
            toxicity_result = toxicity_model.get_score(input_text)

            neutral_score = toxicity_result['neutral_score']
            toxic_score = toxicity_result['toxic_score']

            # Prepare the response
            response = {
                "score using education model": edu_score,
                "score using toxicity model for normal": neutral_score,
                "score using toxicity model for toxic": toxic_score,
            }

            return JsonResponse(response)

    else:
        form = ScoreInputForm()

    return render(request, 'home.html', {'form': form})

def calculate_score(request):
    if request.method == "POST":
        input_text = request.POST.get("input_text", "")
        if not input_text:
            return JsonResponse({"error": "No text provided"}, status=400)

        try:
            # Get scores from both models
            education_result = education_model.get_score(input_text)
            toxicity_result = toxicity_model.get_score(input_text)

            # Convert scores to JSON-serializable format
            result = {
                "score": float(education_result.get("int_score", 0)),
                "education_raw_score": float(education_result.get("score", 0.0)),
                "toxicity": toxicity_result.get("classification", ""),
                "toxicity_scores": {
                    "neutral": float(toxicity_result.get("neutral_score", 0.0)),
                    "toxic": float(toxicity_result.get("toxic_score", 0.0)),
                },
            }

            logger.info(f"Result: {result}")
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Error calculating scores: {str(e)}")
            return JsonResponse({"error": f"Error calculating scores: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
