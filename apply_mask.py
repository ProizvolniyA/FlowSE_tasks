#import torch as th
import random
"""
    Args:
        spectrogram (torch.Tensor): Тензор формы [1, F, T] или [Batch, 1, F, T]
        num_masks (int): Количество прямоугольников.
        max_h (int): Максимальная высота маски (по частоте).
        max_w (int): Максимальная ширина маски (по времени).
    
    Returns:
        torch.Tensor: Спектрограмма с масками.
"""
def apply_random_mask(spectrogram, num_masks=5, max_h=20, max_w=40):
    
    masked_spec = spectrogram.clone()
    
    if masked_spec.dim() == 4:
        b, c, f, t = masked_spec.shape
    else:
        c, f, t = masked_spec.shape
        b = 1
        masked_spec = masked_spec.unsqueeze(0) 

    for i in range(b):
        for _ in range(num_masks):
            
            h = random.randint(5, max_h)
            w = random.randint(10, max_w)
            
            y = random.randint(0, f - h)
            x = random.randint(0, t - w)
            
            masked_spec[i, :, y:y+h, x:x+w] = 0
            
    return masked_spec.squeeze(0) if b == 1 else masked_spec
