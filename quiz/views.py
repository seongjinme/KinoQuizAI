from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

import json
import openai
import os
import re
import string

from dotenv import load_dotenv
from secrets import choice, randbelow
from supabase import create_client
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .models import User, Quiz, Result, Prompt


def home_view(request):
    return render(request, "home.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_path = request.POST.get("next") or None
            if next_path:
                return redirect(next_path)
            return redirect("kinoquizai:home")
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })

    else:
        next_path = request.GET.get("next") or request.META.get("HTTP_REFERER")
        return render(request, "login.html", {
            "next": next_path
        })


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect("kinoquizai:home")
    logout(request)
    return redirect(request.path)


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Allow only up to 16 alphanumeric + hyphen + underscore characters to username
        if not (re.match(r"^[A-Za-z0-9_-]+$", username) and len(username) <= 16):
            return render(request, "register.html", {
                "message": "Only up to 16 alphanumeric characters, hyphen and underscore are allowed to username."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })

        # After creating new user, allow login to the app and redirect to home
        login(request, user)
        return redirect("kinoquizai:home")

    else:
        return render(request, "register.html")


@login_required
def quiz_view(request):
    user = get_object_or_404(User, id=request.user.id)

    # Reset user's current score everytime when user starts playing
    user.score = 0
    user.save()

    return render(request, "quiz.html", {
        "user": user
    })


def leaderboard_view(request):
    all_users_by_ranking = User.objects.filter(highest_record__gt=0)\
        .annotate(rank=Window(expression=Rank(), order_by="-highest_record"))
    top_10_users = all_users_by_ranking[:10]

    try:
        user = User.objects.get(id=request.user.id)
        # Currently filtering against window function doesn't keep the values annotated in the queryset.
        # In the upcoming Django 4.2, filtering against window functions will be available
        # which likely makes the task finding user's current rank more efficient.
        # https://github.com/django/django/pull/15922
        # https://github.com/django/django/blob/main/docs/releases/4.2.txt
        user_rank = 0
        for user_by_ranking in all_users_by_ranking:
            if user_by_ranking.id == user.id:
                user_rank = user_by_ranking.rank
    except User.DoesNotExist:
        user = user_rank = None

    if request.user.is_authenticated and user and user_rank:
        return render(request, "leaderboard.html", {
            "user": user,
            "user_rank": user_rank,
            "top_10_users": top_10_users
        })

    return render(request, "leaderboard.html", {
        "top_10_users": top_10_users
    })


def get_prompt():

    # Get a prompt to make a request
    try:
        prompt_query = Prompt.objects.get(type="query").prompt
    except Prompt.DoesNotExist:
        prompt_query = set_prompt(type="query")

    # To produce the data in the desired format or topic, add a random sample quiz template as an example
    prompt_samples = Prompt.objects.filter(type="sample")
    if prompt_samples.count() > 0:
        prompt_sample = prompt_samples[randbelow(prompt_samples.count())].prompt
    else:
        prompt_sample = set_prompt(type="sample")

    # If there was a problem retrieving prompts, return None
    if not (prompt_query or prompt_sample):
        return None

    # Combine templates to generate the prompt to get a new quiz from Completions/Chat API
    return prompt_query + prompt_sample + "\n\n[Question]"


