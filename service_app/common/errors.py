from werkzeug.exceptions import BadRequest


class IncorrectRequestBodyError(BadRequest):
    message = "[API ERROR] Incorrect fields in request body."


class ExistingUserError(BadRequest):
    message = "[API ERROR] User is already exist in DB."
