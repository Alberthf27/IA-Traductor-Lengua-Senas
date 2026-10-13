import os
from huggingface_hub import hf_hub_download

REPO_ID = "namratha2412/asl-improved-recognition"
TARGET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

def download_asl_models(target_dir=TARGET_DIR):
    """
    Descarga los archivos del modelo desde Hugging Face de forma automática
    y los almacena en la carpeta local 'models'.
    """
    os.makedirs(target_dir, exist_ok=True)
    
    files_to_download = [
        "best_model.pth",
        "label_encoder_classes.npy",
        "model_config.json"
    ]
    
    downloaded_paths = {}
    print(f"[*] Verificando/Descargando archivos desde {REPO_ID}...")
    for filename in files_to_download:
        dest_file = os.path.join(target_dir, filename)
        if not os.path.exists(dest_file):
            print(f"    - Descargando {filename}...")
            cached_path = hf_hub_download(repo_id=REPO_ID, filename=filename)
            # Copiar o mover a target_dir
            import shutil
            shutil.copy2(cached_path, dest_file)
            print(f"    [OK] Guardado en {dest_file}")
        else:
            print(f"    [OK] {filename} ya existe localmente.")
        downloaded_paths[filename] = dest_file
        
    print("[*] Todos los archivos del modelo están disponibles.")
    return downloaded_paths

if __name__ == "__main__":
    download_asl_models()
