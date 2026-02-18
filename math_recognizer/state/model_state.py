import os

import reflex as rx

MODELS_DIR = "models/output"

VALID_EXTENSIONS = (".joblib", ".pickle", ".pkl", ".h5", ".keras")


def _inspect_model(path: str) -> dict:
    """Load a model file and return metadata about it."""
    info: dict = {"path": path, "valid": False, "error": ""}
    try:
        if path.endswith((".joblib", ".pickle", ".pkl")):
            import joblib
            model = joblib.load(path)
        elif path.endswith((".h5", ".keras")):
            from keras.models import load_model
            model = load_model(path)
            info["type"] = type(model).__name__
            info["valid"] = True
            return info
        else:
            info["error"] = "Formato no soportado"
            return info

        info["type"] = type(model).__name__

        # scikit-learn estimator inspection
        if hasattr(model, "classes_"):
            classes = [int(c) if hasattr(c, 'item') else c for c in model.classes_]
            info["n_classes"] = len(classes)
            info["classes"] = str(classes)
        if hasattr(model, "n_features_in_"):
            info["n_features"] = int(model.n_features_in_)
        if hasattr(model, "get_params"):
            params = model.get_params(deep=False)
            # Keep only a few key params to avoid clutter
            short = {k: v for k, v in params.items()
                     if k in ("kernel", "C", "gamma", "n_estimators",
                              "max_depth", "n_neighbors", "alpha",
                              "hidden_layer_sizes", "activation")}
            if short:
                info["params"] = str(short)

        info["valid"] = True
    except Exception as e:
        info["error"] = str(e)
    return info


class ModelState(rx.State):
    """State for ML model uploading and management."""

    upload_message: str = ""
    available_models: list[str] = []
    # Each entry: [filename, details_string]
    model_info_list: list[list[str]] = []
    selected_digit_model: str = ""
    selected_operator_model: str = ""

    def load_available_models(self):
        """Scan the models directory, populate the list, and inspect each model."""
        if os.path.exists(MODELS_DIR):
            self.available_models = sorted(
                f for f in os.listdir(MODELS_DIR)
                if f.endswith(VALID_EXTENSIONS)
                and not f.startswith(".")
            )
        else:
            self.available_models = []

        # Build info list with details for each model
        info_list = []
        for name in self.available_models:
            path = os.path.join(MODELS_DIR, name)
            detail = ""
            try:
                info = _inspect_model(path)
                if info["valid"]:
                    parts = [f"Tipo: {info.get('type', '?')}"]
                    if "n_classes" in info:
                        parts.append(f"Clases: {info['n_classes']} {info.get('classes', '')}")
                    if "n_features" in info:
                        parts.append(f"Features: {info['n_features']}")
                    if "params" in info:
                        parts.append(f"Params: {info['params']}")
                    detail = " | ".join(parts)
                else:
                    detail = f"Error: {info.get('error', 'desconocido')}"
            except Exception as e:
                detail = f"Error inspeccionando: {e}"
            info_list.append([name, detail])
        self.model_info_list = info_list

    def delete_model(self, name: str):
        """Delete a model file from disk and refresh the list."""
        path = os.path.join(MODELS_DIR, name)
        try:
            os.remove(path)
        except OSError:
            pass
        # Clear selection if the deleted model was selected
        if self.selected_digit_model == name:
            self.selected_digit_model = ""
        if self.selected_operator_model == name:
            self.selected_operator_model = ""
        self.upload_message = f"Eliminado: {name}"
        self.load_available_models()

    def set_digit_model(self, value: str):
        self.selected_digit_model = value

    def set_operator_model(self, value: str):
        self.selected_operator_model = value

    @staticmethod
    def _save_file(file_bytes: bytes, filename: str) -> str:
        os.makedirs(MODELS_DIR, exist_ok=True)
        file_path = os.path.join(MODELS_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        return file_path

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file upload — save, inspect, and report model info."""
        for file in files:
            name = file.filename
            if not name.endswith(VALID_EXTENSIONS):
                self.upload_message = f"Formato no soportado: {name}"
                return

            upload_data = await file.read()
            file_path = self._save_file(upload_data, name)

            info = _inspect_model(file_path)
            if not info["valid"]:
                self.upload_message = f"Error al cargar {name}: {info['error']}"
                # Remove the bad file
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                self.load_available_models()
                return

            # Build a human-readable summary
            parts = [f"Guardado: {name}"]
            parts.append(f"Tipo: {info.get('type', '?')}")
            if "n_classes" in info:
                parts.append(f"Clases: {info['n_classes']} {info.get('classes', '')}")
            if "n_features" in info:
                parts.append(f"Features: {info['n_features']}")
            if "params" in info:
                parts.append(f"Params: {info['params']}")

            self.upload_message = " | ".join(parts)

        self.load_available_models()
