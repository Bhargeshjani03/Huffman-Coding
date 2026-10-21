
# ============================================================
# train_mnist.py
# Purpose:
# 1. Download the MNIST dataset.
# 2. Train our feed-forward neural network.
# 3. Evaluate its accuracy on test images.
# 4. Save the trained model and baseline metrics.
# ============================================================

# Standard Python libraries
import json                  # Save experiment details in JSON format
import random                # Control Python's random number generator
import time                  # Measure training and evaluation time
from pathlib import Path     # Work with file and folder paths

# PyTorch libraries
import torch
from torch import nn
from torch.utils.data import DataLoader

# TorchVision provides the MNIST dataset and image transformations
from torchvision import datasets, transforms

# Import our neural network architecture from src/model.py
from src.model import MNISTModel


# ============================================================
# 1. DEFINE PROJECT DIRECTORIES
# ============================================================

# __file__ is the path of this script.
# resolve() converts it to an absolute path.
# parents[1] moves up to the project root directory.
ROOT = Path(__file__).resolve().parents[1]

# Folder where the MNIST dataset will be stored
DATA_DIR = ROOT / "data"

# Folder where the trained model and metrics will be saved
CHECKPOINT_DIR = ROOT / "checkpoints"

# Create the checkpoints folder if it does not exist.
# parents=True creates missing parent directories.
# exist_ok=True avoids an error if the folder already exists.
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. SET RANDOM SEEDS AND COMPUTING DEVICE
# ============================================================

# A fixed seed helps make experiments reproducible.
SEED = 42

# Set Python's random seed
random.seed(SEED)

# Set PyTorch's random seed for model initialisation and
# other PyTorch random operations.
torch.manual_seed(SEED)

# Use CPU for simplicity and compatibility.
# The model, images, and labels will use the same device.
device = torch.device("cpu")


# ============================================================
# 3. PREPARE THE MNIST IMAGES
# ============================================================

# Convert each image into a PyTorch tensor.
# MNIST images become tensors with shape (1, 28, 28).
# Pixel values are converted to floating point and scaled
# to the range [0, 1].
transform = transforms.ToTensor()


# ============================================================
# 4. DOWNLOAD AND LOAD THE DATASET
# ============================================================

# Load the 60,000 MNIST training images.
# download=True downloads the data if it is not already present.
train_dataset = datasets.MNIST(
    root=DATA_DIR,
    train=True,
    download=True,
    transform=transform,
)

# Load the separate 10,000 MNIST test images.
# These images are used to evaluate the trained model.
test_dataset = datasets.MNIST(
    root=DATA_DIR,
    train=False,
    download=True,
    transform=transform,
)


# ============================================================
# 5. CREATE DATA LOADERS
# ============================================================

# Load training examples in batches of 128.
# shuffle=True changes the training-example order each epoch.
# num_workers=0 keeps data loading simple for local execution.
train_loader = DataLoader(
    train_dataset,
    batch_size=128,
    shuffle=True,
    num_workers=0,
)

# Load test examples in batches of 256.
# shuffle=False keeps evaluation order consistent.
test_loader = DataLoader(
    test_dataset,
    batch_size=256,
    shuffle=False,
    num_workers=0,
)


# ============================================================
# 6. INITIALISE THE MODEL AND TRAINING COMPONENTS
# ============================================================

# Create the network defined in src/model.py and place it
# on the selected device.
model = MNISTModel().to(device)

# Cross-entropy measures classification error.
# It is appropriate for our ten-class digit classifier.
criterion = nn.CrossEntropyLoss()

# Adam updates the model's trainable parameters using gradients.
# The learning rate controls the size of parameter updates.
optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.001,
)

# Number of complete passes through the training dataset.
EPOCHS = 5

# Start timing the training and evaluation process.
start_time = time.perf_counter()


# ============================================================
# 7. TRAIN THE MODEL
# ============================================================

