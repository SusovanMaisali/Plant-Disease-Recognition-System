from datasets import load_dataset

print("Loading dataset...")

dataset = load_dataset("mohanty/PlantVillage", "default")

print(dataset)

print("\nFirst sample:\n")

print(dataset["train"][0])