def set_prompt(type):

    load_dotenv()

    # Connect to Supabase Storage
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    client = create_client(url, key)
    bucket = client.storage.get_bucket(os.environ.get("SUPABASE_BUCKET_PROMPTS"))

    # Get the main query prompt
    if type == "query":

        prompt_query_file = bucket.download("quiz.txt")
        prompt_query_content = prompt_query_file.decode("utf-8")
        prompt_query = Prompt(
            type="query",
            prompt=prompt_query_content
        )
        prompt_query.save()

        return prompt_query_content

    # Get the sample question prompts
    if type == "sample":

        prompt_sample_files = bucket.list("samples/")

        for filename in prompt_sample_files:
            prompt_sample_file = bucket.download(f"samples/{filename['name']}")
            prompt_sample_content = prompt_sample_file.decode("utf-8")
            prompt_sample = Prompt(
                type="sample",
                prompt=prompt_sample_content
            )
            prompt_sample.save()

        prompt_samples = Prompt.objects.filter(type="sample")
        idx = randbelow(prompt_samples.count())
        return prompt_samples[idx].prompt

    return None


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5), reraise=True)
def get_response_from_gpt(prompt, chatapi=True):

    if not prompt:
        print("There was a problem retrieving the prompt. Aborted the process.")
        return None

    load_dotenv()
    openai.organization = str(os.environ.get("OPENAI_ORGANIZATION"))
    openai.api_key = str(os.environ.get("OPENAI_API_KEY"))

    # Preset the parameters for Completions/Chat API
    # To check descriptions for each parameter, visit https://platform.openai.com/docs/api-reference/completions
    parameters = {
        "temperature": 1.15,
        "top_p": 0.7,
        "frequency_penalty": 1,
        "presence_penalty": 0.85,
        "max_tokens": 2048
    }

    print("Start getting a response from OpenAI API...")

    try:
        # If chatapi is True, use ChatCompletion mode with gpt-3.5-turbo model
        if chatapi:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Suppose you are an examiner in the movie lecture class."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=parameters["temperature"],
                top_p=parameters["top_p"],
                frequency_penalty=parameters["frequency_penalty"],
                presence_penalty=parameters["presence_penalty"],
                max_tokens=parameters["max_tokens"]
            )

            return response['choices'][0]['message']['content'].strip()

        # If not, use Completion mode with text-davinci-003 model
        else:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Suppose you are an examiner in the movie lecture class.\n" + prompt,
                temperature=parameters["temperature"],
                top_p=parameters["top_p"],
                frequency_penalty=parameters["frequency_penalty"],
                presence_penalty=parameters["presence_penalty"],
                max_tokens=parameters["max_tokens"]
            )

            # In text-davinci-003 model, the requested data comes with the first 2 line-breaks.
            # I used the slicing([2:]) to remove the line-breaks at the start.
            return response["choices"][0]["text"][2:].strip()

    except NameError as e:
        print(f"Wrong OpenAI API key & organization ID values in environment file: {e}")
        return None

    except openai.error.APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        return None

    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return None

    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return None


@ensure_csrf_cookie
def get_quiz(request):

    # Return error message if the user has not logged in
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "You must be logged in to get a quiz."
        }, status=403)

    # Get the user object
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({
            "error": "You must be registered to get a quiz."
        }, status=404)

    # Return error message if the request method is not POST
    if request.method != "POST":
        return JsonResponse({
            "error": "Your request method is invalid."
        }, status=405)

    # Get the queryset contains quizzes the user hasn't solved before
    quiz_set = Quiz.objects.exclude(user_results__user=user)

    # If the queryset has one or more quizzes, return one of it
    if quiz_set:
        quiz = quiz_set.all()[randbelow(quiz_set.count())]

    # If not, generate new quiz
    else:
        quiz = generate_quiz()
        # If generating process has failed, return error message with retry signal
        if quiz is None:
            return JsonResponse({
                "error": "An error occurred during generating a quiz from ChatGPT. Please try again later.",
                "message": "There was a temporary problem during getting a quiz. Please try again later.",
                "retry_generate": True
            }, status=429)

    return JsonResponse({
        "quiz": {
            "quiz_id": quiz.id,
            "question": quiz.question,
            "option_a": quiz.option_a,
            "option_b": quiz.option_b,
            "option_c": quiz.option_c,
            "option_d": quiz.option_d
        }
    }, status=200)


def generate_quiz():
    prompt = get_prompt()
    content = get_response_from_gpt(prompt, chatapi=True)

    if not content:
        return None
    print("Received quiz data from OpenAI API. Now processing the data...")

    items = [item for item in content.splitlines() if item]
    if len(items) != 8:
        print("Validating the received quiz has failed. Rejecting...")
        return None

    if len(items[5]) > 1:
        items[5] = items[5][-1]

    new_quiz_id = save_quiz_data(items)
    if not new_quiz_id:
        return None

    print(f"Received quiz is ready to be served to users! (ID: {new_quiz_id})")
    return Quiz.objects.get(id=new_quiz_id)


