# views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from .education_model import EducationModel
from .toxicity_model import ToxicityModel
from .forms import ScoreInputForm
from .models import TextScore, TextCount  # Import TextCount model
import logging

# Initialize models once (to avoid reloading them for every request)
education_model = EducationModel()
toxicity_model = ToxicityModel()

# Initialize logging
logger = logging.getLogger(__name__)

def home(request):
    # Fetch all records and paginate them
    records = TextScore.objects.all().order_by('-id')  # Order by most recent
    paginator = Paginator(records, 5)  # 5 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ScoreInputForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['text']

            try:
                # Check if the input already exists in the database
                existing_entry = TextScore.objects.filter(entered_text=input_text).first()

                # Calculate scores using the models
                edu_score = education_model.get_score(input_text)['score']
                toxicity_result = toxicity_model.get_score(input_text)
                neutral_score = toxicity_result['neutral_score']
                toxic_score = toxicity_result['toxic_score']

                # Determine toxicity classification
                toxicity_classification = "Normal" if neutral_score > toxic_score else "Toxic"

                if existing_entry:
                    # Update the existing entry in the TextScore table
                    existing_entry.education_score = edu_score
                    existing_entry.toxicity_score_normal = neutral_score
                    existing_entry.toxicity_score_toxic = toxic_score
                    existing_entry.save()

                    # Update or insert into the TextCount table
                    text_count_entry, created = TextCount.objects.get_or_create(text=input_text)
                    if created:
                        # First time entry in TextCount, set count to 2
                        text_count_entry.count = 2
                    else:
                        # Increment the count for subsequent entries
                        text_count_entry.count += 1
                    text_count_entry.save()

                else:
                    # Save the new entry in the TextScore table
                    TextScore.objects.create(
                        entered_text=input_text,
                        education_score=edu_score,
                        toxicity_score_normal=neutral_score,
                        toxicity_score_toxic=toxic_score,
                    )

                # Prepare and return the response
                response = {
                    "score using education model": edu_score,
                    "score using toxicity model for normal": neutral_score,
                    "score using toxicity model for toxic": toxic_score,
                    "toxicity_classification": toxicity_classification,
                }
                return JsonResponse(response)

            except Exception as e:
                logger.error(f"Error calculating scores: {str(e)}")
                return JsonResponse({"error": f"Error calculating scores: {str(e)}"}, status=500)

    else:
        form = ScoreInputForm()

    return render(request, 'home.html', {'form': form, 'page_obj': page_obj})


def calculate_score(request):
    if request.method == "POST":
        input_text = request.POST.get("input_text", "")
        if not input_text:
            return JsonResponse({"error": "No text provided"}, status=400)

        try:
            # Check if the input already exists in the database
            existing_entry = TextScore.objects.filter(entered_text=input_text).first()

            # Calculate scores using the models
            edu_score = education_model.get_score(input_text)['score']
            toxicity_result = toxicity_model.get_score(input_text)
            neutral_score = toxicity_result['neutral_score']
            toxic_score = toxicity_result['toxic_score']

            # Determine toxicity classification
            toxicity_classification = "Normal" if neutral_score > toxic_score else "Toxic"

            if existing_entry:
                # Update the existing entry in the TextScore table
                existing_entry.education_score = edu_score
                existing_entry.toxicity_score_normal = neutral_score
                existing_entry.toxicity_score_toxic = toxic_score
                existing_entry.save()

                # Update or insert into the TextCount table
                text_count_entry, created = TextCount.objects.get_or_create(text=input_text)
                if created:
                    # First time entry in TextCount, set count to 2
                    text_count_entry.count = 2
                else:
                    # Increment the count for subsequent entries
                    text_count_entry.count += 1
                text_count_entry.save()

            else:
                # Save the new entry in the TextScore table
                TextScore.objects.create(
                    entered_text=input_text,
                    education_score=edu_score,
                    toxicity_score_normal=neutral_score,
                    toxicity_score_toxic=toxic_score,
                )

            # Convert scores to JSON-serializable format
            result = {
                "score": edu_score,
                "education_raw_score": edu_score,
                "toxicity": toxicity_classification,
                "toxicity_scores": {
                    "neutral": neutral_score,
                    "toxic": toxic_score,
                },
            }

            logger.info(f"Result: {result}")
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Error calculating scores: {str(e)}")
            return JsonResponse({"error": f"Error calculating scores: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
