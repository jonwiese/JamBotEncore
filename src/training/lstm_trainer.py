from pathlib import Path

import torch
from torch.utils.tensorboard import SummaryWriter


class LstmTrainerConfig:
    def __init__(self, loss_fn, optimizer, num_epochs, model_folder: Path):
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.num_epochs = num_epochs
        self.model_folder = model_folder


class LstmTrainer:
    def __init__(self, model: torch.nn.Module, training_data, test_data, config: LstmTrainerConfig):
        self._config = config
        self.model = model
        self.training_data = training_data
        self.test_data = test_data
        self.tensorboard_writer = self.__get_tensorboard_writer()
        self.training_loss = []
        self.test_loss = []

    def train(self) -> None:
        for epoch in range(self._config.num_epochs):
            train_loss = self.__train_one_epoch()
            self.tensorboard_writer.add_scalar('training_loss', train_loss, epoch)
            self.training_loss.append(train_loss)

            test_loss = self.__get_test_loss()
            self.tensorboard_writer.add_scalar('test_loss', test_loss, epoch)
            self.test_loss.append(test_loss)

    def __get_tensorboard_writer(self):
        tensorboard_path = self._config.model_folder.joinpath('tensorboard')
        return SummaryWriter(str(tensorboard_path))

    def __train_one_epoch(self) -> float:
        running_loss = 0.0
        for input_sequence, target in self.training_data:
            input_sequence = torch.tensor(input_sequence).view(len(input_sequence), 1, -1)
            target = torch.tensor(target)

            # Forward pass
            output = self.model(input_sequence)
            loss = self._config.loss_fn(output, target)

            # Backward pass
            self._config.optimizer.zero_grad()
            loss.backward()
            self._config.optimizer.step()
            running_loss += loss.item()

        epoch_loss = running_loss/len(self.training_data)
        return epoch_loss

    def __get_test_loss(self) -> float:
        total_loss = 0
        for input_sequence, target in self.test_data:
            input_sequence = torch.tensor(input_sequence).view(len(input_sequence), 1, -1)
            target = torch.tensor(target)
            with torch.no_grad():
                output = self.model(input_sequence)
                total_loss += self._config.loss_fn(output, target).item()
        return total_loss / len(self.test_data)
