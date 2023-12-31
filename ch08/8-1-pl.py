import lightning as L
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchmetrics import Accuracy
from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor


torch.set_float32_matmul_precision("medium")


class SequentialModule(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(1, 6, 5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(6, 16, 5),
            nn.ReLU(),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(16, 120, 5),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(120, 84),
            nn.ReLU(),
            nn.Linear(84, 10),
        )
        self.loss = nn.CrossEntropyLoss()
        self.metric = Accuracy(task="multiclass", num_classes=10)
        
        self.acc_list = []

    def configure_optimizers(self):
        return optim.Adam(self.model.parameters(), lr=0.001)

    def forward(self, x):
        x = self.model(x)
        return x

    def training_step(self, batch, batch_idx):
        x, y = batch

        y_hat = self(x)
        loss = self.loss(y_hat, y)
        acc = self.metric(y_hat, y)

        logs = {"train_loss": loss, "train_acc": acc}
        self.log_dict(logs, prog_bar=True)

        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch

        y_hat = self(x)
        acc = self.metric(y_hat, y)
        self.acc_list.append(acc)

        logs = {"val_acc": acc}
        self.log_dict(logs, prog_bar=True)

        return logs

    def on_validation_epoch_end(self):
        mean_acc = torch.tensor(self.acc_list).mean().item()
        self.log("val_acc", mean_acc, prog_bar=True)
        self.acc_list.clear()

    def test_step(self, batch, batch_idx):
        x, y = batch

        y_hat = self(x)
        acc = self.metric(y_hat, y)

        logs = {"test_acc": acc}
        self.log_dict(logs, prog_bar=True)


train_data = MNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
)
test_data = MNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor(),
)
train_loader = DataLoader(train_data, batch_size=128)
test_loader = DataLoader(test_data, batch_size=128)

model = SequentialModule()
trainer = L.Trainer(accelerator="gpu", devices=1, max_epochs=30)
trainer.fit(model, train_dataloaders=train_loader, val_dataloaders=test_loader)

trainer.test(model, dataloaders=test_loader, ckpt_path="last")
