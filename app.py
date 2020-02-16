import os
import sqlite3

from flask import Flask, flash, jsonify, redirect, render_template, request, session, g
from flask_session.__init__ import Session
# from flask import session as Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("select symbol, name, shares from shares where id = ?", [session["user_id"]])
    rows = c.fetchall()
    dict = []
    holdings = 0
    for row in rows:
        tmp = lookup(row[0])
        holdings += tmp["price"] * float(row[2])
        dict.append((row[0], row[1], row[2], tmp["price"], float(row[2]) * tmp["price"]))

    c.execute("select cash from users where id = ?", [session["user_id"]])
    money = c.fetchall()
    return render_template("index.html", rows = dict, money = money[0][0], holdings = holdings + int(money[0][0]))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        dict = lookup(symbol)
        print(dict)
        if not symbol or not dict:
            return apology("Please enter a valid symbol.")

        user = session["user_id"]
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("select cash from users where id = ?", [user])
        rows = c.fetchall()

        cash = rows[0][0]
        cost = shares * dict["price"]

        if cash >= cost:

            # 1) insert symbol, name, shares, price into table named 'shares'
            c.execute("select symbol from shares where symbol = ? and id = ?", [symbol, user])
            rows = c.fetchall()

            if not rows:
                c.execute("insert into shares(id, symbol, name, shares) values(?,?,?,?)", [user, symbol, dict["name"], shares])
                conn.commit()
            elif rows[0][0] == symbol:
                    c.execute("select * from shares where symbol = ? and id = ?", [symbol, user])
                    rows = c.fetchall()
                    new_shares = int(rows[0][3]) + shares
                    c.execute("update shares set shares = ? where id = ? and symbol = ?", [new_shares, user, symbol])
                    conn.commit()

            # 2) insert symbol, shares, price, transcated date into table named 'history'
            c.execute("insert into history(id, symbol, shares, price) values(?,?,?,?)", [user, symbol, shares, dict["price"]])
            conn.commit()

            # 3) update cash value in 'users'
            cash -= cost
            c.execute("update users set cash = ? where id = ?", [cash, user])
            conn.commit()

            return redirect("/")

        else:
            c.close()
            return apology("Not enough cash. Please top up.")





    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    return jsonify("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user = session["user_id"]
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("select symbol, shares, price, transacted from history where id = ?", [user])
    rows = c.fetchall()
    c.close()
    return render_template("history.html", rows = rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Please provide your username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Please provide your password.", 403)

        # Query database for username
        user = request.form.get("username")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("select * from users where username = ?", [user])
        rows = c.fetchall()
        c.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        quote = request.form.get("quote")
        dict = lookup(quote)
        if not dict:
            return apology("Invalid symbol.")
        else:
            return render_template("quoted.html", name=dict["name"], symbol=dict["symbol"], price=dict["price"])
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Please enter a valid username.")
        if not request.form.get("password"):
            return apology("Please enter a valid password.")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Your passwords do not match.")

        user = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        # checking if the username already exists
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("select username from users where username = ?", [user])
        rows = c.fetchall()
        try:
            if rows[0][0] == user:
                return apology("Username already exists.")
        except:
            pass

        # adding user into table
        c.execute("insert into users(username, hash) values(?,?)", [user, hash])
        conn.commit()
        c.close()

        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        user = session["user_id"]
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        dict = lookup(symbol)
        price = dict["price"]

        # update shares table
        c.execute("select shares from shares where id = ? and symbol = ?", [user, symbol])
        rows = c.fetchall()
        cur_shares = int(rows[0][0])
        if cur_shares < shares:
            return apology("Not enough shares.")
        elif cur_shares == shares:
            c.execute("delete from shares where id = ? and symbol = ?", [user, symbol])
            conn.commit()
        else:
            new_shares = cur_shares - shares
            c.execute("update shares set shares = ? where id = ? and symbol = ?", [new_shares, user, symbol])
            conn.commit()

        # update cash
        c.execute("select cash from users where id = ?", [user])
        rows = c.fetchall()
        cash = float(rows[0][0])
        cash += price * shares
        c.execute("update users set cash = ? where id = ?", [cash, user])
        conn.commit()

        # update history
        shares *= -1
        c.execute("insert into history(id, symbol, shares, price) values(?,?,?,?)", [user, symbol, shares, dict["price"]])
        conn.commit()
        c.close()

        return redirect('/')
    else:
        user = session["user_id"]
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("select symbol from shares where id = ?", [user])
        rows = c.fetchall()
        c.close()
        return render_template("sell.html", rows = rows)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
  app.run()