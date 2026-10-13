"""
Script de Entrenamiento de Lengua de Señas Peruana (LSP) para Google Colab
Entrena una red neuronal ligera Bi-GRU + Atención en menos de 10 minutos con GPU T4 gratuita.
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ==============================================================================
# 1. DATASET Y AUGMENTATION
# ==============================================================================
class LSPDataset(Dataset):
    def __init__(self, samples, labels, augment=False):
        self.samples = samples
        self.labels = labels
        self.augment = augment

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x = self.samples[idx].copy() # shape: (30, 126)
        y = self.labels[idx]

        if self.augment:
            # Inyección de jitter gaussiano sutil (simula variabilidad de mano)
            noise = np.random.normal(0, 0.015, x.shape).astype(np.float32)
            x = x + noise
            # Pequeña variación de escala
            scale = np.random.uniform(0.95, 1.05)
            x = x * scale

        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.long)

# ==============================================================================
# 2. ARQUITECTURA EFICIENTE (Bi-GRU + ATENCIÓN)
# ==============================================================================
class CompactLSPModel(nn.Module):
    def __init__(self, num_classes, input_dim=126, hidden_dim=128):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(input_dim, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        self.gru = nn.GRU(
            input_size=128,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.2
        )
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        # x: (batch, seq_len=30, 126)
        x = x.transpose(1, 2)
        x = self.conv(x)
        x = x.transpose(1, 2)
        
        gru_out, _ = self.gru(x) # (batch, seq_len, 256)
        attn_weights = F.softmax(self.attention(gru_out), dim=1) # (batch, seq_len, 1)
        context = torch.sum(attn_weights * gru_out, dim=1) # (batch, 256)
        logits = self.classifier(context)
        return logits

# ==============================================================================
# 3. PIPELINE DE ENTRENAMIENTO
# ==============================================================================
def train_model(dataset_path="lsp_dataset.npz", output_dir="models_lsp", epochs=60, batch_size=16, lr=1e-3):
    os.makedirs(output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Entrenando en: {device}")

    # Cargar datos
    data = np.load(dataset_path)
    X = data["samples"] # (N, 30, 126)
    y_raw = data["labels"]

    # Codificar etiquetas
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    classes = le.classes_.tolist()
    num_classes = len(classes)
    print(f"[*] Clases detectadas ({num_classes}): {classes}")
    print(f"[*] Total muestras: {len(X)}")

    # Split estratificado
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    train_ds = LSPDataset(X_train, y_train, augment=True)
    val_ds = LSPDataset(X_val, y_val, augment=False)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    model = CompactLSPModel(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=5)

    best_val_acc = 0.0
    best_epoch = 0

    print("\n[*] Iniciando bucle de entrenamiento...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        total_train = 0

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(batch_y)
            preds = logits.argmax(dim=-1)
            train_correct += (preds == batch_y).sum().item()
            total_train += len(batch_y)

        train_acc = train_correct / total_train

        # Validación
        model.eval()
        val_correct = 0
        total_val = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                logits = model(batch_x)
                preds = logits.argmax(dim=-1)
                val_correct += (preds == batch_y).sum().item()
                total_val += len(batch_y)

        val_acc = val_correct / total_val if total_val > 0 else 0.0
        scheduler.step(val_acc)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save(model.state_dict(), os.path.join(output_dir, "best_model.pth"))

        if epoch % 5 == 0 or epoch == epochs:
            print(f"Epoch [{epoch:02d}/{epochs:02d}] - Train Acc: {train_acc*100:.1f}% | Val Acc: {val_acc*100:.1f}% (Mejor: {best_val_acc*100:.1f}% en Ep #{best_epoch})")

    # Guardar codificador y configuración
    np.save(os.path.join(output_dir, "label_encoder_classes.npy"), le.classes_)
    config = {
        "num_classes": num_classes,
        "best_val_acc": float(best_val_acc),
        "best_epoch": int(best_epoch),
        "classes": classes
    }
    with open(os.path.join(output_dir, "model_config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n[ÉXITO] Modelo exportado en: {output_dir}")
    print(f"Mejor precisión de validación: {best_val_acc*100:.2f}%")

if __name__ == "__main__":
    train_model()
