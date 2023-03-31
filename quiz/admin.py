from django.contrib import admin
from .models import User, Quiz, Result


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "highest_record", "id")


class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "created_at")


class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quiz", "is_choice_correct", "created_at", "rating")


admin.site.register(User, UserAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result, ResultAdmin)
