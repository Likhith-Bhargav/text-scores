# models/education_model.py
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Initialize logging
logger = logging.getLogger(__name__)

class EducationModel:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")
        self.model = AutoModelForSequenceClassification.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")

    def get_score(self, text):
        try:
            # Tokenize input text
            inputs = self.tokenizer(text, return_tensors="pt", padding="longest", truncation=True)
            # Get model outputs
            outputs = self.model(**inputs)
            # Extract logits and compute the score
            logits = outputs.logits.squeeze(-1).float().detach().numpy()
            score = logits.item()

            # Construct the result
            return {
                "text": text,
                "score": score,
                "int_score": int(round(max(0, min(score, 5)))),  # Ensure score is within [0, 5]
            }
        except Exception as e:
            logger.error(f"Error in EducationModel.get_score: {e}")
            raise
