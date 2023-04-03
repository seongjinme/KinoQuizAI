document.addEventListener("DOMContentLoaded", function() { get_quiz(); });
let QUIZ_SUBMITTED = false;


function get_quiz() {

    const csrftoken = get_cookie('csrftoken');

    fetch(`/api/quiz/create`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        mode: 'same-origin',
        body: JSON.stringify({})
    })
        .then(response => {
            if (!response.ok) {
                console.log('Fetch error occurred.');

                // If fetching new quiz has failed, let user know it and guide to retry fetching it
                fill_error_message();
                throw new Error(response.statusText);
            }
            return response.json()
        })
        .then(content => {
            if (content.error || content.message) {
                console.log(content.error || content.message)
            }
            setTimeout(() => {
                fill_quiz_content(content);
            }, 500);
        })
        .catch(error => {
            console.log(error);
        })

}


function fill_error_message() {

    const quiz_status_message = document.querySelector(`#quiz-status-message`);
    const quiz_question = document.querySelector(`#quiz-question`);
    const quiz_result_container = document.querySelector(`#quiz-result-container`);

    quiz_status_message.textContent = 'An error occurred...';
    quiz_question.innerHTML = 'There was a temporarily problem during getting a quiz. Please try again later.';
    quiz_result_container.innerHTML = `
        <button type="button" id="get-quiz-retry-button"
            class="w-full rounded-md p-3 text-base sm:text-lg font-semibold text-white enabled:bg-gradient-to-r from-teal-500 to-blue-500 enabled:hover:scale-105 enabled:focus:scale-105 disabled:bg-slate-300 drop-shadow-sm ease-in-out duration-300"
            onclick="get_quiz_retry();">
            Get a Quiz Again
        </button>
    `;

}


function get_quiz_retry() {

    const quiz_question = document.querySelector(`#quiz-question`);
    const quiz_result_container = document.querySelector(`#quiz-result-container`);

    quiz_question.innerHTML = `
        <div class="animate-pulse flex space-x-4">
            <div class="flex-1 space-y-5 py-1">
                <div id="quiz-status-message" class="col-span-3 text-sm text-slate-400 animate-pulse">Fetching new quiz...</div>
                <div class="h-2 bg-slate-300 rounded"></div>
                <div class="grid grid-cols-3 gap-4">
                    <div class="h-2 bg-slate-200 rounded col-span-1"></div>
                    <div class="h-2 bg-slate-200 rounded col-span-2"></div>
                </div>
                <div class="grid grid-cols-5">
                    <div class="h-2 bg-slate-300 rounded col-span-3"></div>
                </div>
            </div>
        </div>
    `;

    quiz_result_container.innerHTML = `
        <button type="button" id="quiz-choice-submit-button"
            class="w-full rounded-md p-3 text-base sm:text-lg font-semibold text-white enabled:bg-gradient-to-r from-teal-500 to-blue-500 enabled:hover:scale-105 enabled:focus:scale-105 disabled:bg-slate-300 drop-shadow-sm ease-in-out duration-300"
            disabled>
            Submit
        </button>
    `;

    get_quiz();

}


function fill_quiz_content(content) {

    const quiz_question = document.querySelector(`#quiz-question`);
    const quiz_options = document.querySelectorAll(`ul#quiz-option-list > li > input`);
    const quiz_option_A_label = document.querySelector(`#quiz-option-A-label`);
    const quiz_option_B_label = document.querySelector(`#quiz-option-B-label`);
    const quiz_option_C_label = document.querySelector(`#quiz-option-C-label`);
    const quiz_option_D_label = document.querySelector(`#quiz-option-D-label`);
    const quiz_choice_submit_button = document.querySelector(`#quiz-choice-submit-button`);

    // Fill the question
    quiz_question.innerHTML = content['quiz']['question'];

    // Fill and enable the radio select buttons
    quiz_option_A_label.textContent = `(A) ${content['quiz']['option_a']}`;
    quiz_option_B_label.textContent = `(B) ${content['quiz']['option_b']}`;
    quiz_option_C_label.textContent = `(C) ${content['quiz']['option_c']}`;
    quiz_option_D_label.textContent = `(D) ${content['quiz']['option_d']}`;

    for (let i = 0; i < quiz_options.length; i++) {
        quiz_options[i].value = content['quiz']['option_values'][i]
        quiz_options[i].disabled = false;
        quiz_options[i].checked = false;
    }

    // Enable the submit button
    quiz_choice_submit_button.setAttribute('onclick', `submit_quiz_option_choice('${content['quiz']['quiz_id']}');`)
    quiz_choice_submit_button.disabled = false;

    // Start timer and let the user solve the question
    start_quiz_timeout(content['quiz']['quiz_id']);

}


