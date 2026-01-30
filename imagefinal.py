import torch
from torchvision import transforms, models
from PIL import Image

# ----------------- Device setup -----------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------- Load model checkpoint -----------------
checkpoint = torch.load("plant_disease_model.pth", map_location=device)

# Build model architecture (must match training)
model = models.resnet18(weights=None)
num_features = model.fc.in_features
model.fc = torch.nn.Linear(num_features, len(checkpoint['class_names']))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()
model = model.to(device)

# ----------------- Class names -----------------
class_names = checkpoint['class_names']

# ----------------- Disease -> Cure mapping -----------------
disease_cures = {
    "Corn (Maize) - Cercospora Leaf Spot":
        "Remove infected debris, rotate crops, and apply appropriate fungicides. Improve drainage.",
    "Corn (Maize) - Common Rust":
        "Plant resistant hybrids, maintain crop rotation, and use fungicides if infection is severe.",
    "Corn (Maize) - Healthy":
        "No disease detected. Maintain good crop hygiene and monitor regularly.",
    "Corn (Maize) - Northern Leaf Blight":
        "Use resistant varieties, remove residues, and apply fungicide sprays during high-risk periods.",

    "Grape - Black Rot":
        "Prune and remove mummified berries and infected tissue. Use protective fungicide sprays and improve canopy airflow.",
    "Grape - Esca (Black Measles)":
        "Remove heavily infected wood, practice good pruning sanitation, and follow preventive fungicide recommendations.",
    "Grape - Healthy":
        "No disease detected. Keep monitoring and maintain sanitation.",
    "Grape - Leaf Blight":
        "Prune infected leaves, remove fallen debris, and apply registered fungicides when needed.",

    "Peach - Bacterial Spot":
        "Copper sprays at appropriate timings, remove infected fruit/branches, and avoid overhead irrigation.",
    "Peach - Healthy":
        "No disease detected. Keep trees healthy and monitor regularly.",

    "Potato - Early Blight":
        "Remove debris, rotate crops, and use protectant fungicides as recommended.",
    "Potato - Healthy":
        "No disease detected. Keep fields clean and monitor for early signs.",
    "Potato - Late Blight":
        "Remove infected plants/tubers, apply recommended late-blight fungicides, and avoid excess moisture.",

    "Strawberry - Healthy":
        "No disease detected. Maintain good irrigation and sanitation practices.",
    "Strawberry - Leaf Scorch":
        "Remove affected leaves, improve spacing, and apply fungicide/bactericide per extension guidance.",

    "Tomato - Bacterial Spot":
        "Use copper-based bactericides, remove infected plants, practice crop rotation, and use certified disease-free seed.",
    "Tomato - Early Blight":
        "Remove infected debris, use fungicide sprays, and rotate crops.",
    "Tomato - Healthy":
        "No disease detected. Maintain normal care and monitor pests.",
    "Tomato - Late Blight":
        "Remove infected plants, apply fungicides promptly, and avoid overhead irrigation.",
    "Tomato - Septoria Leaf Spot":
        "Remove infected leaves/plant debris, apply fungicides, ensure good air circulation.",
    "Tomato - Yellow Leaf Curl Virus":
        "Remove infected plants, control whitefly vectors, and use resistant varieties.",

    "Apple - Apple Scab":
        "Rake and remove fallen leaves, apply protective fungicides, and plant resistant cultivars.",
    "Apple - Black Rot":
        "Prune cankers and mummified fruit, dispose of infected debris, and use fungicides.",
    "Apple - Cedar Apple Rust":
        "Remove nearby juniper hosts, prune infected tissue, and use timely fungicide sprays.",
    "Apple - Healthy":
        "No disease detected. Continue monitoring and good orchard hygiene.",

    "Bell Pepper - Bacterial Spot":
        "Use copper bactericides, remove infected plants/fruit, avoid overhead irrigation.",
    "Bell Pepper - Healthy":
        "No disease detected. Maintain good cultural practices.",

    "Cherry - Healthy":
        "No disease detected. Maintain monitoring and sanitation.",
    "Cherry - Powdery Mildew":
        "Improve airflow and reduce humidity, prune infected tissue, and apply sulfur or other fungicides."
}

# ----------------- Prediction function -----------------
def predict(image_input):
    """
    image_input: file path (str) OR file-like object (Flask FileStorage)
    Returns: dict {"disease": <str>, "cure": <str>}
    """
    # Open image
    try:
        img = Image.open(image_input).convert('RGB')
    except Exception as e:
        return {"disease": "Error: could not open image", "cure": str(e)}

    # Transform image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    img_t = transform(img).unsqueeze(0).to(device)

    # Model prediction
    with torch.no_grad():
        output = model(img_t)
        _, pred = torch.max(output, 1)

    disease = class_names[pred.item()]
    print("Predicted disease:", disease)  # Debug log

    # ---------- Normalize for matching ----------
    def normalize(name: str) -> str:
        return (
            name.lower()
            .replace("_", " ")
            .replace("-", " ")
            .replace("(", "")
            .replace(")", "")
            .replace("  ", " ")
            .strip()
        )

    disease_norm = normalize(disease)
    cure = None
    for k, v in disease_cures.items():
        if normalize(k) == disease_norm:
            cure = v
            break

    if cure is None:
        cure = "Cure information not available. Please consult a local agriculture extension officer."

    return {"disease": disease, "cure": cure}
