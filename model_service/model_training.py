#import torch
import torch.nn as nn
#from sklearn.datasets import load_iris
#from sklearn.model_selection import train_test_split
class SimpleClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size, num_classes)
    def forward(self, x):
        x = self.relu(self.layer1(x))
        return(self.layer2(x))
# #Train the model
# dataset = load_iris()
# X = dataset.data    
# y = dataset.target
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# model = SimpleClassifier(input_size=4, hidden_size=10, num_classes=3)
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
# num_epochs = 500
# for epoch in range(num_epochs):
#     model.train()
#     inputs = torch.tensor(X_train, dtype=torch.float32)
#     labels = torch.tensor(y_train, dtype=torch.long)
#     outputs = model(inputs)
#     loss = criterion(outputs, labels)
#     optimizer.zero_grad()
#     loss.backward()
#     optimizer.step()
#     if (epoch+1) % 10 == 0:
#         print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')
# #Evaluate the model
# model.eval()
# with torch.no_grad():
#     inputs = torch.tensor(X_test, dtype=torch.float32)
#     labels = torch.tensor(y_test, dtype=torch.long)
#     outputs = model(inputs)
#     _, predicted = torch.max(outputs.data, 1)
#     accuracy = (predicted == labels).sum().item() / len(labels)
#     print(f'Accuracy: {accuracy:.4f}')
# torch.save(model.state_dict(), 'simple_classifier.pth')