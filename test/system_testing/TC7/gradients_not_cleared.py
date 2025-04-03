import torch


def gradients_not_cleared():
    optimizer = torch.optim.SGD(  # noqa
        [torch.tensor([1.0], requires_grad=True)], lr=0.01
    )  # noqa

    for i in range(10):
        loss = torch.tensor([i], requires_grad=True)
        loss.backward()  # Punto di rilevamento: Nessun `zero_grad()` prima
