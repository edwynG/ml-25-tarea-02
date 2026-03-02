import base64
import io
import os

import numpy as np
import reflex as rx
from PIL import Image

from math_recognizer.utils.image_processing import (
    prepare_digit_image,
    prepare_operator_image,
)

MODELS_DIR = "models/output"

# 0: +, 1: -, 2: x (mult), 3: * (mult), 4: ÷ (div), 5: / (div)
DEFAULT_OPERATOR_LABELS = {
    0: "+",
    1: "-",
    2: "*",
    3: "*",
    4: "/",
    5: "/",
}


def _load_model(path: str):
    if path.endswith((".joblib", ".pickle", ".pkl")):
        import joblib
        return joblib.load(path)
    elif path.endswith((".h5", ".keras")):
        from keras.models import load_model
        return load_model(path)
    return None


class GameState(rx.State):
    """State for the math expression game with 8 canvases."""

    # Base64 image data from each canvas
    number_1_data: str = ""
    number_2_data: str = ""
    number_3_data: str = ""
    exponent_1_data: str = ""
    exponent_2_data: str = ""
    exponent_3_data: str = ""
    operator_1_data: str = ""
    operator_2_data: str = ""

    # Predicted values
    pred_number_1: str = "?"
    pred_number_2: str = "?"
    pred_number_3: str = "?"
    pred_exponent_1: str = "?"
    pred_exponent_2: str = "?"
    pred_exponent_3: str = "?"
    pred_operator_1: str = "?"
    pred_operator_2: str = "?"

    # Operator label mapping (class index → symbol). Configurable per student.
    # 0: +, 1: -, 2: x (mult), 3: * (mult), 4: ÷ (div), 5: / (div)
    op_label_0: str = "+"
    op_label_1: str = "-"
    op_label_2: str = "*"
    op_label_3: str = "*"
    op_label_4: str = "/"
    op_label_5: str = "/"

    # Expression and result
    expression: str = ""
    result: str = ""
    status_message: str = ""
    is_loading: bool = False

    # Debug: per-canvas model output
    # Each entry: [label, pred, type, cls0, val0, pct0, cls1, val1, pct1, ...]
    # Sorted descending by score. Padded to 10 classes (30 score slots + 3 header = 33).
    debug_entries: list[list[str]] = []

    # Debug: 28x28 processed images as base64 data URLs (shown after eval)
    debug_img_number_1: str = ""
    debug_img_number_2: str = ""
    debug_img_number_3: str = ""
    debug_img_exponent_1: str = ""
    debug_img_exponent_2: str = ""
    debug_img_exponent_3: str = ""
    debug_img_operator_1: str = ""
    debug_img_operator_2: str = ""
    show_debug: bool = False
    show_panel: bool = True
    _pending_exports: int = 0
    _awaiting_prediction: bool = False

    @staticmethod
    def _decode_b64(data_url: str) -> np.ndarray | None:
        if not data_url or "," not in data_url:
            return None
        raw = base64.b64decode(data_url.split(",")[1])
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        return np.array(img)

    @staticmethod
    def _flatten(img_28: np.ndarray) -> np.ndarray:
        """Flatten a 28x28 image to (1, 784) float32."""
        return img_28.reshape(1, -1).astype("float32") / 255.0 # Normalize to [0, 1]

    @staticmethod
    def _img_to_data_url(img_28x28: np.ndarray) -> str:
        """Convert a 28x28 uint8 grayscale image to a base64 PNG data URL."""
        pil_img = Image.fromarray(img_28x28, mode="L")
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    @staticmethod
    def _predict_with_model(model, flat: np.ndarray) -> np.ndarray:
        """Run model.predict and return raw output array."""
        pred = model.predict(flat)
        return np.asarray(pred)

    @staticmethod
    def _ovo_votes(decision_values: np.ndarray, n_classes: int) -> list[int]:
        """Convert OvO decision_function values into per-class vote counts."""
        votes = [0] * n_classes
        k = 0
        for i in range(n_classes):
            for j in range(i + 1, n_classes):
                if k < len(decision_values):
                    if decision_values[k] > 0:
                        votes[i] += 1
                    else:
                        votes[j] += 1
                    k += 1
        return votes

    @staticmethod
    def _build_score_row(label: str, pred: str, scores: dict) -> list[str]:
        """Build a flat row sorted by class label ascending.

        Layout: [label, pred, type, winner_cls, cls0, val0, pct0, ...]
        Padded to 34 elements (4 header + 10 classes * 3 slots).
        """
        score_type = scores.get("score_type", "")
        score_vals = scores.get("scores", {})
        row: list[str] = [label, pred, score_type]

        if not score_vals:
            return row + [""] * 31

        # Find the winning class (highest score)
        winner_cls = max(score_vals, key=lambda k: float(score_vals[k]))
        row.append(str(winner_cls))

        # Sort by class label ascending (0, 1, 2, ... or ASCII codes)
        sorted_scores = sorted(
            score_vals.items(), key=lambda x: (float(x[0]) if x[0].lstrip('-').isdigit() else x[0]),
        )

        # Compute max for percentage normalization
        max_val = max(float(v) for v in score_vals.values())
        if max_val <= 0:
            max_val = 1.0

        for cls_key, raw_val in sorted_scores:
            raw_f = float(raw_val)
            if score_type == "proba":
                pct = raw_f * 100
                display = f"{raw_f:.3f}"
            else:  # votes or other
                pct = (raw_f / max_val) * 100
                display = str(int(raw_f)) if raw_f == int(raw_f) else f"{raw_f:.2f}"
            row.extend([str(cls_key), display, f"{pct:.1f}"])

        # Pad to 34 total (4 header + 10 classes * 3 slots)
        while len(row) < 34:
            row.append("")

        return row

    @staticmethod
    def _get_model_scores(model, flat: np.ndarray) -> dict:
        """Return structured score info from the model."""
        result: dict = {}
        classes = None
        if hasattr(model, "classes_"):
            classes = [int(c) if hasattr(c, "item") else c for c in model.classes_]
            result["classes"] = classes

        if hasattr(model, "predict_proba"):
            try:
                proba = model.predict_proba(flat)[0]
                if classes:
                    result["scores"] = {str(c): round(float(p), 3) for c, p in zip(classes, proba)}
                    result["score_type"] = "proba"
            except Exception:
                pass

        if "scores" not in result and hasattr(model, "decision_function"):
            try:
                dec = model.decision_function(flat)
                vals = dec[0] if dec.ndim >= 2 else dec
                vals = np.asarray(vals)
                n_cls = len(classes) if classes else 0
                expected_ovo = n_cls * (n_cls - 1) // 2
                if n_cls > 0 and len(vals) == expected_ovo:
                    votes = GameState._ovo_votes(vals, n_cls)
                    result["scores"] = {str(c): v for c, v in zip(classes, votes)}
                    result["score_type"] = "votos"
                    result["max_votes"] = n_cls - 1
            except Exception:
                pass

        return result

    @staticmethod
    def _predict_digit(model, img_array: np.ndarray) -> tuple[int, np.ndarray, dict]:
        """Returns (predicted_digit, processed_28x28_image, scores_dict).

        Preprocessing: grayscale → resize 28x28 → equalizeHist → invert
        """
        img_28 = prepare_digit_image(img_array)
        flat = GameState._flatten(img_28)
        pred = GameState._predict_with_model(model, flat)
        if pred.ndim >= 2 and pred.shape[-1] > 1:
            digit = int(np.argmax(pred[0]))
        else:
            digit = int(pred.flat[0])
        scores = GameState._get_model_scores(model, flat)
        return digit, img_28, scores

    def _predict_operator(self, model, img_array: np.ndarray) -> tuple[str, int, np.ndarray, dict]:
        """Returns (symbol, class_idx, processed_28x28_image, scores_dict).

        Preprocessing: grayscale → resize 28x28 → equalizeHist (NO inversion)
        """
        img_28 = prepare_operator_image(img_array)
        flat = GameState._flatten(img_28)
        pred = GameState._predict_with_model(model, flat)

        if pred.ndim >= 2 and pred.shape[-1] > 1:
            idx = int(np.argmax(pred[0]))
        else:
            idx = int(pred.flat[0])

        label_map = {
            0: self.op_label_0,
            1: self.op_label_1,
            2: self.op_label_2,
            3: self.op_label_3,
            4: self.op_label_4,
            5: self.op_label_5,
        }
        symbol = label_map.get(idx, f"?({idx})")
        scores = GameState._get_model_scores(model, flat)
        return symbol, idx, img_28, scores

    async def _on_canvas_received(self):
        """Called after each canvas data arrives. When all 8 are in, run prediction."""
        if not self._awaiting_prediction:
            return
        self._pending_exports += 1
        if self._pending_exports >= 8:
            self._awaiting_prediction = False
            self._pending_exports = 0
            await self._run_prediction()

    async def receive_number_1(self, data: str):
        self.number_1_data = data
        await self._on_canvas_received()

    async def receive_number_2(self, data: str):
        self.number_2_data = data
        await self._on_canvas_received()

    async def receive_number_3(self, data: str):
        self.number_3_data = data
        await self._on_canvas_received()

    async def receive_exponent_1(self, data: str):
        self.exponent_1_data = data
        await self._on_canvas_received()

    async def receive_exponent_2(self, data: str):
        self.exponent_2_data = data
        await self._on_canvas_received()

    async def receive_exponent_3(self, data: str):
        self.exponent_3_data = data
        await self._on_canvas_received()

    async def receive_operator_1(self, data: str):
        self.operator_1_data = data
        await self._on_canvas_received()

    async def receive_operator_2(self, data: str):
        self.operator_2_data = data
        await self._on_canvas_received()

    def export_all_canvases(self):
        """Trigger JS export for all 8 canvases (no prediction)."""
        return [
            rx.call_script(
                f"window.exportCanvas_{cid}()",
                callback=getattr(GameState, cb),
            )
            for cid, cb in [
                ("number_1", "receive_number_1"),
                ("number_2", "receive_number_2"),
                ("number_3", "receive_number_3"),
                ("exponent_1", "receive_exponent_1"),
                ("exponent_2", "receive_exponent_2"),
                ("exponent_3", "receive_exponent_3"),
                ("operator_1", "receive_operator_1"),
                ("operator_2", "receive_operator_2"),
            ]
        ]

    def download_canvases(self):
        """Download each canvas that has data as a PNG via the browser."""
        scripts = []
        for name, data in [
            ("number_1", self.number_1_data),
            ("number_2", self.number_2_data),
            ("number_3", self.number_3_data),
            ("exponent_1", self.exponent_1_data),
            ("exponent_2", self.exponent_2_data),
            ("exponent_3", self.exponent_3_data),
            ("operator_1", self.operator_1_data),
            ("operator_2", self.operator_2_data),
        ]:
            if data and "," in data:
                js = (
                    f"var a=document.createElement('a');"
                    f"a.href='{data}';"
                    f"a.download='{name}.png';"
                    f"document.body.appendChild(a);a.click();document.body.removeChild(a);"
                )
                scripts.append(rx.call_script(js))
        if not scripts:
            self.status_message = "Primero exporta los canvas antes de descargar."
            return
        self.status_message = "Descargando imagenes..."
        return scripts

    def clear_all_canvases(self):
        """Clear all canvases and reset predictions."""
        for attr in [
            "number_1_data", "number_2_data", "number_3_data",
            "exponent_1_data", "exponent_2_data", "exponent_3_data",
            "operator_1_data", "operator_2_data",
        ]:
            setattr(self, attr, "")
        for attr in [
            "pred_number_1", "pred_number_2", "pred_number_3",
            "pred_exponent_1", "pred_exponent_2", "pred_exponent_3",
            "pred_operator_1", "pred_operator_2",
        ]:
            setattr(self, attr, "?")
        for attr in [
            "debug_img_number_1", "debug_img_number_2", "debug_img_number_3",
            "debug_img_exponent_1", "debug_img_exponent_2", "debug_img_exponent_3",
            "debug_img_operator_1", "debug_img_operator_2",
        ]:
            setattr(self, attr, "")
        self.expression = ""
        self.result = ""
        self.status_message = ""
        self.debug_entries = []
        self._awaiting_prediction = False
        self._pending_exports = 0
        return [
            rx.call_script(f"window.clearCanvas_{cid}()")
            for cid in [
                "number_1", "number_2", "number_3",
                "exponent_1", "exponent_2", "exponent_3",
                "operator_1", "operator_2",
            ]
        ]

    async def evaluate_expression(self):
        """Export all canvases, then auto-run prediction when all 8 arrive."""
        from math_recognizer.state.model_state import ModelState

        ms = await self.get_state(ModelState)

        if not ms.selected_digit_model:
            self.status_message = "Selecciona un modelo de digitos primero."
            return
        if not ms.selected_operator_model:
            self.status_message = "Selecciona un modelo de operadores primero."
            return

        digit_path = os.path.join(MODELS_DIR, ms.selected_digit_model)
        op_path = os.path.join(MODELS_DIR, ms.selected_operator_model)

        if not os.path.exists(digit_path):
            self.status_message = f"No se encuentra: {ms.selected_digit_model}"
            return
        if not os.path.exists(op_path):
            self.status_message = f"No se encuentra: {ms.selected_operator_model}"
            return

        # Arm the counter — when all 8 callbacks arrive, _run_prediction fires
        self._awaiting_prediction = True
        self._pending_exports = 0
        self.is_loading = True
        self.status_message = "Exportando canvas y clasificando..."

        return self.export_all_canvases()

    async def _run_prediction(self):
        """Run ML models on all canvas data and evaluate the expression."""
        from math_recognizer.state.model_state import ModelState

        ms = await self.get_state(ModelState)
        digit_path = os.path.join(MODELS_DIR, ms.selected_digit_model)
        op_path = os.path.join(MODELS_DIR, ms.selected_operator_model)

        try:
            digit_model = _load_model(digit_path)
            op_model = _load_model(op_path)

            if digit_model is None or op_model is None:
                self.status_message = "Error cargando modelos."
                self.is_loading = False
                return

            # Predict digits + exponents
            entries = []
            for canvas_attr, pred_attr, dbg_attr, label in [
                ("number_1_data", "pred_number_1", "debug_img_number_1", "Num 1"),
                ("number_2_data", "pred_number_2", "debug_img_number_2", "Num 2"),
                ("number_3_data", "pred_number_3", "debug_img_number_3", "Num 3"),
                ("exponent_1_data", "pred_exponent_1", "debug_img_exponent_1", "Exp 1"),
                ("exponent_2_data", "pred_exponent_2", "debug_img_exponent_2", "Exp 2"),
                ("exponent_3_data", "pred_exponent_3", "debug_img_exponent_3", "Exp 3"),
            ]:
                img = self._decode_b64(getattr(self, canvas_attr))
                if img is not None:
                    digit, img_28, scores = self._predict_digit(digit_model, img)
                    setattr(self, pred_attr, str(digit))
                    setattr(self, dbg_attr, self._img_to_data_url(img_28))
                    entries.append(self._build_score_row(label, str(digit), scores))
                else:
                    setattr(self, pred_attr, "?")
                    setattr(self, dbg_attr, "")

            # Predict operators
            for canvas_attr, pred_attr, dbg_attr, label in [
                ("operator_1_data", "pred_operator_1", "debug_img_operator_1", "Op 1"),
                ("operator_2_data", "pred_operator_2", "debug_img_operator_2", "Op 2"),
            ]:
                img = self._decode_b64(getattr(self, canvas_attr))
                if img is not None:
                    symbol, idx, img_28, scores = self._predict_operator(op_model, img)
                    setattr(self, pred_attr, symbol)
                    setattr(self, dbg_attr, self._img_to_data_url(img_28))
                    entries.append(self._build_score_row(label, f"{symbol} ({idx})", scores))
                else:
                    setattr(self, pred_attr, "?")
                    setattr(self, dbg_attr, "")
            self.debug_entries = entries

            # Build and evaluate expression
            n1, n2, n3 = self.pred_number_1, self.pred_number_2, self.pred_number_3
            e1, e2, e3 = self.pred_exponent_1, self.pred_exponent_2, self.pred_exponent_3
            op1, op2 = self.pred_operator_1, self.pred_operator_2

            if "?" in [n1, n2, n3, e1, e2, e3, op1, op2]:
                self.status_message = "No se pudieron clasificar todos los canvas. Asegurate de dibujar en todos."
                self.is_loading = False
                return

            op1_safe = self._normalize_operator(op1)
            op2_safe = self._normalize_operator(op2)
            if op1_safe is None or op2_safe is None:
                self.status_message = f"Operador no reconocido: {op1}, {op2}"
                self.is_loading = False
                return

            self.expression = f"{n1}^{e1} {op1} {n2}^{e2} {op2} {n3}^{e3}"

            val1 = int(n1) ** int(e1)
            val2 = int(n2) ** int(e2)
            val3 = int(n3) ** int(e3)
            computed = eval(f"{val1} {op1_safe} {val2} {op2_safe} {val3}")
            self.result = f"{computed:.3f}" if isinstance(computed, float) else str(computed)
            self.status_message = ""

        except Exception as e:
            self.status_message = f"Error: {e}"
        finally:
            self.is_loading = False

    @staticmethod
    def _normalize_operator(op: str) -> str | None:
        mapping = {
            "+": "+", "-": "-",
            "*": "*", "\u00d7": "*", "x": "*", "X": "*",
            "/": "/", "\u00f7": "/",
        }
        return mapping.get(op)
