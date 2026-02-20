from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction


class User(AbstractUser):

    phone = models.CharField(max_length=15, unique=True)


class CommonInfo(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        abstract = True


class ProgrammingLanguage(CommonInfo):

    name = models.CharField(max_length=255)


    def __str__(self):
        return self.name



class Quiz(CommonInfo):

    LEVEL_CHOICES = (
    ("Expert", "Expert"),
    ("Intermediate", "Intermediate"),
    ("Beginner", "Beginner")
    )

    title = models.CharField(max_length=255, unique=True)

    description = models.TextField(null=True, blank=True)

    programming_language = models.ForeignKey(ProgrammingLanguage, on_delete=models.SET_NULL, null=True)

    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='Beginner')

    duration_minutes = models.PositiveIntegerField(default=30, help_text="Time limit in minutes")

    is_published = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz')


    def __str__(self):
        return self.title



class Question(CommonInfo):

    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
    )

    text = models.CharField(max_length=1000)

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')

    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')

    points = models.PositiveIntegerField(default=1, help_text="Points awarded for a correct answer")


    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"



class Choice(CommonInfo):

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')

    option = models.CharField(max_length=255)

    is_correct = models.BooleanField(default=False)


    def __str__(self):
        return self.option



class QuizAttempt(CommonInfo):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempt')

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')

    score = models.FloatField(default=0.0)

    start_time = models.DateTimeField(auto_now_add=True)

    end_time = models.DateTimeField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)


    @property
    def is_expired(self):
        """Checks if the user has run out of time based on Quiz.duration_minutes"""
        if not self.start_time:
            return False
        expiry_time = self.start_time + timezone.timedelta(minutes=self.quiz.duration_minutes)
        return timezone.now() > expiry_time


    # @transaction.atomic
    # def calculate_final_score(self):
    #     total_possible_points = 0
    #     earned_points = 0
        
    #     # Get all questions in this quiz
    #     quiz_questions = self.quiz.questions.all()
    #     total_possible_points = sum(q.points for q in quiz_questions)
        
    #     # Get all responses for this attempt
    #     responses = self.responses.prefetch_related('selected_choices')
        
    #     for resp in responses:
    #         question = resp.question
            
    #         # Get IDs of correct choices for this question
    #         correct_choice_ids = set(
    #             question.choices.filter(is_correct=True).values_list('id', flat=True)
    #         )
            
    #         # Get IDs of choices the user actually selected
    #         selected_ids = set(
    #             resp.selected_choices.values_list('id', flat=True)
    #         )
            
    #         # Logic: Sets must match exactly
    #         if selected_ids == correct_choice_ids and len(correct_choice_ids) > 0:
    #             earned_points += question.points

    #     # Calculate percentage
    #     if total_possible_points > 0:
    #         self.score = round((earned_points / total_possible_points) * 100, 2)
    #     else:
    #         self.score = 0
            
    #     self.is_completed = True
    #     self.end_time = timezone.now()
    #     self.save()
    #     return self.score

    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Attempt {self.id}"



class QuizResponse(CommonInfo):

    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_choices = models.ManyToManyField(Choice)


    class Meta:

        unique_together = ['attempt', 'question']


    # def clean(self):
    #     if self.choice.question != self.question:
    #         raise ValidationError("The selected choice does not belong to this question.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)








    

