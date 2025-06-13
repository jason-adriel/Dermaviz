from PIL import Image
from io import BytesIO
import pandas as pd
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn
import io
import matplotlib.pyplot as plt
import pickle
from transformers import AutoImageProcessor, AutoModel
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from tqdm import tqdm

id2label = {
 0: 'Eczema',
 1: 'Urticaria',
 2: 'Folliculitis',
 3: 'Psoriasis',
 4: 'Tinea',
 5: 'Acne',
 6: 'Tinea Versicolor',
 7: 'Stasis Dermatitis',
 8: 'Verruca vulgaris',
 9: 'Scar Condition',
 10: 'Seborrheic Dermatitis',
 11: 'Actinic Keratosis',
 12: 'SCC/SCCIS',
 13: 'SK/ISK',
 14: 'Basal Cell Carcinoma',
 15: 'Melanocytic Nevus',
 16: 'Hidradenitis',
 17: 'Cyst',
 18: 'Vitiligo',
 19: 'Melanoma'
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
loadedModel = None
loadedScaler = None
loadedPCA = None
imageProcessor = None

def load_preprocessor():
    global loadedScaler
    global loadedPCA
    with open("scaler.pkl", "rb") as f:
        loadedScaler = pickle.load(f)

    with open("pca.pkl", "rb") as f:
        loadedPCA = pickle.load(f)

def load_model():
    model = CNNForLDL(20, 23)
    model.load_state_dict(torch.load('./model_resnet50_gated_randaug.pth', map_location=device))
    model.to(device)
    model.eval()
    global loadedModel
    global imageProcessor

    loadedModel = model
    imageProcessor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")

def convert_image_blob_to_pil(img_blob: bytes) -> Image.Image:
    return Image.open(BytesIO(img_blob)).convert("RGB")

def flatten_onehot_jsonb_fields(detail):
    onehot = {}

    all_possible_values = {
        "textures": [
            "raised_or_bumpy",
            "flat",
            "rough_or_flaky",
            "fluid_filled"
        ],
        "body_parts": [
            "head_or_neck",
            "arm",
            "palm",
            "back_of_hand",
            "torso_front",
            "torso_back",
            "genitalia_or_groin",
            "buttocks",
            "leg",
            "foot_top_or_side",
            "foot_sole",
            "other"
        ],
        "condition_symptoms": [
            "bothersome_appearance",
            "bleeding",
            "increasing_size",
            "darkening",
            "itching",
            "burning",
            "pain"
        ]
    }

    for field_attr, prefix in [
        ("textures", "textures_"),
        ("body_parts", "body_parts_"),
        ("condition_symptoms", "condition_symptoms_")
    ]:
        field_value = getattr(detail, field_attr) or []
        if not isinstance(field_value, list):
            continue

        active_set = {item.lower() for item in field_value}

        for option in all_possible_values[field_attr]:
            key = f"{prefix}{option}"
            onehot[key] = "YES" if option in active_set else "NO"

    return onehot

def process_dataframe_pipeline(df_raw: pd.DataFrame):

    if (loadedPCA is None or loadedScaler is None):
        load_preprocessor()

    if (loadedPCA is None or loadedScaler is None):
        raise RuntimeError("Preprocessor failed to load.")
    
    TABULAR_DATA_COLUMNS = [
    'age_group',
    'sex_at_birth',
    'textures_raised_or_bumpy',
    'textures_flat',
    'textures_rough_or_flaky',
    'textures_fluid_filled',
    'body_parts_head_or_neck',
    'body_parts_arm',
    'body_parts_palm',
    'body_parts_back_of_hand',
    'body_parts_torso_front',
    'body_parts_torso_back',
    'body_parts_genitalia_or_groin',
    'body_parts_buttocks',
    'body_parts_leg',
    'body_parts_foot_top_or_side',
    'body_parts_foot_sole',
    'body_parts_other',
    'condition_symptoms_bothersome_appearance',
    'condition_symptoms_bleeding',
    'condition_symptoms_increasing_size',
    'condition_symptoms_darkening',
    'condition_symptoms_itching',
    'condition_symptoms_burning',
    'condition_symptoms_pain',
    'condition_duration'
]

    one_hot_encoded_columns = [
        'textures_raised_or_bumpy',
        'textures_flat',
        'textures_rough_or_flaky',
        'textures_fluid_filled',
        'body_parts_head_or_neck',
        'body_parts_arm',
        'body_parts_palm',
        'body_parts_back_of_hand',
        'body_parts_torso_front',
        'body_parts_torso_back',
        'body_parts_genitalia_or_groin',
        'body_parts_buttocks',
        'body_parts_leg',
        'body_parts_foot_top_or_side',
        'body_parts_foot_sole',
        'body_parts_other',
        'condition_symptoms_bothersome_appearance',
        'condition_symptoms_bleeding',
        'condition_symptoms_increasing_size',
        'condition_symptoms_darkening',
        'condition_symptoms_itching',
        'condition_symptoms_burning',
        'condition_symptoms_pain',
    ]

    label_encoded_columns = [
        'age_group',
        'sex_at_birth',
        'condition_duration'
    ]

    df = df_raw.copy()

    df['condition_duration'] = df['condition_duration'].fillna('UNKNOWN')

    for col in one_hot_encoded_columns:
        df[col] = df[col].apply(lambda x: 1 if x == 'YES' else 0)

    for col in label_encoded_columns:
        le = preprocessing.LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # Standardize + PCA
    X_scaled = loadedScaler.transform(df[TABULAR_DATA_COLUMNS])

    X_pca = loadedPCA.transform(X_scaled)

    return X_pca  # shape (n_samples, n_features)

def run_model(df: pd.DataFrame, image):

    if loadedModel is None or imageProcessor is None:
        load_model()
    
    if loadedModel is None or imageProcessor is None:
        raise RuntimeError("Model or processor failed to load.")

    X_pca = process_dataframe_pipeline(df)
    inputs = imageProcessor(images=image, return_tensors="pt")
    inputs = {k: v.squeeze(0).to(device) for k, v in inputs.items()}
    tabular_tensor = torch.tensor(X_pca, dtype=torch.float32).to(device)
    loadedModel.eval()

    with torch.no_grad():
        log_probs = loadedModel(pixel_values=inputs["pixel_values"], tabular_features=tabular_tensor)
        probs = log_probs.exp().cpu().squeeze().numpy()
        image_bytes = generate_result_image(image, probs, [id2label[i] for i in range(len(probs))])

    return probs, image_bytes



def generate_result_image(input_img: Image.Image, probs: list[float], labels: list[str]) -> bytes:
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    axs[0].imshow(input_img)
    axs[0].axis('off')
    axs[0].set_title("Input Image")

    axs[1].barh(labels, probs)
    axs[1].set_xlim(0, 1)
    axs[1].set_title("Predicted Probabilities")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf.read()



# ========== Tabular Encoder ==========
class TabularEncoder(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.LayerNorm(256),

            nn.Linear(256, 512),
            nn.ReLU(),
            nn.LayerNorm(512),

            nn.Linear(512, output_dim),
            nn.ReLU(),
            nn.LayerNorm(output_dim)
        )

    def forward(self, x):
        return self.encoder(x)

# ======== Focal Loss ===========
class FocalKLLoss(nn.Module):
    def __init__(self, gamma: float = 2.0, eps: float = 1e-8, reduction="mean"):
        """
        gamma: focusing parameter — higher means more focus on “hard” (low-p) classes
        eps: numerical stability
        reduction: "mean" or "sum"
        """
        super().__init__()
        self.gamma = gamma
        self.eps = eps
        self.reduction = reduction

    def forward(self, log_p: torch.Tensor, q: torch.Tensor):
        """
        log_p:   Tensor of shape (B, C), log-probabilities from model
        q:       Tensor of shape (B, C), raw label distributions (will be renormalized)
        """
        # normalize targets
        q = q / (q.sum(dim=1, keepdim=True) + self.eps)
        # convert log-p to p
        p = log_p.exp()
        # compute element-wise KL
        kl_el = q * (torch.log(q + self.eps) - log_p)
        # focal weights
        weights = (1.0 - p).pow(self.gamma)
        # apply weights
        loss_el = weights * kl_el
        # sum over classes
        loss_per_sample = loss_el.sum(dim=1)
        # reduction
        if self.reduction == "mean":
            return loss_per_sample.mean()
        else:
            return loss_per_sample.sum()

# ========== Model ==========
class CNNForLDL(nn.Module):
    def __init__(self, num_labels, tabular_input_dim):
        super().__init__()
        self.backbone = AutoModel.from_pretrained("microsoft/resnet-50")
        self.hidden_size = self.backbone.config.hidden_sizes[-1] if hasattr(self.backbone.config, 'hidden_sizes') else self.backbone.config.hidden_size
        self.tabular_encoder = TabularEncoder(tabular_input_dim, self.hidden_size)
        self.dropout = nn.Dropout(0.2)
        self.classifier = nn.Linear(self.hidden_size, num_labels)
        self.gate_layer = nn.Linear(self.hidden_size * 2, self.hidden_size)
        self.alpha = nn.Parameter(torch.tensor(1.0))

    def forward(self, pixel_values, tabular_features):
        features = self.backbone(pixel_values=pixel_values).last_hidden_state
        if features.ndim == 4:
            features = features.mean(dim=[2, 3])
        elif features.ndim == 3:
            features = features.mean(dim=1)

        tabular_embedding = self.tabular_encoder(tabular_features)

        image_h = torch.tanh(features)           # after mean pooling from ResNet
        tabular_h = torch.tanh(tabular_embedding)


        gate = torch.sigmoid(self.gate_layer(torch.cat([image_h, tabular_h], dim=1)))
        fused = gate * image_h + (1 - gate) * tabular_h

        logits = self.classifier(self.dropout(fused))
        log_probs = torch.log_softmax(logits, dim=-1)

        return log_probs
