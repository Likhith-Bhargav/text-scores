# models/toxicity_model.py
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification

class ToxicityModel:
    def __init__(self):
        # Initialize the tokenizer and model
        self.tokenizer = RobertaTokenizer.from_pretrained('s-nlp/roberta_toxicity_classifier')
        self.model = RobertaForSequenceClassification.from_pretrained('s-nlp/roberta_toxicity_classifier')

    def get_score(self, text: str) -> dict:
        # Tokenize the input text
        inputs = self.tokenizer.encode(text, return_tensors="pt")
        
        # Get the model output (logits)
        outputs = self.model(inputs)
        logits = outputs.logits
        
        # Convert logits to probabilities using softmax
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        # Extract the probabilities for neutral and toxic
        neutral_score = probabilities[0][0].item()  # Neutral class probability (idx 0)
        toxic_score = probabilities[0][1].item()  # Toxic class probability (idx 1)
        
        # Determine the classification based on the probabilities
        classification = "toxic" if toxic_score > neutral_score else "neutral"
        
        return {
            "text": text,
            "neutral_score": neutral_score,
            "toxic_score": toxic_score,
            "classification": classification,
        }
