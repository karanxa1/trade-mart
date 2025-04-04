from flask import Flask
from trade_mart.app import app as application

# This is the entry point for Vercel
app = application

# We don't need to run the app here as Vercel will handle that
# The app will be imported by Vercel's Python runtime