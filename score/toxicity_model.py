import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification

class ToxicityModel:
    def __init__(self):
        self.tokenizer = RobertaTokenizer.from_pretrained('s-nlp/roberta_toxicity_classifier')
        self.model = RobertaForSequenceClassification.from_pretrained('s-nlp/roberta_toxicity_classifier')

    def get_score(self, text: str) -> dict:
        inputs = self.tokenizer.encode(text, return_tensors="pt")
        
        outputs = self.model(inputs)
        logits = outputs.logits
        
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        neutral_score = probabilities[0][0].item()
        toxic_score = probabilities[0][1].item()
        
        classification = "toxic" if toxic_score > neutral_score else "neutral"
        
        return {
            "text": text,
            "neutral_score": neutral_score,
            "toxic_score": toxic_score,
            "classification": classification,
        }
