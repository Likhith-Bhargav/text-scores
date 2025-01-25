import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

class EducationModel:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")
        self.model = AutoModelForSequenceClassification.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")

    def get_score(self, text):
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding="longest", truncation=True)
            outputs = self.model(**inputs)
            logits = outputs.logits.squeeze(-1).float().detach().numpy()
            score = logits.item()

            return {
                "text": text,
                "score": score,
                "int_score": int(round(max(0, min(score, 5)))),  # Ensure score is within [0, 5]
            }
        except Exception as e:
            logger.error(f"Error in EducationModel.get_score: {e}")
            raise
