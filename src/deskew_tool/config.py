from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    ENGLISH = "en_US"
    CHINESE = "zh_CN"


@dataclass
class DeskewConfig:
    # Basic settings
    dpi: int = 300
    background_color: tuple[int, int, int] = (255, 255, 255)

    # Watermark removal
    remove_watermark: bool = False
    watermark_method: str = "Inpainting"
    inpainting_algorithm: str = "Telea"
    watermark_threshold: int = 127

    # Image enhancement
    enhance_image: bool = False
    contrast_enhancement: bool = False
    contrast_level: int = 2
    denoising_method: str = "Gaussian"
    denoising_kernel: int = 3
    sharpening: bool = False
    sharpening_strength: int = 3

    # Grayscale conversion
    convert_grayscale: bool = False
    grayscale_quant_levels: int = 64
    grayscale_scale_factor: int = 1
    grayscale_smoothing_method: str = "Gaussian"
    grayscale_smoothing_kernel: int = 3

    @classmethod
    def from_dict(cls, data: dict):
        """Create a config from a dictionary, filtering out unknown keys."""
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def to_dict(self) -> dict:
        """Convert config to a dictionary."""
        return {k: v for k, v in self.__dict__.items()}
