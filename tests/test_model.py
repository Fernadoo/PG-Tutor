"""
Unit tests for the AI Tutoring System components.
"""

import unittest
import numpy as np
from src.bayesian_model import BayesianKnowledgeModel
from src.knowledge_graph import KnowledgeGraph, Topic
from src.teacher import AITeacher
from src.student import Student


class TestBayesianModel(unittest.TestCase):
    """Test cases for the BayesianKnowledgeModel."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model = BayesianKnowledgeModel(alpha=1.0, beta=1.0)

    def test_initial_parameters(self):
        """Test that initial parameters are set correctly."""
        self.assertEqual(self.model.alpha, 1.0)
        self.assertEqual(self.model.beta, 1.0)
        self.assertEqual(self.model.posterior_alpha, 1.0)
        self.assertEqual(self.model.posterior_beta, 1.0)

    def test_expected_lambda_initial(self):
        """Test initial expected lambda calculation."""
        expected = self.model.get_expected_lambda()
        self.assertEqual(expected, 1.0)  # alpha/beta = 1/1 = 1

    def test_update_belief(self):
        """Test Bayesian update with observations."""
        observations = np.array([1, 2, 3])
        alpha, beta = self.model.update_belief(observations)

        # Posterior should be Gamma(1+1+2+3, 1+3) = Gamma(7, 4)
        self.assertEqual(alpha, 7.0)
        self.assertEqual(beta, 4.0)

    def test_expected_lambda_after_update(self):
        """Test expected lambda after update."""
        observations = np.array([2, 3, 1])
        self.model.update_belief(observations)
        expected = self.model.get_expected_lambda()
        # After update: Gamma(1+2+3+1, 1+3) = Gamma(7, 4)
        # E[λ] = 7/4 = 1.75
        self.assertAlmostEqual(expected, 7.0/4.0, places=5)


class TestKnowledgeGraph(unittest.TestCase):
    """Test cases for the KnowledgeGraph."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.graph = KnowledgeGraph()

    def test_get_all_levels(self):
        """Test getting all difficulty levels."""
        levels = self.graph.get_all_levels()
        self.assertIn(0, levels)
        self.assertIn(1, levels)
        self.assertIn(2, levels)
        self.assertIn(3, levels)
        self.assertIn(4, levels)

    def test_get_topics_at_level(self):
        """Test getting topics at a specific level."""
        topics = self.graph.get_topics_at_level(0)
        self.assertGreater(len(topics), 0)
        for topic in topics:
            self.assertEqual(topic.level, 0)

    def test_get_random_topic_at_level(self):
        """Test getting a random topic at a level."""
        topic = self.graph.get_random_topic_at_level(1)
        self.assertIsNotNone(topic)
        self.assertEqual(topic.level, 1)

    def test_get_next_level_topics(self):
        """Test getting topics from next levels."""
        topics = self.graph.get_next_level_topics(1, max_levels_ahead=2)
        self.assertGreaterEqual(len(topics), 0)
        # All topics should be at level 2 or 3
        for topic in topics:
            self.assertIn(topic.level, [2, 3])

    def test_topic_structure(self):
        """Test that topics have expected attributes."""
        topic = self.graph.get_topic_by_name("Introduction to Algebra")
        self.assertIsNotNone(topic)
        self.assertEqual(topic.level, 0)
        self.assertEqual(topic.difficulty, 0.2)
        self.assertEqual(topic.prerequisites, [])


class TestAITeacher(unittest.TestCase):
    """Test cases for the AITeacher."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.graph = KnowledgeGraph()
        self.teacher = AITeacher(self.graph)

    def test_teacher_initialization(self):
        """Test teacher initialization."""
        self.assertIsNotNone(self.teacher.knowledge_graph)
        self.assertIsNotNone(self.teacher.bayesian_model)

    def test_observe_student_performance(self):
        """Test observing student performance."""
        topic = self.graph.get_topic_by_name("Linear Equations")
        self.teacher.observe_student_performance(topic, True)

        # Should have updated belief
        belief = self.teacher.get_current_belief()
        self.assertIsNotNone(belief)

    def test_get_next_topic(self):
        """Test getting next topic."""
        topic = self.teacher.get_next_topic(1)
        self.assertIsNotNone(topic)
        # Should be at level 2 or 3 (or possibly level 1 if no higher levels available)
        self.assertIn(topic.level, [1, 2, 3])

    def test_get_current_belief(self):
        """Test getting current belief."""
        belief = self.teacher.get_current_belief()
        self.assertIn('alpha', belief)
        self.assertIn('beta', belief)
        self.assertIn('expected_lambda', belief)


class TestStudent(unittest.TestCase):
    """Test cases for the Student."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.student = Student(true_level=2.0)

    def test_student_initialization(self):
        """Test student initialization."""
        self.assertEqual(self.student.true_level, 2.0)
        self.assertEqual(self.student.performance_variance, 0.5)

    def test_answer_question(self):
        """Test student answering a question."""
        graph = KnowledgeGraph()
        topic = graph.get_topic_by_name("Quadratic Equations")
        correct = self.student.answer_question(topic)
        # Should return boolean
        self.assertIsInstance(correct, bool)

    def test_get_accuracy(self):
        """Test getting student accuracy."""
        # Initially should be 0
        accuracy = self.student.get_accuracy()
        self.assertEqual(accuracy, 0.0)

        # After answering a few questions
        graph = KnowledgeGraph()
        topic1 = graph.get_topic_by_name("Linear Equations")
        topic2 = graph.get_topic_by_name("Quadratic Equations")

        self.student.answer_question(topic1)
        self.student.answer_question(topic2)

        accuracy = self.student.get_accuracy()
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)


if __name__ == '__main__':
    unittest.main()