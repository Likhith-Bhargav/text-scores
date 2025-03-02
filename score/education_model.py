import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

class EducationModel:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")

        try:
            # Attempt to load the model with PyTorch weights
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "HuggingFaceTB/fineweb-edu-classifier",
                from_tf=True  # Load TensorFlow weights if no PyTorch weights
            )
            logger.info("Model loaded successfully with PyTorch weights.")
        except Exception as e:
            # If the PyTorch model loading fails, log the error and attempt to load with TensorFlow weights
            logger.error(f"Error loading model with PyTorch weights: {e}")
            try:
                logger.info("Attempting to load model with TensorFlow weights.")
                self.model = AutoModelForSequenceClassification.from_pretrained("HuggingFaceTB/fineweb-edu-classifier")
                logger.info("Model loaded successfully with TensorFlow weights.")
            except Exception as e:
                logger.error(f"Error loading model with TensorFlow weights: {e}")
                raise  # Re-raise exception if both loading attempts fail

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
