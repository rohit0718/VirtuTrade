# VirtuTrade

Paper money trading web application built using `Flask`, deployed using `Heroku`. Simple implementation of a web application that, as the name suggests, is created for those who may want to try out paper money investing before their ventures into doing so with their hard earney money. The application was also created as an introductory venture into the world of full stack web development:
- Started out with thinking about the architecture of the application, particularly in the choice of a frontend web framework, database, and server to host my application on. Decided to go with `Flask` as my frontend framework, `sqlite3` as my database, and `Heroku` as my cloud platform.
- I then went on to design the UI of the application and implemented it using `Flask`, with some simple `HTML, CSS, Javascript` tools such as `Bootstrap`.
- Using `Flask` for session management, I then used `sqlite3` as my database to store all the information required for the application, including `username`, `password` (hashed with `sha`), value of account, number of stocks held, history of transactions etc.
- I used the free API service provided by `iexcloud` to obtain real time data of stocks during buy and sell transactions and the full featured free chart provided by `TradingView` to analyse trends of the stock over time.
- Finally, using free cloud services provided by `Heroku`, I deployed the application to the cloud. (Disclaimer: because of the limitations of the free cloud services provided by `Heroku`, it may lead to a slightly longer wait time on initial load of the application, as the server "sleeps" when there is no network activity for 30 minutes or more and requires some time to restart the server.)


View the application at https://virtu-trade.herokuapp.com/
