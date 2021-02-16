#! python3

'''
1.      pull old info on index weights from existing file
1.a)    create a file that has previous prices of assets and their associative weights
2.      create a function that determines what the top 10 will be
3.      call api for new prices and market caps of assets
4.      compare current market caps to previous market caps
5.      find difference and assign the difference to the new weights
'''

from pycoingecko import CoinGeckoAPI
import shelve
import openpyxl


# gather old info
shelfFile = shelve.open('index')
blacklist = shelfFile['blacklist']
old_portfolio_total = shelfFile['old_portfolio_total']
old_weights = shelfFile['old_weights']
old_market_caps = shelfFile['old_market_caps']


# conduct analyses
cg = CoinGeckoAPI()
raw = cg.get_coins_markets(vs_currency='usd')       # all coins in top 100
date = raw[0]['last_updated']                       # date and time of reweighing
top100 = {}                                         # empty dictionary for top 100, cleaned by market cap

# populates mcs dictionary with ticker as key and market cap as value
for i in range(len(raw)):
    top100.setdefault(raw[i]['symbol'], raw[i]['market_cap'])

# pulls blacklist from shelf file and removes assets from mcs dictionary
for i in blacklist:
    if i in top100:
        del top100[i]
#print(top100)

# creates a sorted list of top 10 coins by market cap; new top 10
sorted_top10 = sorted(top100, key=lambda k:top100[k], reverse=True)[0:10]
#print(sorted_top10)


# assigns market cap to each of the top 10 and creates a total cap variable to be used to find weights
new_market_caps = {}
totalcap = 0
for i in sorted_top10:
    cap = top100[i]
    new_market_caps.setdefault(i, cap)
    totalcap += cap
#print(old_market_caps, '\n', new_market_caps)


# determining growth in total cap
cap_growth = 0
for i in sorted_top10:
    ind_growth = (new_market_caps[i]/old_market_caps[i]) * old_weights[i]
    cap_growth += ind_growth
new_portfolio_total = old_portfolio_total * cap_growth
print(new_portfolio_total)

# determines new weights
new_weights = {}
for i in sorted_top10:
    ind_weight = top100[i] / totalcap
    new_weights.setdefault(i, ind_weight)
#print(new_weights)

for i in sorted_top10:
    if i in old_weights:
        difference = (new_weights[i] - old_weights[i]) * new_portfolio_total
        if difference > 0:
            print('Weight of %s has grown. Buy $%d of %s.' % (i, difference, i))
        elif difference < 0:
            difference = difference * -1
            print('Weight of %s has shrunk. Sell $%d of %s.' % (i, difference, i))
        else:
            print('Weight for %s has not changed.' % i)
    else:
        for j in old_weights:
            if j not in new_weights:
                print('%s has been removed from top 10. Sell all.' % j)
                purchase = new_weights[i] * new_portfolio_total
                print('%s has been newly added. Buy $%d of %i.' % (i, purchase, i))

#wb = openpyxl.load_workbook()


#shelfFile['old_market_caps'] = new_market_caps
#shelfFile['old_weights'] = new_weights
#shelfFile['old_portfolio_total'] = new_portfolio_total

shelfFile.close()
