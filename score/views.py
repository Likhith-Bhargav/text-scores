from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .education_model import EducationModel
from .toxicity_model import ToxicityModel
from .forms import ScoreInputForm
from .models import TextScore, TextCount
import logging


education_model = EducationModel()
toxicity_model = ToxicityModel()

logger = logging.getLogger(__name__)

def calculate_scores(input_text):

    try:
        edu_score = education_model.get_score(input_text)['score']
        toxicity_result = toxicity_model.get_score(input_text)
        neutral_score = toxicity_result['neutral_score']
        toxic_score = toxicity_result['toxic_score']

        toxicity_classification = "Normal" if neutral_score > toxic_score else "Toxic"

        return edu_score, neutral_score, toxic_score, toxicity_classification
    except Exception as e:
        logger.error(f"Error calculating scores: {str(e)}")
        raise e

def home(request):
    records = TextScore.objects.all().order_by('-id')
    paginator = Paginator(records, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ScoreInputForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['text']
            try:
                edu_score, neutral_score, toxic_score, toxicity_classification = calculate_scores(input_text)

                existing_entry = TextScore.objects.filter(entered_text=input_text).first()
                if existing_entry:
                    existing_entry.education_score = edu_score
                    existing_entry.toxicity_score_normal = neutral_score
                    existing_entry.toxicity_score_toxic = toxic_score
                    existing_entry.save()

                    text_count_entry, created = TextCount.objects.get_or_create(text=input_text)
                    text_count_entry.count = text_count_entry.count + 1 if not created else 2
                    text_count_entry.save()
                else:
                    TextScore.objects.create(
                        entered_text=input_text,
                        education_score=edu_score,
                        toxicity_score_normal=neutral_score,
                        toxicity_score_toxic=toxic_score,
                    )

                response = {
                    "score_using_education_model": edu_score,
                    "score_using_toxicity_model_for_normal": neutral_score,
                    "score_using_toxicity_model_for_toxic": toxic_score,
                    "toxicity_classification": toxicity_classification,
                }
                return JsonResponse(response)

            except Exception as e:
                logger.error(f"Error handling POST request: {str(e)}")
                return JsonResponse({"error": "An error occurred while processing the request."}, status=500)

    else:
        form = ScoreInputForm()

    return render(request, 'home.html', {'form': form, 'page_obj': page_obj})

@csrf_exempt
def calculate_score(request):

    if request.method == "POST":
        input_text = request.POST.get("input_text", "").strip()

        if not input_text:
            return JsonResponse({"error": "No text provided"}, status=400)

        try:
            edu_score, neutral_score, toxic_score, toxicity_classification = calculate_scores(input_text)

            existing_entry = TextScore.objects.filter(entered_text=input_text).first()
            if existing_entry:
                existing_entry.education_score = edu_score
                existing_entry.toxicity_score_normal = neutral_score
                existing_entry.toxicity_score_toxic = toxic_score
                existing_entry.save()

                text_count_entry, created = TextCount.objects.get_or_create(text=input_text)
                text_count_entry.count = text_count_entry.count + 1 if not created else 2
                text_count_entry.save()
            else:
                TextScore.objects.create(
                    entered_text=input_text,
                    education_score=edu_score,
                    toxicity_score_normal=neutral_score,
                    toxicity_score_toxic=toxic_score,
                )

            result = {
                "score": edu_score,
                "education_raw_score": edu_score,
                "toxicity": toxicity_classification,
                "toxicity_scores": {
                    "neutral": neutral_score,
                    "toxic": toxic_score,
                },
            }
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Error handling calculate_score request: {str(e)}")
            return JsonResponse({"error": "An error occurred while calculating scores."}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

from django.http import JsonResponse
from .models import TextScore
import logging

logger = logging.getLogger(__name__)

def get_all_scores(request):
    try:
        text_scores = TextScore.objects.all()

        data = []

        for record in text_scores:
            data.append({
                'entered_text': record.entered_text,
                'education_score': record.education_score,
                'neutral_score': record.toxicity_score_normal,
                'toxicity_score': record.toxicity_score_toxic,
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error in get_all_scores: {e}")
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
