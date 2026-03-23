"""论文生成智能体"""
from .base import BaseAgent
from .abstract_agent import AbstractAgent
from .introduction_agent import IntroductionAgent
from .content_agent import ContentAgent
from .conclusion_agent import ConclusionAgent
from .references_agent import ReferencesAgent
from .corrector_agent import CorrectorAgent

__all__ = [
    "BaseAgent",
    "AbstractAgent",
    "IntroductionAgent",
    "ContentAgent",
    "ConclusionAgent",
    "ReferencesAgent",
    "CorrectorAgent",
]