function start_quiz_timeout(quiz_id) {

    const quiz_timeout_bar = document.querySelector(`#quiz-timeout-bar`);
    quiz_timeout_bar.style.width = '100%';

    let quiz_timeout_bar_width = 100
    const animate = () => {
        quiz_timeout_bar_width--;
        quiz_timeout_bar.style.width = `${quiz_timeout_bar_width}%`;
    }

    setTimeout(() => {
        let interval = setInterval(() => {
            if (quiz_timeout_bar_width === 0) {
                clearInterval(interval);
                // If user didn't submit the choice until time ran out, submit null
                submit_quiz_option_choice(quiz_id);
            }
            else if (QUIZ_SUBMITTED === true) {
                clearInterval(interval);
            }
            else {
                animate();
            }
        }, 150);
    }, 500);

}


function submit_quiz_option_choice(quiz_id) {

    const quiz_options = document.querySelectorAll(`ul#quiz-option-list > li > input`);
    const quiz_choice_submit_button = document.querySelector(`#quiz-choice-submit-button`);

    for (let i = 0; i < quiz_options.length; i++) {
        quiz_options[i].disabled = true;
    }

    quiz_choice_submit_button.disabled = true;
    const checked = document.querySelector(`input[name='quiz-option']:checked`);
    const choice = checked ? checked.value : null;

    QUIZ_SUBMITTED = true;

    get_result(quiz_id, choice)

}


