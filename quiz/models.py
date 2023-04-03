from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=32, unique=True)
    score = models.IntegerField(default=0)
    life = models.IntegerField(default=3)
    highest_record = models.IntegerField(default=0)
    highest_record_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.username


class Movie(models.Model):
    title = models.TextField()

    def __str__(self):
        return self.title


class Prompt(models.Model):
    type = models.CharField(max_length=16)
    prompt = models.TextField()

    def __str__(self):
        return f"Type: {self.type}, Prompt: {self.prompt[:25]}"


class Quiz(models.Model):
    id = models.CharField(primary_key=True, default='00000000', max_length=8, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_titles')
    question = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    answer = models.CharField(max_length=1)
    explanation = models.TextField()
    imdb_url = models.URLField()

    def __str__(self):
        return f"[{self.id}] {self.question[:50]}"


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='user_results')
    is_choice_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(null=True, blank=False)

    class Meta:
        unique_together = ('user', 'quiz')

    def __str__(self):
        return f"{self.user.username}'s result on quiz [{self.quiz.id}]"
