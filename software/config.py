import os

class Config:
    SECRET_KEY = 'your-secret-key-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False