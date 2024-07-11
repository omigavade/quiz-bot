from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id, session)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    current_question = get_current_question(current_question_id)

    if current_question is None:
        return False, "There is no current question to answer."

    correct_answer = current_question['correct_answer']
    if answer not in current_question['options']:
        return False, "Invalid answer. Please choose a valid option."

    if "answers" not in session:
        session["answers"] = []

    session["answers"].append({
        'question': current_question['question'],
        'answer': answer,
        'correct': answer == correct_answer
    })

    return True, None


def get_current_question(current_question_id):
    for question in PYTHON_QUESTION_LIST:
        if question['id'] == current_question_id:
            return question
    return None


def get_next_question(current_question_id, session):
    current_index = next((index for (index, d) in enumerate(PYTHON_QUESTION_LIST) if d["id"] == current_question_id), None)

    if current_index is None or current_index + 1 >= len(PYTHON_QUESTION_LIST):
        return None, None

    next_question = PYTHON_QUESTION_LIST[current_index + 1]
    return next_question['question'], next_question['id']


def generate_final_response(session):
    answers = session.get("answers", [])
    total_questions = len(answers)
    correct_answers = sum(1 for answer in answers if answer['correct'])

    return f"You answered {correct_answers} out of {total_questions} questions correctly. Your score is {correct_answers}/{total_questions}."
