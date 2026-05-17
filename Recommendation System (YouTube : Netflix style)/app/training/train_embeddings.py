import torch
from torch.optim import Adam
from app.retrieval.embedding_model import TwoTowerModel


model = TwoTowerModel()
optimizer = Adam(model.parameters(), lr=0.001)
criterion = torch.nn.MSELoss()


for epoch in range(10):

    user_features = torch.randn(32, 128)
    item_features = torch.randn(32, 128)
    labels = torch.randn(32)

    predictions = model(
        user_features,
        item_features
    )
    
    loss = criterion(predictions, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"epoch={epoch} loss={loss.item()}")


torch.save(model.state_dict(), "two_tower.pt")