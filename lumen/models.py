from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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



LEVEL_CHOICES = (
    ("Expert", "Expert"),
    ("Intermediate", "Intermediate"),
    ("Beginner", "Beginner")
)



class Quiz(CommonInfo):

    title = models.CharField(max_length=255, unique=True)

    description = models.TextField(null=True, blank=True)

    programming_language = models.ForeignKey(ProgrammingLanguage, on_delete=models.SET_NULL, null=True)

    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='Beginner')

    is_published = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz')


    def __str__(self):
        return self.title



class Question(CommonInfo):

    text = models.CharField(max_length=1000)

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')


    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"



class Choice(CommonInfo):

    option = models.CharField(max_length=255)

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')

    is_correct = models.BooleanField(default=False)


    def __str__(self):
        return self.option



class QuizAttempt(CommonInfo):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempt')

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')

    score = models.FloatField(default=0.0)

    is_completed = models.BooleanField(default=False)


    # def calculate_score(self):
    #     total_questions = self.quiz.questions.count()
    #     if total_questions == 0:
    #         return 0
        
    #     # Count correct responses linked to this attempt
    #     correct_answers = self.responses.filter(choice__is_correct=True).count()
        
    #     # Calculation: (Correct / Total) * 100
    #     self.score = round((correct_answers / total_questions) * 100, 2)
    #     self.is_completed = True
    #     self.save()
    #     return self.score

    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - Attempt {self.id}"



class QuizResponse(CommonInfo):

    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:

        unique_together = ['attempt', 'question']


    # def clean(self):
    #     if self.choice.question != self.question:
    #         raise ValidationError("The selected choice does not belong to this question.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)








    

