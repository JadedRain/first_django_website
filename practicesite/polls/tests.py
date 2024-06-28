import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice

def create_question(question_text, days):
    """
    Create a question with the give 'question_text and published the given number of 'days' offset to now
    (negative for quesitons published in the past, positive for questions yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(choice_text, question_id):
    return Choice.objects.create(choice_text=choice_text, question_id=question_id)
    
class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
        
    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page
        """
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Questions with a pub_date in the future are not displayed on the index page
        """
        question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
        
    def test_past_and_future_questions(self):
        """
        Even if there are questions from the past and future only the questions from the past should be shown
        on the index page
        """
        question = create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertIs(Question.objects.all().count(), 2)
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])
    
    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions
        """
        question1 = create_question(question_text="Question 1", days=-30)
        question2 = create_question(question_text="Question 2", days=-15)
        response = self.client.get(reverse("polls:index"))
        # responses ordered with most recent being at index 0
        self.assertQuerySetEqual(response.context["latest_question_list"], [question2, question1])
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found.
        """
        future_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:detail", args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past displays the questions text
        """
        past_question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The result view of a question with a pub_date in the future shouldn't display
        """
        future_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:results", args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        The result view of a question with a pub_date in the past should display
        """
        past_question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:results", args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)

class QuestionModelTests(TestCase):
    def test_was_published_recent_with_future_question(self):
        """
        was_published_recent() returns False for question whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recent(), False)
    def test_was_published_recent_with_old_question(self):
        """
        was_published_recent() returns False for questions whose pub_date is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recent(), False)
    def test_was_published_recent_with_recent_question(self):
        """
        was_published_recent() returns True for questions whose pub_date is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recent(), True)
        
    def test_get_choices_count(self):
        """
        get_choices_count() returns an integer value for the number of choices the question has
        """
        question = create_question("Test question", 0)
        create_choice("Choice 1", question.id)
        create_choice("Choice 2", question.id)
        self.assertIs(question.choices_count(), 2)
    