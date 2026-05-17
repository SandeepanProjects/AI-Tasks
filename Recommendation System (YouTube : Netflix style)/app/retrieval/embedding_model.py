import torch
import torch.nn as nn


class UserTower(nn.Module):

    def __init__(self, input_dim=128, emb_dim=64):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
            nn.Linear(256, emb_dim)
        )

    def forward(self, x):
        return self.network(x)

class ItemTower(nn.Module):

    def __init__(self, input_dim=128, emb_dim=64):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
            nn.Linear(256, emb_dim)
        )

    def forward(self, x):
        return self.network(x)

class TwoTowerModel(nn.Module):

    def __init__(self):
        super().__init__()

        self.user_tower = UserTower()
        self.item_tower = ItemTower()

    def forward(self, user_features, item_features):

        user_embedding = self.user_tower(user_features)
        item_embedding = self.item_tower(item_features)

        similarity = torch.sum(
            user_embedding * item_embedding,
            dim=1
        )

        return similarity