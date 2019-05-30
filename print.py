from main import *
import time

db=DB()
imdb = IMDB(db.connection)


genre = imdb.top_ten('genre')
genre['budget'] = genre['budget'].map('${:,.2f}'.format)
genre['gross'] = genre['gross'].map('${:,.2f}'.format)
print("\n2a. Top Ten Genres from IMDB by Profit Index (i.e. for every dollar invested, how many dollars were returned)")
print("\tProfitability defined as ('gross'-'budget')/'budget'\n")
print(genre.to_string(index=False))

actor = imdb.top_ten('actor')
actor['budget'] = actor['budget'].map('${:,.2f}'.format)
actor['gross'] = actor['gross'].map('${:,.2f}'.format)
actor['profit'] = actor['profit'].map('${:,.2f}'.format)
print("\n2b. Top Ten Actors or Directors from IMDB by Profit (i.e. Net Profit)")
print("\tProfit defined as 'gross'-'budget'\n")
print(actor.to_string(index=False))

bonus = imdb.top_ten('pair')
print("\n3c. BONUS: Average IMDB Score by Director and Actor pair with at least 3 movies\n")
print(bonus.to_string(index=False))