import torch


def deterministic_example():
    torch.use_deterministic_algorithms(True)
