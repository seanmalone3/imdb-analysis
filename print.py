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

bonus = imdb.metrics_by_year()
bonus['avg_gross'] = bonus['avg_gross'].map('${:,.2f}'.format)
bonus['avg_budget'] = bonus['avg_budget'].map('${:,.2f}'.format)
print("\n3c. BONUS: Average IMDB Score by year since 1950\n")
response = input("Would you ready to see a not particularly interesting 66 row dataset>? \n>>>>>>>Input (y/n):")
if response.lower() in ['y','yes']:
    print(bonus.to_string(index=False))