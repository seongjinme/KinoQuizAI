from django.contrib import admin
from .models import User, Movie, Quiz, Result, Prompt


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "highest_record", "id")


class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "created_at")


class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quiz", "is_choice_correct", "created_at", "feedback")


class PromptAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "prompt")


admin.site.register(User, UserAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Prompt, PromptAdmin)
