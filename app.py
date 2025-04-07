from flask import Flask,request,render_template
import sqlite3
import datetime
import google.generativeai as genai
import os
import wikipedia
import requests

api = os.getenv("makersuite")
telegram_api = os.getenv("telegram")
model = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=api)

app = Flask(__name__)

flag = 1

@app.route("/",methods=["POST","GET"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["POST","GET"])
def main():
    global flag
    if flag == 1:
        t = datetime.datetime.now()
        user_name = request.form.get("q")
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("insert into user (name, timestamp) values (?,?)", (user_name, t))
        conn.commit()
        c.close()
        conn.close
        flag = 0
    return(render_template("main.html"))

@app.route("/foodexp",methods=["POST","GET"])
def foodexp():
    return(render_template("foodexp.html"))

@app.route("/foodexp_pred",methods=["POST","GET"])
def foodexp_pred():
    q = float(request.form.get("q"))
    return(render_template("foodexp_pred.html",r=(q*0.4851)+147.4))

@app.route("/foodexp1",methods=["POST","GET"])
def foodexp1():
    return(render_template("foodexp1.html"))

@app.route("/telegram",methods=["POST","GET"])
def telegram():
    return(render_template("telegram.html"))

@app.route("/interest_pred",methods=["POST","GET"])
def interest_pred():
    q = float(request.form.get("q"))
    url = f"https://api.telegram.org/bot{telegram_api}/"
    updates = url+"getUpdates"
    r = requests.get(updates)
    r = r.json()
    print(r)
    chatId = r["result"][-1]["message"]["chat"]["id"]
    prompt = "please enter inflation rate, type exit to break"
    msg = url + f"sendMessage?chat_id={chatId}&text={prompt}"
    requests.get(msg)
    q = "The predicted interest rate is" + str(q+1.5)
    msg = url + f"sendMessage?chat_id={chatId}&text={q}"
    requests.get(msg)
    return(render_template("telegram_reply.html",r=q))

@app.route('/investment', methods=['POST'])
def investment():
    investment_type = request.form.get('type')
    if investment_type == "Equity":
        txt = "Equity" 
    elif investment_type == "Fixed Income":
        txt = "Fixed Income" 
    elif investment_type == "Alternatives":
        txt = "Alternatives" 
    prompt = f"Please provide top 3 investment recommendations in {txt}.List the recommendations in the following strict format:1. Recommendation One 2. Recommendation Two 3. Recommendation Three .Do not include any introductory or concluding text. Just the raw list in the specified format."
    r = model.generate_content(prompt)
    print(r)
    return render_template("investment_recom.html", r=r.candidates[0].content.parts[0].text,investment_type=investment_type)

@app.route("/investment_recom",methods=["POST","GET"])
def investment_recom():
    return(render_template("asset_choice.html"))

@app.route("/ethical_test",methods=["POST","GET"])
def ethical_test():
    return(render_template("ethical_test.html"))

@app.route("/test_result",methods=["POST","GET"])
def test_result():
    answer = request.form.get("answer")
    if answer=="false":
        return(render_template("pass.html"))
    elif answer=="true":
        return(render_template("fail.html"))

@app.route("/FAQ",methods=["POST","GET"])
def FAQ():
    return(render_template("FAQ.html"))

@app.route("/FAQ1",methods=["POST","GET"])
def FAQ1():
    r = model.generate_content("Factors for Profit")
    return(render_template("FAQ1.html",r=r.candidates[0].content.parts[0]))

@app.route("/FAQinput",methods=["POST","GET"])
def FAQinput():
    q = request.form.get("q")
    r = wikipedia.summary(q)
    return(render_template("FAQinput.html",r=r))

@app.route("/userLog",methods=["POST","GET"])
def userLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from user")
    r = ""
    for row in c:
        r = r + str(row) + "\n"
    print(r)
    c.close()
    conn.close
    return(render_template("userLog.html",r=r))

@app.route("/deleteLog",methods=["POST","GET"])
def deleteLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("delete from user")
    conn.commit()
    c.close()
    conn.close
    return(render_template("deleteLog.html"))

if __name__ == "__main__":
    app.run()