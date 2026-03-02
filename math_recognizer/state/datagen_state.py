import reflex as rx


class DatagenState(rx.State):
    """State for the data generator page."""

    stroke_width: int = 8
    stroke_color: str = "#ffffff"
    canvas_bg_color: str = "#333333"
    resolution: int = 280
    _download_count: int = 0

    @rx.var
    def resolution_label(self) -> str:
        return f"{self.resolution} \u00d7 {self.resolution} px"

    def update_stroke_width(self, value: list[float]):
        self.stroke_width = int(value[0])

    def update_resolution(self, value: list[float]):
        self.resolution = int(value[0])

    def download_image(self):
        """Export canvas, resize to target resolution in JS, and download."""
        self._download_count += 1
        count = self._download_count
        res = self.resolution
        js = (
            "(async()=>{"
            "const d=await window.exportCanvas_datagen();"
            "if(!d)return;"
            "const img=document.createElement('img');"
            "img.src=d;"
            "await new Promise(r=>{img.onload=r;});"
            "const c=document.createElement('canvas');"
            f"c.width={res};c.height={res};"
            "const ctx=c.getContext('2d');"
            f"ctx.drawImage(img,0,0,{res},{res});"
            "const url=c.toDataURL('image/png');"
            "const a=document.createElement('a');"
            "a.href=url;"
            f"a.download='dato_{count}_{res}x{res}.png';"
            "document.body.appendChild(a);a.click();document.body.removeChild(a);"
            "})()"
        )
        return rx.call_script(js)

    def clear_canvas(self):
        """Clear the drawing canvas."""
        return rx.call_script("window.clearCanvas_datagen()")
