# KinoQuizAI
## Introduction
![cover](https://user-images.githubusercontent.com/73219583/228546421-b0fb336e-f977-4be1-8a02-e5566bacbe7b.png)
**KinoQuizAI** is a **web application that offers AI-generated movie quizzes** powered by **ChatGPT API**. 

Users can test their knowledge of movies from various genres and time periods by playing random quizzes and earning scores. They can also compete with other users on the leaderboard and see how they rank among movie enthusiasts. KinoQuizAI is a fun and convenient way to challenge yourself and learn more about movies.

The app was originally developed as the capstone project of [Harvard's CS50’s Web Programming with Python and JavaScript](https://cs50.harvard.edu/web/2020/) course, but it has been updated and enhanced since then to provide a more enjoyable and user-friendly experience. The app features:

* A collection of movie quizzes generated by ChatGPT based on 300 films from 1996 to 2021 that have received more than 200,000 ratings on the IMDB Top 250 list.
* A simple and intuitive interface that allows you to answer single-choice questions and get instant feedback.
* A scoring system that rewards correct answers with 1 point and penalizes wrong answers with 1 heart loss. You start each game with 3 hearts and the game ends when you run out of hearts.
* A leaderboard that displays the top scores of all users who have played the game.

## Distinctiveness and Complexity
This application follows all expectations mentioned in the [CS50W Capstone project requirements](https://cs50.harvard.edu/web/2020/projects/final/capstone/#requirements). Detailed descriptions are below:

> Your web application must be sufficiently distinct from the other projects in this course (and, in addition, may not be based on the old CS50W Pizza project), and more complex than those.

My project, KinoQuizAI, is a quiz game app that differs from any other projects offered in CS50W courses. (It has no resemblance to the old CS50W Pizza project either.)

The app allows users to play movie quizzes generated by ChatGPT, check the answers and explanations, and compete with other users by scoring points for consecutive correct answers. These features are intuitive and simple, but they require a lot of complexity on both the back-end and front-end to create a seamless user experience.

By using the ChatGPT API, the app can theoretically provide new movie quizzes that are never repeated. However, the main function of LLMs (Large Language Models) like GPT is to predict the next text based on a given prompt. This means that ChatGPT may not always produce the data in the desired format or topic.

To minimize this problem and to maintain the consistency and quality of the generated quiz data, my project implements several data-handling functions on the back-end: sending a well-designed prompt with fine-tuned parameters to the third-party API, receiving the real-time generated data, validating and preprocessing the data, saving it to DB, and adding a retry mechanism for cases where fetching the data fails.

Additionally, to optimize the user experience and reduce the server costs, I have implemented a smart system that minimizes the number of requests to ChatGPT API. The system works as follows: when a new user signs up for KinoQuizAI, they will first have access to quizzes that have been previously created by other users and stored in the DB. This way, they can enjoy quizzes without waiting for ChatGPT to generate them. Once a user has completed all the quizzes available in the DB, they will receive new quizzes from ChatGPT in real-time. These new quizzes will also be stored in the DB for future use by other users.

To ensure a seamless and dynamic interface for the quiz playing screen, I have used JavaScript to manipulate the document structure according to the responses from the back-end side. By using `fetch` API in JavaScript, this app can request and receive data asynchronously while the user is playing the quiz. If the data is successfully received, the quiz page will be updated dynamically without reloading. This enhances the usability and interactivity of the app.

> Your web application must utilize Django (including at least one model) on the back-end and JavaScript on the front-end.

KinoQuizAI uses the Django framework for its back-end development. It has three models that store and manipulate data: 
* `User` - which represents the registered users of the app.
* `Quiz` - which contains the questions and answers for each quiz.
* `Result` - which records each user's quiz attempt. 

The front-end of the app relies on JavaScript to provide a dynamic and interactive user interface. In particular, the `/quiz/` route allows users to take quizzes, submit their responses, and view the explanations without reloading or navigating to another page.

> Your web application must be mobile-responsive.

This project utilizes [Tailwind CSS](https://tailwindcss.com/). By applying various classes provided by Tailwind CSS, this project has achieved full mobile responsiveness. This means that the web application can adapt to different screen sizes and devices.

## Screenshots

* Playing Quiz
![quiz_playing](https://user-images.githubusercontent.com/73219583/228549715-cad71dfc-cef1-4ac5-bbce-6bb42cf2f72c.png)

* Getting Result
![quiz_result](https://user-images.githubusercontent.com/73219583/228549880-a78f9d64-8c3a-4cb5-a155-8e27d80c50b6.png)

* Leaderboard
![leaderboard](https://user-images.githubusercontent.com/73219583/228549968-dae1d31b-64e9-4d6a-912f-a02b856be8a3.png)
