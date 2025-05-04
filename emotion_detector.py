# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch.nn.functional as F

# # Load pretrained emotion model
# MODEL_NAME = "bhadresh-savani/distilbert-base-uncased-emotion"

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
# model.eval()  # set model to evaluation mode

# # All possible emotion labels for this model
# EMOTION_LABELS = [
#     "admiration", "amusement", "anger", "annoyance", "approval",
#     "caring", "confusion", "curiosity", "desire", "disappointment",
#     "disapproval", "disgust", "embarrassment", "excitement", "fear",
#     "gratitude", "grief", "joy", "love", "nervousness",
#     "optimism", "pride", "realization", "relief", "remorse",
#     "sadness", "surprise", "neutral"
# ]


# def detect_emotion(text: str, top_k: int = 1):
#     """
#     Detects the dominant emotion(s) in the given text.
#     """
#     inputs = tokenizer(text, return_tensors="pt", truncation=True)
#     with torch.no_grad():
#         outputs = model(**inputs)
#         probs = F.softmax(outputs.logits, dim=1).squeeze()

#     top_indices = torch.topk(probs, k=top_k).indices.tolist()
#     id2label = model.config.id2label
#     return [(id2label[i], round(probs[i].item(), 3)) for i in top_indices]


