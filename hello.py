from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    request
)

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


app = Flask(__name__)

app.config["SECRET_KEY"] = "hard-to-guess-string"

bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField(
        "What is your name?",
        validators=[DataRequired()]
    )

    email = StringField(
        "What is your UofT Email address?",
        validators=[DataRequired(), Email()]
    )

    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()

    if form.validate_on_submit():
        old_name = session.get("name")
        old_email = session.get("email")

        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have changed your name!")

        if old_email is not None and old_email != form.email.data:
            flash("Looks like you have changed your email!")

        session["name"] = form.name.data
        session["email"] = form.email.data

        if "utoronto" in form.email.data.lower():
            session["valid_uoft_email"] = True
            return redirect(url_for("chatbot"))
        else:
            session["valid_uoft_email"] = False

    return render_template(
        "index.html",
        form=form,
        name=session.get("name"),
        email=session.get("email"),
        valid_uoft_email=session.get("valid_uoft_email")
    )


@app.route("/chatbot")
def chatbot():
    if not session.get("valid_uoft_email"):
        return redirect(url_for("index"))

    return render_template(
        "chatbot.html",
        username=session.get("name")
    )


@app.route("/chat", methods=["POST"])
def chat():
    message = request.json["message"]
    message_lower = message.lower()

    if message_lower.startswith("my name is "):
        name = message[11:].strip().rstrip(".")
        session["chat_name"] = name
        reply = f"Nice to meet you, {name}!"

    elif "what is my name" in message_lower:
        name = session.get("chat_name")

        if name:
            reply = f"Your name is {name}."
        else:
            reply = "I don't know your name yet."

    elif "hello" in message_lower:
        reply = "Hello!"

    else:
        reply = "I don't understand."

    return {"reply": reply}


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)