for epoch in range(EPOCHS):

    # Put the model into training mode.
    model.train()

    # Accumulate the batch losses for this epoch.
    total_loss = 0.0

    # Iterate over the training dataset one batch at a time.
    for images, labels in train_loader:

        # Move the images and correct labels to the CPU.
        images = images.to(device)
        labels = labels.to(device)

        # Clear gradients left over from the previous batch.
        optimizer.zero_grad()

        # FORWARD PASS:
        # Predict ten class scores for each image.
        outputs = model(images)

        # Calculate how far the predictions are from the
        # correct digit labels.
        loss = criterion(outputs, labels)

        # BACKPROPAGATION:
        # Calculate gradients of the loss with respect
        # to the trainable model parameters.
        loss.backward()

        # PARAMETER UPDATE:
        # Use the gradients to update weights and biases.
        optimizer.step()

        # Add this batch's loss to the running total.
        # item() converts the scalar tensor to a Python number.
        total_loss += loss.item()

    # Calculate the average batch loss for this epoch.
    average_loss = total_loss / len(train_loader)

    # Display the current epoch and its average loss.
    print(
        f"Epoch {epoch + 1}/{EPOCHS} "
        f"| Average loss: {average_loss:.4f}"
    )


# ============================================================
# 8. EVALUATE THE TRAINED MODEL
# ============================================================

# Put the model into evaluation mode.
model.eval()

# Counters for correctly predicted and total examples.
correct = 0
total = 0

# Disable gradient tracking because we are not training here.
# This reduces unnecessary computation and memory usage.
with torch.no_grad():

    # Iterate over all test batches.
    for images, labels in test_loader:

        # Generate prediction scores.
        outputs = model(images)

        # Select the class index with the largest score.
        # dim=1 means we select the best class for each image.
        predictions = outputs.argmax(dim=1)

        # Compare predictions with the correct labels.
        # True values count as 1 and False values as 0.
        correct += (predictions == labels).sum().item()

        # Add the number of examples in this batch.
        total += labels.size(0)

# Accuracy is the fraction of correct predictions.
accuracy = correct / total

# Measure elapsed time since training started.
# This includes training and test evaluation.
training_seconds = time.perf_counter() - start_time


# ============================================================
# 9. SAVE THE TRAINED MODEL PARAMETERS
# ============================================================

# Define the checkpoint filename and location.
checkpoint_path = CHECKPOINT_DIR / "mnist_model.pth"

# Save the model's state dictionary.
# This contains learned parameters such as layer weights
# and biases, rather than the complete Python model class.
torch.save(model.state_dict(), checkpoint_path)


# ============================================================
# 10. COUNT MODEL PARAMETERS
# ============================================================

# numel() returns the number of elements in a tensor.
# Sum the element counts across all model parameter tensors.
parameter_count = sum(
    parameter.numel()
    for parameter in model.parameters()
)


# ============================================================
# 11. RECORD BASELINE METRICS
# ============================================================

# Store important details about this experiment.
# These values will help us evaluate compression later.
metadata = {
    "dataset": "MNIST",
    "architecture": "784-128-64-10 feed-forward network",
    "epochs": EPOCHS,
    "seed": SEED,
    "dtype": "float32",
    "parameter_count": parameter_count,
    "test_examples": total,
    "test_accuracy": accuracy,
    "test_accuracy_percent": accuracy * 100,
    "training_seconds": training_seconds,
    "checkpoint": "checkpoints/mnist_model.pth",
    "device": str(device),
}

# Save the baseline metrics in a readable JSON file.
metadata_path = CHECKPOINT_DIR / "baseline_metrics.json"

metadata_path.write_text(
    json.dumps(metadata, indent=4),
    encoding="utf-8",
)


# ============================================================
# 12. DISPLAY THE RESULTS
# ============================================================

print("\nTraining complete!")

# Display the total number of trainable parameters.
print(f"Model parameters: {parameter_count:,}")

# Display test accuracy as a percentage.
print(f"Test accuracy: {accuracy:.4%}")

# Display elapsed training and evaluation time.
print(f"Training and evaluation time: {training_seconds:.2f} seconds")

# Display where the trained model was saved.
print(f"Checkpoint: {checkpoint_path}")

# Display where baseline metrics were saved.
print(f"Baseline metadata: {metadata_path}")

# Display the size of the complete checkpoint file.
# This includes serialization overhead, not just raw parameter bytes.
print(f"Checkpoint file size: {checkpoint_path.stat().st_size:,} bytes")
