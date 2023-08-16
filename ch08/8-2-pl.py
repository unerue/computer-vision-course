from collections import defaultdict

import lightning as L
import torch
import matplotlib.pyplot as plt
from torch import nn, optim
from torch.utils.data import DataLoader
from torchmetrics import Accuracy
from torchvision.datasets import CIFAR10
from torchvision.transforms import ToTensor


torch.set_float32_matmul_precision('medium')


class SequentialModule(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(3, 32, 3),
            nn.ReLU(),
            nn.Conv2d(32, 32, 3),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout(0.25),
            nn.Conv2d(32, 64, 5),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout(0.25),
            nn.Flatten(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 10),
        )
        self.loss = nn.CrossEntropyLoss()
        self.metric = Accuracy(task='multiclass', num_classes=10)
        
        self.train_loss_list = []
        self.train_acc_list = []
        self.val_loss_list = []
        self.val_acc_list = []

        self.history = defaultdict(list)

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
        self.train_loss_list.append(loss)
        self.train_acc_list.append(acc)

        logs = {'train_loss': loss, 'train_acc': acc}
        self.log_dict(logs, prog_bar=True)

        return loss
    
    def on_train_epoch_end(self):
        mean_loss = torch.tensor(self.train_loss_list).mean().item()
        mean_acc = torch.tensor(self.train_acc_list).mean().item()
        self.history['loss'].append(mean_loss)
        self.history['accuracy'].append(mean_acc)
        self.train_loss_list.clear()
        self.train_acc_list.clear()

    def validation_step(self, batch, batch_idx):
        x, y = batch

        y_hat = self(x)
        loss = self.loss(y_hat, y)
        acc = self.metric(y_hat, y)
        self.val_loss_list.append(loss)
        self.val_acc_list.append(acc)

        logs = {'val_acc': acc}
        self.log_dict(logs, prog_bar=True)

        return logs

    def on_validation_epoch_end(self):
        mean_loss = torch.tensor(self.val_loss_list).mean().item()
        mean_acc = torch.tensor(self.val_acc_list).mean().item()
        self.log('val_acc', mean_acc, prog_bar=True)
        self.history['val_loss'].append(mean_loss)
        self.history['val_accuracy'].append(mean_acc)
        self.val_loss_list.clear()
        self.val_acc_list.clear()

    def test_step(self, batch, batch_idx):
        x, y = batch

        y_hat = self(x)
        acc = self.metric(y_hat, y)

        logs = {'test_acc': acc}
        self.log_dict(logs, prog_bar=True)


train_data = CIFAR10(
    root='data',
    train=True,
    download=True,
    transform=ToTensor(),
)
test_data = CIFAR10(
    root='data',
    train=False,
    download=True,
    transform=ToTensor(),
)
train_loader = DataLoader(train_data, batch_size=128)
test_loader = DataLoader(test_data, batch_size=128)

cnn = SequentialModule()
trainer = L.Trainer(accelerator='gpu', devices=1, max_epochs=100)
trainer.fit(cnn, train_dataloaders=train_loader, val_dataloaders=test_loader)

# trainer.save_checkpoint('cnn_cifar10.ckpt')
# trainer.test(dmlp, dataloaders=test_loader, ckpt_path='cnn_cifar10.ckpt')

trainer.test(cnn, dataloaders=test_loader, ckpt_path='last')

plt.plot(cnn.history['accuracy'])
plt.plot(cnn.history['val_accuracy'])
plt.title('Accuracy graph')
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['train', 'test'])
plt.grid()
plt.show()

plt.plot(cnn.history['loss'])
plt.plot(cnn.history['val_loss'])
plt.title('Loss graph')
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['train', 'test'])
plt.grid()
plt.show()