def save_quiz_data(items):
    quiz_id = create_quiz_id()

    try:
        quiz = Quiz(
            id=quiz_id,
            question=items[0].strip(),
            option_a=items[1].strip(),
            option_b=items[2].strip(),
            option_c=items[3].strip(),
            option_d=items[4].strip(),
            answer=items[5].strip().upper(),
            explanation=items[6].strip(),
            imdb_url=items[7].strip()
        )
        quiz.save()
    except IntegrityError:
        print("IntegrityError occurred during saving new quiz data:")
        print(items)
        return None

    return quiz_id


@ensure_csrf_cookie
def get_result(request, quiz_id):

    # Return error message if the user has not logged in
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "You must be logged in to get a quiz."
        }, status=403)

    # Return error message if the request method is not POST
    if request.method != "POST":
        return JsonResponse({
            "error": "Your request method is invalid."
        }, status=405)

    # Get the user object
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({
            "error": "You must be registered to get the result."
        }, status=404)

    # Get the quiz object with quiz_id
    try:
        quiz = Quiz.objects.exclude(user_results__user=user).get(id=quiz_id)
    except Quiz.DoesNotExist:
        return JsonResponse({
            "error": "Your requested quiz data has not found."
        }, status=404)

    # Get the input data and cleanse it
    user_choice = json.loads(request.body).get("choice", "")
    user_choice = user_choice.strip().upper() if user_choice else None

    # Validate the input data. If the data is not A~D, return error message
    if user_choice not in ["A", "B", "C", "D", None]:
        return JsonResponse({
            "error": "Invalid input data.",
            "message": "The data contains your choice has corrupted. \
            Please try again, or refresh your browser and start again."
        }, status=400)

    # Check and save the result
    is_user_choice_correct = check_and_save_quiz_result(quiz, user, user_choice)
    score = user.score
    highest_record = user.highest_record

    # Check if user's current score exceeds the user's highest record
    is_new_record = True if score > highest_record else False

    # If user got the new record, save it to User model
    if is_new_record:
        user.highest_record = score
        user.highest_record_at = timezone.now()
        user.save()

    return JsonResponse({
        "quiz_result": {
            "is_user_choice_correct": is_user_choice_correct,
            "answer": quiz.answer,
            "explanation": quiz.explanation,
            "imdb_url": quiz.imdb_url
        },
        "user_status": {
            "score": score,
            "highest_record": highest_record,
            "is_new_record": is_new_record
        }
    }, status=200)


def check_and_save_quiz_result(quiz, user, user_choice):
    # Check if user's choice is right
    result = True if quiz.answer == user_choice else False

    # Save the result to DB
    quiz.user_results.create(
        user=user,
        quiz=quiz,
        is_choice_correct=result
    )

    # If user's choice is right, add a score to the user
    if result is True:
        user.score += 1
        user.save()

    return result


def create_quiz_id(size=8, chars=string.ascii_letters):
    while True:
        quiz_id = "".join([choice(chars) for _ in range(size)])
        if not Quiz.objects.filter(id=quiz_id).exists():
            break
    return quiz_id


@ensure_csrf_cookie
def save_quiz_user_rating(request, quiz_id):

    # Return error message if the user has not logged in
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "You must be logged in to give a rating to the quiz."
        }, status=403)

    # Return error message if the request method is not PATCH
    if request.method != "PATCH":
        return JsonResponse({
            "error": "Your request method is invalid."
        }, status=405)

    # Get the objects to precess
    try:
        user = User.objects.get(id=request.user.id)
        quiz = Quiz.objects.get(id=quiz_id)
        result = Result.objects.get(user=user, quiz=quiz)
    except User.DoesNotExist:
        return JsonResponse({
            "error": "Your user info has not found."
        }, status=404)
    except Quiz.DoesNotExist:
        return JsonResponse({
            "error": "Your requested quiz data has not found."
        }, status=404)
    except Result.DoesNotExist:
        return JsonResponse({
            "error": "Your requested result data has not found."
        }, status=404)

    # Get the input data and cleanse it
    user_rating = json.loads(request.body).get("rating", "")
    user_rating_result = "Good" if user_rating else "Bad"

    # Add user rating info to Result model
    result.rating = 1 if user_rating else -1
    result.save()

    return JsonResponse({
        "rating_result": {
            "user_rating": user_rating_result,
        }
    }, status=200)
