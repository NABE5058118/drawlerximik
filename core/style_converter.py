import cv2
import numpy as np
import random

class StyleConverter:
    def __init__(self):
        self.styles = {
            "pencil": self._pencil_style,
            "pen_hatching": self._pen_hatching_style,
            "makelangelo5": self._makelangelo5_style,
            "portrait": self._portrait_style,
            "sketch": self._sketch_style,
            "contour": self._contour_style,
            "silhouette": self._silhouette_style,
            "blurred": self._blurred_style
        }
    
    def _sketch_style(self, image):
        """Стиль эскиза из первого проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        return sketch
    
    def _contour_style(self, image):
        """Стиль контура из первого проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1=50, threshold2=150)
        kernel = np.ones((1, 1), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=1)
        contours = np.zeros_like(gray)
        contours[edges_dilated != 0] = 255
        return contours
    
    def _silhouette_style(self, image):
        """Стиль силуэта из первого проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary
    
    def _blurred_style(self, image):
        """Размытый контур из первого проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_gray = cv2.medianBlur(gray, 7)
        edges_soft = cv2.Laplacian(blurred_gray, cv2.CV_8U, ksize=5)
        _, edge_mask = cv2.threshold(edges_soft, 80, 255, cv2.THRESH_BINARY_INV)
        return edge_mask
    
    def _pencil_style(self, image):
        """Карандашный стиль из второго проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0, 0)
        pencil_sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
        noise = np.random.normal(0, 15, pencil_sketch.shape).astype(np.uint8)
        pencil_sketch = cv2.add(pencil_sketch, noise)
        pencil_sketch = cv2.equalizeHist(pencil_sketch)
        return pencil_sketch
    
    def _pen_hatching_style(self, image):
        """Штриховка ручкой из второго проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hatching_layers = []
        angles = [45, 135]
        
        for angle in angles:
            kernel = self._create_hatching_kernel(angle, length=7)
            hatched = cv2.filter2D(gray, cv2.CV_32F, kernel)
            hatching_layers.append(hatched)
        
        combined = np.zeros_like(gray, dtype=np.float32)
        for layer in hatching_layers:
            combined = np.maximum(combined, layer)
        
        combined = cv2.normalize(combined, None, 0, 255, cv2.NORM_MINMAX)
        combined = np.uint8(combined)
        result = cv2.bitwise_not(combined)
        result = cv2.adaptiveThreshold(result, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        return result
    
    def _create_hatching_kernel(self, angle, length=5):
        kernel_size = max(7, length * 2 + 1)
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
        center = kernel_size // 2
        radians = np.radians(angle)
        
        for i in range(-length, length + 1):
            x = int(center + i * np.cos(radians))
            y = int(center + i * np.sin(radians))
            
            if 0 <= x < kernel_size and 0 <= y < kernel_size:
                weight = 1.0 - abs(i) / (length + 1)
                kernel[y, x] = weight
        
        kernel_sum = np.sum(kernel)
        if kernel_sum > 0:
            kernel /= kernel_sum
        
        return kernel - np.mean(kernel)
    
    def _makelangelo5_style(self, image):
        """Стиль Makelangelo 5 из второго проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        _, binary = cv2.threshold(inverted, 128, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(binary, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        canvas = np.zeros_like(gray)
        cv2.drawContours(canvas, contours, -1, 255, 1)
        noise = np.random.normal(0, 5, canvas.shape).astype(np.uint8)
        canvas = cv2.add(canvas, noise)
        return canvas

    def _portrait_style(self, image):
        """Портретный стиль из второго проекта"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        inverted = cv2.bitwise_not(gray)
        
        height, width = inverted.shape
        step = 3
        lines = []
        
        # Горизонтальные линии
        for y in range(0, height, step):
            line = []
            for x in range(width):
                intensity = inverted[y, x]
                if intensity > 100 and random.random() < intensity / 255.0:
                    line.append((x, y))
            if len(line) > 2:
                lines.append(line)
        
        # Вертикальные линии
        for x in range(0, width, step):
            line = []
            for y in range(height):
                intensity = inverted[y, x]
                if intensity > 100 and random.random() < intensity / 255.0:
                    line.append((x, y))
            if len(line) > 2:
                lines.append(line)
        
        # Диагональные линии
        for d in range(-height//2, width//2, step*2):
            line = []
            for x in range(max(0, d), min(width, d + height)):
                y = x - d
                if 0 <= y < height:
                    intensity = inverted[y, x]
                    if intensity > 100 and random.random() < intensity / 255.0:
                        line.append((x, y))
            if len(line) > 2:
                lines.append(line)
        
        canvas = np.zeros_like(gray)
        for line in lines:
            for i in range(len(line)-1):
                x1, y1 = line[i]
                x2, y2 = line[i+1]
                cv2.line(canvas, (x1, y1), (x2, y2), 255, 1)
        
        return canvas

    def apply_style(self, image, style_name):
        """Применяет выбранный стиль к изображению"""
        if style_name in self.styles:
            return self.styles[style_name](image)
        return self._sketch_style(image)  # fallback