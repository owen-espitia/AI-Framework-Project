import torch
print("Tensor O'clock!!")
#Tensor from list
list_1 = [1, 2, 3]
tensor_1 = torch.Tensor(list_1)
#Making Random Tensors
rand_tensor = torch.rand(3, 3)
rand_tensor2 = torch.rand(3, 3)
#Tensor Multiplication
mul_rand_tensor = rand_tensor.mul(rand_tensor2)
#Tensor Addition
add_rand_tensor = torch.add(rand_tensor, rand_tensor2)

x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x + 1    # y = x^2 + 2x + 1
y.backward()                # dy/dx = 2x + 2
print(f"x = {x.item()}, dy/dx = {x.grad.item()}")  # x = 3.0, dy/dx = 8.0
