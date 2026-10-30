from flask import Flask, render_template, request
import markdown

from app.agent import answer

app = Flask(__name__)


@app.post("/ask")
def ask():
    reply = answer(request.form["user_id"], request.form["question"])
    return render_template("reply.html", reply=markdown.markdown(reply))


# Safe: plain-text summary, autoescaped by Jinja (decoy)
@app.post("/summary")
def summary():
    reply = answer(request.form["user_id"], "Summarise my last order in one line.")
    return render_template("summary.html", summary=reply)


app.run(host="0.0.0.0", debug=True)