function get_result(quiz_id, choice) {

    const csrftoken = get_cookie('csrftoken');

    fetch(`/api/quiz/${quiz_id}/result`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        mode: 'same-origin',
        body: JSON.stringify({ choice })
    })
        .then(response => {
            if (!response.ok) {
                console.log('Fetch error occurred.');
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then(result => {
            if (result.error || result.message) {
                console.log(result.error || result.message)
            }

            setTimeout(() => {
                clear_quiz_content(result['quiz_result']['answer']);
                fill_quiz_result(result);
            }, 1000);

        })
        .catch(error => {
            console.error(error);
        });

}


function clear_quiz_content(answer) {

    const quiz_options = document.querySelectorAll(`ul#quiz-option-list > li > input`);
    const quiz_choice_submit_button = document.querySelector(`#quiz-choice-submit-button`);

    for (let i = 0; i < quiz_options.length; i++) {
        if (quiz_options[i].value !== answer && !quiz_options[i].checked) {
            quiz_options[i].parentElement.remove();
        }
        else if (quiz_options[i].value === answer) {
            quiz_options[i].parentElement.lastElementChild.className = 'block px-6 py-3 mt-1.5 font-semibold text-green-600 bg-neutral-50 border border-green-600 rounded-md cursor-pointer answer';
        }
        else {
            quiz_options[i].parentElement.lastElementChild.className = 'block px-6 py-3 mt-1.5 font-medium text-rose-600 bg-neutral-50 border rounded-md cursor-pointer';
        }
    }

    quiz_choice_submit_button.remove();

}


function fill_quiz_result(result) {

    let quiz_result_div;
    let quiz_next_interface_div = document.createElement('div');
    quiz_next_interface_div.className = 'flex items-center justify-between';
    quiz_next_interface_div.id = 'quiz-next-interface-div';

    const quiz_option_answer = document.querySelector('ul#quiz-option-list > li > label[class~="answer"]').textContent[1];

    if (result['quiz_result']['is_user_choice_correct']) {
        quiz_result_div = `
            <div id="quiz-result" class="bg-green-100 p-3 text-sm sm:text-base font-semibold text-green-600 text-center border border-green-600 drop-shadow-sm rounded-md">
                Great! The answer is (${quiz_option_answer}).
            </div>
        `;
    }
    else {
        quiz_result_div = `
            <div id="quiz-result" class="bg-rose-100 p-3 text-sm sm:text-base font-semibold text-rose-600 text-center border border-rose-600 drop-shadow-sm rounded-md">
                How unfortunate! The answer is (${quiz_option_answer}).
            </div>
        `;
    }

    if (result['user_status']['game_continue']) {
        quiz_next_interface_div.innerHTML = `
            <button type="button" id="quiz-result-continue-button"
                class="block rounded-md w-full py-3 px-5 text-sm sm:text-base font-semibold text-white bg-gradient-to-r from-teal-500 to-blue-500 hover:scale-105 focus:scale-105 drop-shadow-sm ease-in-out duration-300"
                onclick="continue_play_quiz();">
                Next Quiz
            </button>
        `;
    }
    else {
        quiz_next_interface_div.innerHTML = `
            <a type="button" id="quiz-result-restart-button"
                class="rounded-md py-3 px-4 text-sm sm:text-base font-semibold text-white bg-gradient-to-r from-teal-500 to-blue-500 hover:scale-105 focus:scale-105 drop-shadow-sm ease-in-out duration-300"
                href="/quiz/">
                Restart Game
            </a>
            <a type="button" id="quiz-result-leaderboard-button"
                class="rounded-md py-3 px-4 text-sm sm:text-base font-normal text-white bg-slate-400 hover:scale-105 focus:scale-105 drop-shadow-sm ease-in-out duration-300"
                href="/">
                Back to Home
            </a>
        `;
    }

    const quiz_status_score = document.querySelector(`#quiz-status-score`);
    quiz_status_score.textContent = result['user_status']['score'];

    const quiz_user_life = document.querySelector(`#quiz-user-life`);
    if (result['user_status']['life'] === 3) {
        quiz_user_life.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-rose-600" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-rose-600" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-rose-600" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg>
        `;
    }
    else if (result['user_status']['life'] === 2) {
        quiz_user_life.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-slate-300" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-rose-600" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-rose-600" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg>
        `;
    }
    else if (result['user_status']['life'] === 1) {
        quiz_user_life.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-slate-300" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-slate-300" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-heart-fill inline-block fill-rose-600" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg>
        `;
    }
    else {
        quiz_user_life.innerHTML = `
            <p class="text-sm text-slate-400 animate-pulse">Game over...</p>
        `;
    }

    const quiz_explanation_div = `
        <div id="quiz-explanation" class="text-base select-none text-slate-500 px-6 py-4 sm:text-lg sm:py-6 w-full h-full bg-neutral-50 border border-slate-300 rounded-md drop-shadow-sm">
            <p>${result['quiz_result']['explanation']}</p>
            <a class="inline-block pt-3 text-sm sm:text-base text-blue-500 hover:text-blue-600" href="${result['quiz_result']['imdb_url']}" target="_blank">${result['quiz_result']['imdb_url']}</a>
        </div>
    `;

    const quiz_result_container = document.querySelector(`#quiz-result-container`);
    quiz_result_container.innerHTML = `
        ${quiz_result_div}
        ${quiz_explanation_div}
    `;
    quiz_result_container.parentElement.appendChild(quiz_next_interface_div);

}


function continue_play_quiz() {

    reset_quiz_content();
    setTimeout(() => {
        get_quiz();
    }, 1000);

}


function reset_quiz_content() {

    const quiz_question = document.querySelector(`#quiz-question`);
    const quiz_timeout_bar = document.querySelector(`#quiz-timeout-bar`);
    const quiz_option_list = document.querySelector(`ul#quiz-option-list`);
    const quiz_result_container = document.querySelector(`#quiz-result-container`);
    const quiz_next_interface_div = document.querySelector(`#quiz-next-interface-div`);

    quiz_question.innerHTML = `
        <div class="animate-pulse flex space-x-4">
            <div class="flex-1 space-y-5 py-1">
                <div id="quiz-status-message" class="col-span-3 text-sm text-slate-400 animate-pulse">Fetching new quiz...</div>
                <div class="h-2 bg-slate-300 rounded"></div>
                <div class="grid grid-cols-3 gap-4">
                    <div class="h-2 bg-slate-200 rounded col-span-1"></div>
                    <div class="h-2 bg-slate-200 rounded col-span-2"></div>
                </div>
                <div class="grid grid-cols-5">
                    <div class="h-2 bg-slate-300 rounded col-span-3"></div>
                </div>
            </div>
        </div>
    `;
    quiz_timeout_bar.style.width = '0';
    quiz_option_list.innerHTML = `
        <li>
            <input type="radio" id="quiz-option-A" name="quiz-option" value="A" class="hidden peer" disabled>
            <label for="quiz-option-A" id="quiz-option-A-label" class="block px-6 py-3 mt-1.5 font-normal text-slate-500 bg-neutral-50 border border-slate-200 rounded-md cursor-pointer peer-checked:border-blue-500 peer-checked:text-blue-500 peer-checked:font-semibold hover:text-gray-600 hover:bg-gray-100">
              <div class="animate-pulse flex space-x-4">
                <div class="flex-1 space-y-5 py-1 grid grid-cols-5">
                  <div class="h-2 bg-slate-200 rounded col-span-4"></div>
                </div>
              </div>
            </label>
          </li>
          <li>
            <input type="radio" id="quiz-option-B" name="quiz-option" value="B" class="hidden peer" disabled>
            <label for="quiz-option-B" id="quiz-option-B-label" class="block px-6 py-3 mt-1.5 font-normal text-slate-500 bg-neutral-50 border border-slate-200 rounded-md cursor-pointer peer-checked:border-blue-500 peer-checked:text-blue-500 peer-checked:font-semibold hover:text-gray-600 hover:bg-gray-100">
              <div class="animate-pulse flex space-x-4">
                <div class="flex-1 space-y-5 py-1 grid grid-cols-5">
                  <div class="h-2 bg-slate-200 rounded col-span-3"></div>
                </div>
              </div>
            </label>
          </li>
          <li>
            <input type="radio" id="quiz-option-C" name="quiz-option" value="C" class="hidden peer" disabled>
            <label for="quiz-option-C" id="quiz-option-C-label" class="block px-6 py-3 mt-1.5 font-normal text-slate-500 bg-neutral-50 border border-slate-200 rounded-md cursor-pointer peer-checked:border-blue-500 peer-checked:text-blue-500 peer-checked:font-semibold hover:text-gray-600 hover:bg-gray-100">
              <div class="animate-pulse flex space-x-4">
                <div class="flex-1 space-y-5 py-1 grid grid-cols-5">
                  <div class="h-2 bg-slate-200 rounded col-span-2"></div>
                </div>
              </div>
            </label>
          </li>
          <li>
            <input type="radio" id="quiz-option-D" name="quiz-option" value="D" class="hidden peer" disabled>
            <label for="quiz-option-D" id="quiz-option-D-label" class="block px-6 py-3 mt-1.5 font-normal text-slate-500 bg-neutral-50 border border-slate-200 rounded-md cursor-pointer peer-checked:border-blue-500 peer-checked:text-blue-500 peer-checked:font-semibold over:text-gray-600 hover:bg-gray-100">
              <div class="animate-pulse flex space-x-4">
                <div class="flex-1 space-y-5 py-1 grid grid-cols-5">
                  <div class="h-2 bg-slate-200 rounded col-span-3"></div>
                </div>
              </div>
            </label>
          </li>
    `;
    quiz_result_container.innerHTML = `
        <button type="button" id="quiz-choice-submit-button"
            class="w-full rounded-md p-3 text-base sm:text-lg font-semibold text-white enabled:bg-gradient-to-r from-teal-500 to-blue-500 enabled:hover:scale-105 enabled:focus:scale-105 disabled:bg-slate-300 drop-shadow-sm ease-in-out duration-300"
            disabled>
            Submit
        </button>
    `;
    quiz_next_interface_div.remove();

    QUIZ_SUBMITTED = false;

}


function get_cookie(name) {

    let cookie_value = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookie_value;

}