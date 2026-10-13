import torch
import torch.nn as nn
import torch.nn.functional as F

class ImprovedASLModel(nn.Module):
    """
    Arquitectura híbrida CNN 1D + Bi-LSTM + Atención para reconocimiento de ASL.
    Entrada esperada:
      - (batch_size, seq_len, 2, 21, 3) o (batch_size, seq_len, 126)
    Salida:
      - Logits de dimensión (batch_size, num_classes)
    """
    def __init__(self, num_classes=77, dropout=0.3):
        super().__init__()
        
        # Bloque Convolucional 1D para extracción de características espaciales de los landmarks
        self.conv_layers = nn.Sequential(
            nn.Conv1d(in_channels=126, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Bloque Recurrente Bidireccional (Bi-LSTM) para modelar dependencias temporales
        self.lstm = nn.LSTM(
            input_size=256,
            hidden_size=256,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        
        # Mecanismo de Atención temporal
        self.attention = nn.Sequential(
            nn.Linear(512, 128),
            nn.Tanh(),
            nn.Linear(128, 1)
        )
        
        # Clasificador Perceptrón Multicapa (MLP)
        self.classifier = nn.Sequential(
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        # Aplanar landmarks si vienen con dimensiones de mano y coordenadas:
        # (batch, seq_len, 2, 21, 3) -> (batch, seq_len, 126)
        if x.dim() == 5:
            b, s = x.shape[0], x.shape[1]
            x = x.view(b, s, -1)
            
        # Conv1d espera forma (batch, canales, seq_len)
        x = x.transpose(1, 2)
        x = self.conv_layers(x)
        
        # LSTM espera forma (batch, seq_len, características)
        x = x.transpose(1, 2)
        lstm_out, _ = self.lstm(x)  # shape: (batch, seq_len, 512)
        
        # Cálculo de pesos de atención sobre la dimensión temporal
        attn_scores = self.attention(lstm_out)  # shape: (batch, seq_len, 1)
        attn_weights = F.softmax(attn_scores, dim=1)
        
        # Vector de contexto ponderado por atención
        context = torch.sum(attn_weights * lstm_out, dim=1)  # shape: (batch, 512)
        
        # Clasificación final
        logits = self.classifier(context)  # shape: (batch, num_classes)
        return logits
