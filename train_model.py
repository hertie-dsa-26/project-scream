"""Run this once before starting Flask to train and save the logistic regression model.

Usage:
    uv run python train_model.py
"""
from app.model.logit import train_and_save

if __name__ == "__main__":
    train_and_save()
