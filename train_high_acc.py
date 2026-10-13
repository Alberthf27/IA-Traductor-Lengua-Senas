import os
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from huggingface_hub import hf_hub_download

def train_autonomous():
    print("=" * 65)
    print("  ENTRENAMIENTO AUTÓNOMO EN SEGUNDO PLANO")
    print("  Optimizando modelo de alta precisión sobre landmarks")
    print("=" * 65)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Dispositivo de cómputo: {device}")
    
    # Descargar dataset de Hugging Face
    print("[*] Descargando dataset Siruyy/asl-static-landmarks-v1...")
    p_x_train = hf_hub_download(repo_id="Siruyy/asl-static-landmarks-v1", filename="X_train.npy", repo_type="dataset")
    p_y_train = hf_hub_download(repo_id="Siruyy/asl-static-landmarks-v1", filename="y_train.npy", repo_type="dataset")
    p_x_test = hf_hub_download(repo_id="Siruyy/asl-static-landmarks-v1", filename="X_test.npy", repo_type="dataset")
    p_y_test = hf_hub_download(repo_id="Siruyy/asl-static-landmarks-v1", filename="y_test.npy", repo_type="dataset")

    X_train = np.load(p_x_train)
    y_train = np.load(p_y_train)
    X_test = np.load(p_x_test)
    y_test = np.load(p_y_test)

    # Combinar y hacer split estratificado limpio
    X = np.vstack([X_train, X_test]).astype(np.float32)
    y = np.concatenate([y_train, y_test])

    classes = sorted(list(set(y)))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y_idx = np.array([class_to_idx[c] for c in y], dtype=np.int64)

    np.random.seed(42)
    indices = np.random.permutation(len(X))
    split_idx = int(len(X) * 0.85)
    tr_idx, val_idx = indices[:split_idx], indices[split_idx:]
    X_tr, y_tr = X[tr_idx], y_idx[tr_idx]
    X_val, y_val = X[val_idx], y_idx[val_idx]

    train_ds = TensorDataset(torch.tensor(X_tr), torch.tensor(y_tr))
    val_ds = TensorDataset(torch.tensor(X_val), torch.tensor(y_val))

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

    num_classes = len(classes)
    input_dim = X.shape[1]
    print(f"[*] Muestras: {len(X)} | Features: {input_dim} | Clases: {num_classes}")

    # Red neuronal profunda con Residuals + BatchNorm + Dropout
    class RobustLandmarkMLP(nn.Module):
        def __init__(self, in_features, num_classes):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(in_features, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Dropout(0.25),
                nn.Linear(256, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Dropout(0.25),
                nn.Linear(256, 128),
                nn.BatchNorm1d(128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, num_classes)
            )
        def forward(self, x):
            return self.net(x)

    model = RobustLandmarkMLP(input_dim, num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=4)

    best_val_acc = 0.0
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models_high_acc")
    os.makedirs(output_dir, exist_ok=True)

    epochs = 40
    print(f"\n[*] Entrenando durante {epochs} épocas...")
    for ep in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        correct_tr = 0
        total_tr = 0

        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(by)
            preds = out.argmax(dim=-1)
            correct_tr += (preds == by).sum().item()
            total_tr += len(by)

        model.eval()
        correct_val = 0
        total_val = 0
        with torch.no_grad():
            for bx, by in val_loader:
                bx, by = bx.to(device), by.to(device)
                out = model(bx)
                preds = out.argmax(dim=-1)
                correct_val += (preds == by).sum().item()
                total_val += len(by)

        val_acc = correct_val / total_val if total_val > 0 else 0.0
        scheduler.step(val_acc)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(output_dir, "best_model.pth"))

        if ep % 5 == 0 or ep == epochs:
            print(f"Época [{ep:02d}/{epochs:02d}] - Train Acc: {correct_tr/total_tr*100:.1f}% | Val Acc: {val_acc*100:.1f}% (Mejor: {best_val_acc*100:.1f}%)")

    # Guardar metadatos
    np.save(os.path.join(output_dir, "classes.npy"), np.array(classes))
    info = {
        "num_classes": num_classes,
        "input_features": input_dim,
        "best_val_acc": float(best_val_acc),
        "classes": [str(c) for c in classes]
    }
    with open(os.path.join(output_dir, "info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    print(f"\n[FINALIZADO CON ÉXITO] Mejor precisión alcanzada: {best_val_acc*100:.2f}%")
    print(f"Archivos guardados en: {output_dir}")

if __name__ == "__main__":
    train_autonomous()
