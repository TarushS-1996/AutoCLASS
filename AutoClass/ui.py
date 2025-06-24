from .Agent import Agent
import streamlit as st

class Agent:
    def __init__(self, pipeline: dict):
        self.pipeline = pipeline or {}
        

