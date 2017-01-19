#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import logging
import jinja2
import csv
import urllib2
import datetime
import math
import numpy as np
import time
from google.appengine.api import urlfetch


def get_current_price(stock):
	baseurl = 'http://finance.yahoo.com/d/quotes.csv?s='
	for_code = '&f='
	code = 'l1' 
	fullurl = baseurl + stock + for_code + code
	result = urlfetch.fetch(fullurl)
	if result.status_code == 200:
		yahoo_finance_response = urllib2.urlopen(fullurl)
		yahoo_finance_data = csv.reader(iter(yahoo_finance_response)) 
		for item in yahoo_finance_data: 
			for price in item: 
				return float(price)
def get_oneyear_price_target(stock):
	baseurl = 'http://finance.yahoo.com/d/quotes.csv?s='
	for_code = '&f=' #part three of the Yahoo Finance URL
	code = 't8' #part four of the Yahoo Finance URL. **Important: this 't8' code is the Yahoo Finance code to retrieve the one-year price target for the stock
	fullurl = baseurl + stock + for_code + code #perform a string interplation. Part 1, 3, and 4 are described above. Part two - 'self.ticker' - just plugs in the stock ticker for the particular stock that was inputted to the class (as performed on line 31)
	result = urlfetch.fetch(fullurl)
	if result.status_code == 200:
		yahoo_finance_response = urllib2.urlopen(fullurl)
		yahoo_finance_data = csv.reader(iter(yahoo_finance_response)) 
		for item in yahoo_finance_data: 
			for price in item: 
				return float(price)
def get_dividend(stock): #the program is reconstructing a Yahoo Finance URL to retrieve a csv file that contains the dividend of the particular stock
	baseurl = 'http://finance.yahoo.com/d/quotes.csv?s=' #part one of the Yahoo Finance URL
	for_code = '&f=' #part three of the Yahoo Finance URL
	code = 'd' #part four of the Yahoo Finance URL. **Important: this 'd' code is the Yahoo Finance code to retrieve dividend for the stock
	fullurl = baseurl + stock + for_code + code #perform a string interplation. Part 1, 3, and 4 are described above. Part two - 'self.ticker' - just plugs in the stock ticker for the particular stock that was inputted to the class (as performed on line 31)
	result = urlfetch.fetch(fullurl)
	if result.status_code == 200:
		yahoo_finance_response = urllib2.urlopen(fullurl)
		yahoo_finance_data = csv.reader(iter(yahoo_finance_response)) 
		for item in yahoo_finance_data: 
			try:
				for dividend in item:
					return float(dividend)
			except:
				return float(0)
def calculate_projected_return_on_investment(stock): #this method in the function is used to calculated the projected Rate of Return (ROR) percentage
	price_for_growth_plus_dividend = get_oneyear_price_target(stock)+ get_dividend(stock) #an investor's return is not only based on the price of where the stock is a year from now, but it is also how much the company has returned to the investor in the form of a dividend. A helpful way to think about it is that 'dividend' is essentially guaranteed Return on Investment and 'price target' is perspective Return on Investment
	return_percentage = float(price_for_growth_plus_dividend - get_current_price(stock))/get_current_price(stock) #now that the program has found the true monetary value of the complete Rate of Return it is a simply %change equation. This equivalent is (y2-y1)/y1, where y2 is the complete Rate of Return (aka 'price_for_growth_plus_dividend') and y1 is the 'current price'
	return return_percentage #returns that percentage of projected return for the particular stock. Will be important down the line in calculating weighted average of return for entire portfolio, and eventually calculating the portfolio's Sharpe Ratio
def calculate_volatility(stock): #now that everything with Rate of Return is squared away, the program moves on to calculating volatility
	url_pt1 = 'http://real-chart.finance.yahoo.com/table.csv?s=' #part one of Yahoo Finance URL ... will be used in order to retrieve a CSV with the historical prices for a time frame of our choice (as performed below)
	url_pt3 = '&d=' #part three of Yahoo Finance URL
	url_pt5 = '&e=' #part three of Yahoo Finance URL
	url_pt7 = '&f=' #part three of Yahoo Finance URL
	url_pt9 = '&g=d&a=' #part three of Yahoo Finance URL
	url_pt11 = '&b=' #part three of Yahoo Finance URL
	url_pt13 = '&c=' #part three of Yahoo Finance URL
	url_pt15 = '&ignore=.csv' #part three of Yahoo Finance URL
	now = datetime.datetime.now() #using the datetime import, the program uses this variable to say we want today's information when the subsequent lines ask for - day, month, year
	month = str(int(now.month)-1) #the way Yahoo Finance's URL works is that it constructs its URL with the month's number minues one. For example, if I wanted to get the information for the month of March, traditionally March would be represented by the number 3. But in Yahoo Finance, it is represented by the number 2. In order to do that, the program first converts the current month to an integer ('int'), then subtracts 1, and then converts it back to a string that will be inputted to the URL string interpolation on line 84
	day = str(now.day) #uses the now variable from line 79, and the datetime import, to retrieve the current day. It then converts the current day into a string
	currentYear = str(now.year) #uses the now variable from line 79, and the datetime import, to retrieve the current year. It then converts the current day into a string
	lastYear = str(int(now.year)-1) #because we want to find the one-year volatility, the program needs another variable for the last year so that it retrieves all historical prices from this same day in this same month today to exactly one year ago
	fullurl = url_pt1 + str(stock) + url_pt3 + month + url_pt5 + day + url_pt7 + currentYear + url_pt9 + month + url_pt11 + day + url_pt13 + lastYear + url_pt15 #brings the url all together through string interpolation
	#fullurl = 'http://real-chart.finance.yahoo.com/table.csv?s=' + str(self.ticker) + '&d=2&e=1&f=2016&g=d&a=2&b=1&c=2015&ignore.csv'
	logging.info(fullurl)
	result = urlfetch.fetch(fullurl)
	if result.status_code == 200:
		yahoo_finance_response = urllib2.urlopen(fullurl)
		yahoo_finance_data = csv.reader(iter(yahoo_finance_response)) 
		list_of_closing_prices = [] #create an empty list to append all these historical prices to so the program can perform data manipulation
		for price in yahoo_finance_data:
			list_of_closing_prices.append(price[4])
		final_list_of_closing_prices = list_of_closing_prices[1:] #the first item in this 'list_of_closing_prices' is the header 'closign prices'. Therefore, the program takes out this header, and the new list called 'final_list_of_closing_prices' is all purely numbers
		final_list_of_closing_prices = [float(x) for x in final_list_of_closing_prices]
		logging.info(final_list_of_closing_prices)
		average_closing_price = np.mean(final_list_of_closing_prices)
		list_of_each_day_deviation = []
		for price in final_list_of_closing_prices: 
			list_of_each_day_deviation.append((float(price)) - average_closing_price)
		list_of_each_day_deviationSquared = [] 
		for deviation in list_of_each_day_deviation: 
			list_of_each_day_deviationSquared.append((float(deviation))**2)
		average_deviation_per_day_squared = float((reduce(lambda x, y: float(x)+float(y), list_of_each_day_deviationSquared)) / float(len(list_of_each_day_deviationSquared))) 
		average_deviation_per_day = math.sqrt(average_deviation_per_day_squared)
		volatility_percentage = (float(average_deviation_per_day) / average_closing_price)
	return volatility_percentage
	logging.info("volatility percentage:")
	logging.iinfo(volatility_percentage)
def calculate_Sharpe_Ratio(stock): # function to find Sharpe Ratio of the portfolio. Honestly, don't need, it is just something that the program has in case we can to reference it later
		sharpe_ratio = calculate_projected_return_on_investment(stock)/calculate_volatility(stock) #calculates Sharpe ratio by taking the output of method 'calculate_projected_return_on_investment' divided by the 'volatility_percentage'. Need to use ".self" before the method names, just as the program had to do with 'ticker' in the __init__ section.
		return sharpe_ratio #returns the Sharpe Ratio of the portfolio


def current_allocation_percentages_of_portfolio(portfolio): #method to get a dictionary of the portfolio's individual stocks as the 'key' and the stock's individual allocation percentages based on dollar value (represented in percentages) for the 'value'
	my_portfolio_holding_value = {} #open dictionary we will add all the stock tickers to as well as their respective holding value (as calculated by number of shares owned * currend price of individual share)
	for stock in portfolio: # 'for' each stock (key) in the 'portfolio' dictionary
		my_portfolio_holding_value[stock] = get_current_price(stock) #runs the ticker of that particular stock through the 'Stock' class and ONLY performs the 'get_current_price' method for that stock
		my_portfolio_holding_value[stock] *= (float(portfolio[stock])) #multiplies the cuurent price for each stock which was found in line 115 by the number of shares owned from line 112
	portfolio_holding_percentages = {} #open dictionary which will be used to store the allocation percentage (calculated on basis of dollar value) as done in previous two lines
	for stock in my_portfolio_holding_value: # 'for' each stock in 'my_portfolio_holding_value' 
		individual_percent = my_portfolio_holding_value[stock]/(float(sum(my_portfolio_holding_value.values()))) #divides dollar value of that stock from the 'my_portfolio_holding_value' dictionary and divides it by all the 'values' in the 'my_portfolio_holding_value' dictionary
		portfolio_holding_percentages[stock] = float(individual_percent) #makes sure that 'indiviudal_percent' for stock's holding value is a 'float' number and then adds it to the dictionary of 'portfolio_holding_percentages'
	return portfolio_holding_percentages #returns a dictionary with all the stocks in the portfolio and their respective holding percentage in decimal form
def portfolio_ReturnOnInvestment_WeightedAverage(weighted_portfolio): #method to get a dictionary of the portfolio's individual stocks as the 'key' and the stock's individual projected rate of return as the 'value'
	my_portfolio_weighted_return = {} #empty dictionary that the method will add the portfolio's stocks and their respective WEIGHTED projected ROR to
	for stock in weighted_portfolio: # 'for' each stock in the portfolio, perform the following
		my_portfolio_weighted_return[stock] = ((float(weighted_portfolio[stock]))*float(calculate_projected_return_on_investment(stock))) #multiply the stock's allocation percentage (as retrieved from line 123) to the stock's projected return on investment calculated using the stock class. Assign the result as the 'value' and the 'stock' as the 'key' to 'my_portfolio_weighted_return' dictionary
	portfolio_ReturnonInvestment = float(100*(sum(my_portfolio_weighted_return.values()))) # sum all the values in 'my_portfolio_weighted_return' and multiply it by 100 so that it is all in percentage form rather than decimal form and assign that single number to a variable called 'portfolio_ReturnOnInvestment'
	return portfolio_ReturnonInvestment #return the 'portfolio_ReturnOnInvestment' variable
def portfolio_Volatility_WeightedAverage(weighted_portfolio): #method to get a dictionary of the portfolio's individual stocks as the 'key' and the stock's individual projected rate of return as the 'value'
	my_portfolio_weighted_volatility = {} #empty dictionary that the method will add the portfolio's stocks and their respective WEIGHTED volatility to
	for stock in weighted_portfolio: #'for' each stock in the portfolio, perform the following
		my_portfolio_weighted_volatility[stock] = ((float(weighted_portfolio[stock]))*(float(calculate_volatility(stock)))) #multiply the stock's allocation percentage by the stock's volatility as calculated by Stock class, and assigns it to 'my_portfolio_weighted_volatility' dictionary
	portfolio_Volatility = float(100*(sum(my_portfolio_weighted_volatility.values()))) # sum all the values in "my_portfolio_weighted_volatility' and multiply it by 100 so that it is all in percentage form rather than decimal form and assign that single number to a variable called 'portfolio_Volatility'
	return portfolio_Volatility #return 'portfolio_Volatility' variable
def portfolio_Sharpe_Ratio(weighted_return, weighted_volatility): #method to calculate the Sharpe Ratio of the portfolio
	sharpe = portfolio_ReturnOnInvestment_WeightedAverage(weighted_return)/portfolio_Volatility_WeightedAverage(weighted_volatility) #divides the weighted ReturnOnInvestment portfolio average by the weighted Volatility portfolio average to find the Sharpe ratio of the portfolio
	return str(sharpe) #returns the Sharpe Ratio in a 'string' so we can read the output. WILL BE MODIFIED WHEN CONVERT TO WEB DEV

def calculate_covariance(ticker1, ticker2):
	now = datetime.datetime.now()
	month = str(int(now.month)-1) 
	day = str(now.day) 
	currentYear = str(now.year) 
	lastYear = str(int(now.year)-1)
	url_pt1 = 'http://real-chart.finance.yahoo.com/table.csv?s=' 
	url_pt3 = '&d='
	url_pt5 = '&e='
	url_pt7 = '&f='
	url_pt9 = '&g=d&a='
	url_pt11 = '&b='
	url_pt13 = '&c='
	url_pt15 = '&ignore=.csv'
	fullurl = url_pt1 + ticker1 + url_pt3 + month + url_pt5 + day + url_pt7 + currentYear + url_pt9 + month + url_pt11 + day + url_pt13 + lastYear + url_pt15 
	#fullurl = 'http://real-chart.finance.yahoo.com/table.csv?s=' + ticker1 + '&d=2&e=1&f=2016&g=d&a=2&b=1&c=2015&ignore.csv'
	result = urlfetch.fetch(fullurl)
	if result.status_code == 200:
		yahoo_finance_response = urllib2.urlopen(fullurl)
		yahoo_finance_data = csv.reader(iter(yahoo_finance_response)) 
		ticker1_list_of_closing_prices = [] #create an empty list to append all these historical prices to so the program can perform data manipulation
		for row in yahoo_finance_data:
			ticker1_list_of_closing_prices.append(row[4])
		ticker1_final_list_of_closing_prices = ticker1_list_of_closing_prices[1:]
		ticker1_final_list_of_closing_prices = [float(x) for x in ticker1_final_list_of_closing_prices]
		ticker1_average_price = np.mean(ticker1_final_list_of_closing_prices)
		ticker1_average_price = float(ticker1_average_price)
		ticker1_each_day_variance = map(lambda x: x - ticker1_average_price, ticker1_final_list_of_closing_prices)
		ticker1_variance = [x**2 for x in ticker1_each_day_variance]
		ticker1_variance = sum(ticker1_variance)/len(ticker1_variance)

	fullurl = url_pt1 + ticker2 + url_pt3 + month + url_pt5 + day + url_pt7 + currentYear + url_pt9 + month + url_pt11 + day + url_pt13 + lastYear + url_pt15 
	#fullurl = 'http://real-chart.finance.yahoo.com/table.csv?s=' + ticker2 + '&d=2&e=1&f=2016&g=d&a=2&b=1&c=2015&ignore.csv'
	result = urlfetch.fetch(fullurl)
	if result.status_code == 200:
		yahoo_finance_response = urllib2.urlopen(fullurl)
		yahoo_finance_data = csv.reader(iter(yahoo_finance_response)) 
		ticker2_list_of_closing_prices = [] #create an empty list to append all these historical prices to so the program can perform data manipulation
		for row in yahoo_finance_data:
			ticker2_list_of_closing_prices.append(row[4])
		ticker2_final_list_of_closing_prices = ticker2_list_of_closing_prices[1:]
		ticker2_final_list_of_closing_prices = [float(x) for x in ticker2_final_list_of_closing_prices]
		ticker2_average_price = np.mean(ticker2_final_list_of_closing_prices)
		ticker2_average_price = float(ticker2_average_price)
		ticker2_each_day_variance = map(lambda x: x - ticker2_average_price, ticker2_final_list_of_closing_prices)
		ticker2_variance = [x**2 for x in ticker2_each_day_variance]
		ticker2_variance = sum(ticker2_variance)/len(ticker2_variance)

	#xy = [a*b for a,b in zip(ticker1_final_list_of_closing_prices, ticker2_final_list_of_closing_prices)]
	xy = [a*b for a,b in zip(ticker1_each_day_variance, ticker2_each_day_variance)]
	covariance = float(sum(xy)) / float(len(xy))
	#summation_xy = (sum(xy))/(len(xy))
	#covariance = summation_xy - (ticker1_average_price * ticker2_average_price)

	correlation = (covariance/(ticker1_variance*ticker2_variance))
	return correlation
	#return ticker1_variance, ticker2_variance, covariance


JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class HomeHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		template = JINJA_ENVIRONMENT.get_template('templates/home.html')
		self.response.write(template.render())

class AboutUsHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		template = JINJA_ENVIRONMENT.get_template('templates/aboutus.html')
		self.response.write(template.render())

class OurAlgorithmHandler(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/ouralgorithm.html')
		self.response.write(template.render())

class ResultsHandler(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('templates/results.html')
		self.response.write(template.render())

class ContactUsHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		logging.info(self.request.path)
		try:
			path = self.request.path
			template = JINJA_ENVIRONMENT.get_template('templates'+path)
			if path == '/contactus.html':
				self.response.write(template.render())
			elif path =='/newfeature.html':
				self.response.write(template.render())
			elif path =='/foundbug.html':
				self.response.write(template.render())
			elif path =='/connect.html':
				self.response.write(template.render())
			else:
				self.response.write('templates/contactus.html'.render())
		except:
			template = JINJA_ENVIRONMENT.get_template('templates/contactus.html')
			self.response.write(template.render())

class PortfolioHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		template = JINJA_ENVIRONMENT.get_template('templates/portfolio.html')
		self.response.write(template.render())

class DiagnoseHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		template = JINJA_ENVIRONMENT.get_template('templates/portfolio.html')
		self.response.write(template.render())

	def post(self):
		logging.info("POST")
		my_tickers = []
		my_shares = []
		stock1 = self.request.get('stock1')
		my_tickers.append(stock1)
		shares1 = self.request.get('shares1')
		my_shares.append(shares1)
		try:
			stock2 = self.request.get('stock2')
			my_tickers.append(stock2)
		except:
			None
		try:
			shares2 = self.request.get('shares2')
			my_shares.append(shares2)
		except:
			None
		try:
			stock3 = self.request.get('stock3')
			my_tickers.append(stock3)
		except:
			None
		try:
			shares3 = self.request.get('shares3')
			my_shares.append(shares3)
		except:
			None
		try:
			stock4 = self.request.get('stock4')
			my_tickers.append(stock4)
		except:
			None
		try:
			shares4 = self.request.get('shares4')
			my_shares.append(shares4)
		except:
			None
		try:
			stock5 = self.request.get('stock5')
			my_tickers.append(stock5)
		except:
			None
		try:
			shares5 = self.request.get('shares5')
			my_shares.append(shares5)
		except:
			None
		try:
			stock6 = self.request.get('stock6')
			my_tickers.append(stock6)
		except:
			None
		try:
			shares6 = self.request.get('shares6')
			my_shares.append(shares6)
		except:
			None
		try:
			stock7 = self.request.get('stock7')
			my_tickers.append(stock7)
		except:
			None
		try:
			shares7 = self.request.get('shares7')
			my_shares.append(shares7)
		except:
			None
		try:
			stock8 = self.request.get('stock8')
			my_tickers.append(stock8)
		except:
			None
		try:
			shares8 = self.request.get('shares8')
			my_shares.append(shares8)
		except:
			None
		try:
			stock9 = self.request.get('stock9')
			my_tickers.append(stock9)
		except:
			None
		try:
			shares9 = self.request.get('shares9')
			my_shares.append(shares9)
		except:
			None
		try:
			stock10 = self.request.get('stock10')
			my_tickers.append(stock10)
		except:
			None
		try:
			shares10 = self.request.get('shares10')
			my_shares.append(shares10)
		except:
			None
		ticker_list = []
		share_list = []
		for item in my_tickers:
			ticker_list.append(str(item.upper()))
		ticker_list = filter(None, ticker_list)
		for item in my_shares:
			share_list.append(str(item))
		share_list = filter(None, share_list)
		portfolio = dict(zip(ticker_list, share_list))
		global portfolio
		allocation_importer = current_allocation_percentages_of_portfolio(portfolio)
		allocation_list = []
		stock_list = []
		price_list = []
		dividend_list = []
		target_list = []
		growth_list = []
		volatility_list = []
		total_value = 0.0
		for stock in portfolio:
			stock_list.append(stock)
			price = get_current_price(stock)
			target = get_oneyear_price_target(stock)
			volatility = 100*(calculate_volatility(stock))
			dividend = get_dividend(stock)
			#growth = calculate_projected_return_on_investment(stock)
			growth = 100*((target + dividend - price)/price)
			total_value += (price * int(portfolio[stock]))
			allocation = 100*(allocation_importer[stock])
			price = "$"+ str(price)
			dividend = "$" + str(dividend)
			target = "$" + str(target)
			growth = "%.2f" %(growth) + "%"
			volatility = "%.2f" %(volatility) + "%"
			allocation = "%.2f" %(allocation) + "%"
			price_list.append(price)
			target_list.append(target)
			volatility_list.append(volatility)
			dividend_list.append(dividend)
			growth_list.append(growth)
			allocation_list.append(allocation)
		total_value= "$" + str(total_value)
		try:
			stock1=stock_list[0]
			price1=price_list[0]
			dividend1=dividend_list[0]
			target1=target_list[0]
			growth1=growth_list[0]
			volatility1=volatility_list[0]
			allocation1=allocation_list[0]
		except:
			stock1 = '-'
			price1 = '-'
			dividend1 = '-'
			target1 = '-'
			growth1 = '-'
			volatility1 = '-'
			allocation1 = '-'
		try:
			stock2=stock_list[1]
			price2=price_list[1]
			dividend2=dividend_list[1]
			target2=target_list[1]
			growth2=growth_list[1]
			volatility2=volatility_list[1]
			allocation2=allocation_list[1]
		except:
			stock2 = '-'
			price2 = '-'
			dividend2 = '-'
			target2 = '-'
			growth2 = '-'
			volatility2 = '-'
			allocation2 = '-'
		try:
			stock3=stock_list[2]
			price3=price_list[2]
			dividend3=dividend_list[2]
			target3=target_list[2]
			growth3=growth_list[2]
			volatility3=volatility_list[2]
			allocation3=allocation_list[2]
		except:
			stock3 = '-'
			price3 = '-'
			dividend3 = '-'
			target3 = '-'
			growth3 = '-'
			volatility3 = '-'
			allocation3 = '-'
		try:
			stock4=stock_list[3]
			price4=price_list[3]
			dividend4=dividend_list[3]
			target4=target_list[3]
			growth4=growth_list[3]
			volatility4=volatility_list[3]
			allocation4=allocation_list[3]
		except:
			stock4 = '-'
			price4 = '-'
			dividend4 = '-'
			target4 = '-'
			growth4 = '-'
			volatility4 = '-'
			allocation4 = '-'
		try:
			stock5=stock_list[4]
			price5=price_list[4]
			dividend5=dividend_list[4]
			target5=target_list[4]
			growth5=growth_list[4]
			volatility5=volatility_list[4]
			allocation5=allocation_list[4]
		except:
			stock5 = '-'
			price5 = '-'
			dividend5 = '-'
			target5 = '-'
			growth5 = '-'
			volatility5 = '-'
			allocation5 = '-'
		try:
			stock6=stock_list[5]
			price6=price_list[5]
			dividend6=dividend_list[5]
			target6=target_list[5]
			growth6=growth_list[5]
			volatility6=volatility_list[5]
			allocation6=allocation_list[6]
		except:
			stock6 = '-'
			price6 = '-'
			dividend6 = '-'
			target6 = '-'
			growth6 = '-'
			volatility6 = '-'
			allocation6 = '-'
		try:
			stock7=stock_list[6]
			price7=price_list[6]
			dividend7=dividend_list[6]
			target7=target_list[6]
			growth7=growth_list[6]
			volatility7=volatility_list[6]
			allocation7=allocation_list[6]
		except:
			stock7 = '-'
			price7 = '-'
			dividend7 = '-'
			target7 = '-'
			growth7 = '-'
			volatility7 = '-'
			allocation7 = '-'
		try:
			stock8=stock_list[7]
			price8=price_list[7]
			dividend8=dividend_list[7]
			target8=target_list[7]
			growth8=growth_list[7]
			volatility8=volatility_list[7]
			allocation8=allocation_list[7]
		except:
			stock8 = '-'
			price8 = '-'
			dividend8 = '-'
			target8 = '-'
			growth8 = '-'
			volatility8 = '-'
			allocation8 = '-'
		try:
			stock9=stock_list[8]
			price9=price_list[8]
			dividend9=dividend_list[8]
			target9=target_list[8]
			growth9=growth_list[8]
			volatility9=volatility_list[8]
			allocation9=allocation_list[8]
		except:
			stock9 = '-'
			price9 = '-'
			dividend9 = '-'
			target9 = '-'
			growth9 = '-'
			volatility9 = '-'
			allocation9 = '-'
		try:
			stock10=stock_list[9]
			price10=price_list[9]
			dividend10=dividend_list[9]
			target10=target_list[9]
			growth10=growth_list[9]
			volatility10=volatility_list[9]
			allocation10=allocation_list[9]
		except:
			stock10 = '-'
			price10 = '-'
			dividend10 = '-'
			target10 = '-'
			growth10 = '-'
			volatility10 = '-'
			allocation10 = '-'
		portfolio_allocation_percentages = current_allocation_percentages_of_portfolio(portfolio)
		portfolio_return = (str(int(portfolio_ReturnOnInvestment_WeightedAverage(portfolio_allocation_percentages))))+ "%"
		portfolio_volatility = (str(int(portfolio_Volatility_WeightedAverage(portfolio_allocation_percentages)))) + "%"

		template = JINJA_ENVIRONMENT.get_template('templates/diagnosis.html')
		self.response.write(template.render({'portfolioreturn': portfolio_return, 'portfoliovolatility': portfolio_volatility, 'totalvalue': total_value, 'stock1': stock1, 'price1': price1, 'dividend1': dividend1, 'target1': target1, 'growth1': growth1, 'volatility1': volatility1, 'allocation1': allocation1, 'stock2': stock2, 'price2': price2, 'dividend2': dividend2, 'target2': target2, 'growth2': growth2, 'volatility2': volatility2, 'allocation2': allocation2, 'stock3': stock3, 'price3': price3, 'dividend3': dividend3, 'target3': target3, 'growth3': growth3, 'volatility3': volatility3, 'allocation3': allocation3, 'stock4': stock4, 'price4': price4, 'dividend4': dividend4, 'target4': target4, 'growth4': growth4, 'volatility4': volatility4, 'allocation4': allocation4, 'stock5': stock5, 'price5': price5, 'dividend5': dividend5, 'target5': target5, 'growth5': growth5, 'volatility5': volatility5, 'allocation5': allocation5, 'stock6': stock6, 'price6': price6, 'dividend6': dividend6, 'target6': target6, 'growth6': growth6, 'volatility6': volatility6, 'allocation6': allocation6, 'stock7': stock7, 'price7': price7, 'dividend7': dividend7, 'target7': target7, 'growth7': growth7, 'volatility7': volatility7, 'allocation7': allocation7, 'stock8': stock8, 'price8': price8, 'dividend8': dividend8, 'target8': target8, 'growth8': growth8, 'volatility8': volatility8, 'allocation8': allocation8, 'stock9': stock9, 'price9': price9, 'dividend9': dividend9, 'target9': target9, 'growth9': growth9, 'volatility9': volatility9, 'allocation9': allocation9, 'stock10': stock10, 'price10': price10, 'dividend10': dividend10, 'target10': target10, 'growth10': growth10, 'volatility10': volatility10, 'allocation10': allocation10}))

class RecommendHandler(webapp2.RequestHandler):
	def post(self):
		logging.info("POST")
		template = JINJA_ENVIRONMENT.get_template('templates/recommend.html')
		self.response.write(template.render())			

class OutputHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		template = JINJA_ENVIRONMENT.get_template('templates/recommend.html')
		self.response.write(template.render())

	def post(self):
		logging.info("POST")
		stockpurchase1 = self.request.get('stockpurchase1')
		stockpurchase2 = self.request.get('stockpurchase2')
		moneyinvestment = float(self.request.get('moneyinvestment'))
		my_portfolio_holding_value = {}
		for stock in portfolio:
			my_portfolio_holding_value[stock] = get_current_price(stock)
			my_portfolio_holding_value[stock] *= (float(portfolio[stock]))
			logging.info(my_portfolio_holding_value[stock])
		portfoliovalue = (float(sum(my_portfolio_holding_value.values())))
		weighted_portfolio = current_allocation_percentages_of_portfolio(portfolio)
		percentaffected = float(moneyinvestment)/(portfoliovalue+(float(moneyinvestment)))
		
		portfoliobaseROR = (portfolio_ReturnOnInvestment_WeightedAverage(weighted_portfolio))
		stock1ROR = float(calculate_projected_return_on_investment(stockpurchase1))
		stock2ROR = float(calculate_projected_return_on_investment(stockpurchase2))
		new_0_100 = 100*((0.0*stock1ROR) + (1.0*stock2ROR))
		logging.info("individual returns here:")
		logging.info("0_100::")
		logging.info(new_0_100)
		return_0_100 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_0_100))
		new_10_90 = 100*((0.1*stock1ROR) + (0.9*stock2ROR))
		logging.info("10_90::")
		logging.info(new_10_90)
		return_10_90 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_10_90))
		new_20_80 = 100*((0.2*stock1ROR) + (0.8*stock2ROR))
		logging.info("20_80::")
		logging.info(new_20_80)
		return_20_80 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_20_80))
		new_30_70 = 100*((0.3*stock1ROR) + (0.7*stock2ROR))
		logging.info("30_70::")
		logging.info(new_30_70)
		return_30_70 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_30_70))
		new_40_60 = 100*((0.4*stock1ROR) + (0.6*stock2ROR))
		logging.info("40_60::")
		logging.info(new_40_60)
		return_40_60 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_40_60))
		new_50_50 = 100*((0.5*stock1ROR) + (0.5*stock2ROR))
		logging.info("50_50::")
		logging.info(new_50_50)
		return_50_50 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_50_50))
		new_60_40 = 100*((0.6*stock1ROR) + (0.4*stock2ROR))
		logging.info("60_40::")
		logging.info(new_60_40)
		return_60_40 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_60_40))
		new_70_30 = 100*((0.7*stock1ROR) + (0.3*stock2ROR))
		logging.info("70_30::")
		logging.info(new_70_30)
		return_70_30 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_70_30))
		new_80_20 = 100*((0.8*stock1ROR) + (0.2*stock2ROR))
		logging.info("80_20::")
		logging.info(new_80_20)
		return_80_20 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_80_20))
		new_90_10 = 100*((0.9*stock1ROR) + (0.1*stock2ROR))
		logging.info("90_10::")
		logging.info(new_90_10)
		return_90_10 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_90_10))
		new_100_0 = 100*((1.0*stock1ROR) + (0.0*stock2ROR))
		logging.info("100_0::")
		logging.info(new_100_0)
		return_100_0 = float(((1.0- percentaffected)*portfoliobaseROR) + (percentaffected*new_100_0))

		portfoliobaseVolatility = ((1.0 - percentaffected)*(portfolio_Volatility_WeightedAverage(weighted_portfolio)))
		logging.info('PORTFOLIO BASE VOLATILITY')
		logging.info(portfoliobaseVolatility)
		logging.info('percentaffected')
		logging.info(percentaffected)
		the_covar = calculate_covariance(stockpurchase1, stockpurchase2)
		stock1Volatility = calculate_volatility(stockpurchase1)
		logging.info('Stock1Volatility final calc')
		logging.info(stock1Volatility)
		stock2Volatility = calculate_volatility(stockpurchase2)
		logging.info('stock2Volatility final calc')
		logging.info(stock2Volatility)
		#stock1Variation, stock2Variation, the_covar = calculate_covariance(stockpurchase1, stockpurchase2)
		#stock1Volatility = math.sqrt(stock1Variation)
		#stock2Volatility = math.sqrt(stock2Variation)
		logging.info('covar')
		logging.info(the_covar)

		logging.info("Individual volatilities here:")
		spec_volatility_0_100 = (((0.0*stock1Volatility)**2)+((1.0*stock2Volatility)**2)+(2.0*0.0*1.0*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_0_100 = math.sqrt(spec_volatility_0_100)
		logging.info("0_100::")
		logging.info(spec_volatility_0_100)
		volatility_0_100 = portfoliobaseVolatility + (percentaffected* spec_volatility_0_100*100)
		logging.info(volatility_0_100)

		spec_volatility_10_90 = (((0.1*stock1Volatility)**2)+((0.9*stock2Volatility)**2)+(2.0*0.1*0.9*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_10_90 = math.sqrt(spec_volatility_10_90)
		logging.info("10_90::")
		logging.info(spec_volatility_10_90)
		volatility_10_90 = portfoliobaseVolatility + (percentaffected* spec_volatility_10_90*100)
		logging.info(volatility_10_90)

		spec_volatility_20_80 = (((0.2*stock1Volatility)**2)+((0.8*stock2Volatility)**2)+(2.0*0.2*0.8*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_20_80 = math.sqrt(spec_volatility_20_80)
		logging.info("20_80::")
		logging.info(spec_volatility_20_80)
		volatility_20_80 = portfoliobaseVolatility + (percentaffected* spec_volatility_20_80*100)
		logging.info(volatility_20_80)

		spec_volatility_30_70 = (((0.3*stock1Volatility)**2)+((0.7*stock2Volatility)**2)+(2.0*0.3*0.7*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_30_70 = math.sqrt(spec_volatility_30_70)
		logging.info("30_70::")
		logging.info(spec_volatility_30_70)
		volatility_30_70 = portfoliobaseVolatility + (percentaffected* spec_volatility_30_70*100)
		logging.info(volatility_30_70)

		spec_volatility_40_60 = (((0.4*stock1Volatility)**2)+((0.6*stock2Volatility)**2)+(2.0*0.4*0.6*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_40_60 = math.sqrt(spec_volatility_40_60)
		logging.info("40_60::")
		logging.info(spec_volatility_40_60)
		volatility_40_60 = portfoliobaseVolatility + (percentaffected* spec_volatility_40_60*100)
		logging.info(volatility_40_60)

		spec_volatility_50_50 = (((0.5*stock1Volatility)**2)+((0.5*stock2Volatility)**2)+(2.0*0.5*0.5*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_50_50 = math.sqrt(spec_volatility_50_50)
		logging.info("50_50::")
		logging.info(spec_volatility_50_50)
		volatility_50_50 = portfoliobaseVolatility + (percentaffected* spec_volatility_50_50*100)
		logging.info(volatility_50_50)

		spec_volatility_60_40 = (((0.6*stock1Volatility)**2)+((0.4*stock2Volatility)**2)+(2.0*0.6*0.4*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_60_40 = math.sqrt(spec_volatility_60_40)
		logging.info("60_40::")
		logging.info(spec_volatility_60_40)
		volatility_60_40 = portfoliobaseVolatility + (percentaffected* spec_volatility_60_40*100)
		logging.info(volatility_60_40)

		spec_volatility_70_30 = (((0.7*stock1Volatility)**2)+((0.3*stock2Volatility)**2)+(2.0*0.7*0.3*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_70_30 = math.sqrt(spec_volatility_70_30)
		logging.info("70_30::")
		logging.info(spec_volatility_70_30)
		volatility_70_30 = portfoliobaseVolatility + (percentaffected* spec_volatility_70_30*100)
		logging.info(volatility_70_30)

		spec_volatility_80_20 = (((0.8*stock1Volatility)**2)+((0.2*stock2Volatility)**2)+(2.0*0.8*0.2*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_80_20 = math.sqrt(spec_volatility_80_20)
		logging.info("80_20::")
		logging.info(spec_volatility_80_20)
		volatility_80_20 = portfoliobaseVolatility + (percentaffected* spec_volatility_80_20*100)
		logging.info(volatility_80_20)

		spec_volatility_90_10 = (((0.9*stock1Volatility)**2)+((0.1*stock2Volatility)**2)+(2.0*0.9*0.1*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_90_10 = math.sqrt(spec_volatility_90_10)
		logging.info("90_10::")
		logging.info(spec_volatility_90_10)
		volatility_90_10 = portfoliobaseVolatility + (percentaffected* spec_volatility_90_10*100)
		logging.info(volatility_90_10)

		spec_volatility_100_0 = (((1.0*stock1Volatility)**2)+((0.0*stock2Volatility)**2)+(2.0*0.0*1.0*the_covar*stock1Volatility*stock2Volatility))
		spec_volatility_100_0 = math.sqrt(spec_volatility_100_0)
		logging.info("100_0::")
		logging.info(spec_volatility_100_0)
		volatility_100_0 = portfoliobaseVolatility + (percentaffected* spec_volatility_100_0*100)
		logging.info(volatility_100_0)

		sharpe0 = return_0_100 / volatility_0_100
		sharpe1 = return_10_90 / volatility_10_90
		logging.info('IS IT FUCKED UP HERE?')
		logging.info('Return:')
		logging.info(return_10_90)
		logging.info('Volatility:')
		logging.info(volatility_10_90)
		logging.info('Sharpe:')
		logging.info(sharpe1)
		sharpe2 = return_20_80 / volatility_20_80
		sharpe3 = return_30_70 / volatility_30_70
		sharpe4 = return_40_60 / volatility_40_60
		sharpe5 = return_50_50 / volatility_50_50
		sharpe6 = return_60_40 / volatility_60_40
		sharpe7 = return_70_30 / volatility_70_30
		sharpe8 = return_80_20 / volatility_80_20
		sharpe9 = return_90_10 / volatility_90_10
		sharpe10 = return_100_0 / volatility_100_0

		alloc0 = "0%" + stockpurchase1 + ".  100%" + stockpurchase2
		alloc1 = "10%" + stockpurchase1 + ".  90%" + stockpurchase2
		alloc2 = "20%" + stockpurchase1 + ".  80%" + stockpurchase2
		alloc3 = "30%" + stockpurchase1 + ".  70%" + stockpurchase2
		alloc4 = "40%" + stockpurchase1 + ".  60%" + stockpurchase2
		alloc5 = "50%" + stockpurchase1 + ".  50%" + stockpurchase2
		alloc6 = "60%" + stockpurchase1 + ".  40%" + stockpurchase2
		alloc7 = "70%" + stockpurchase1 + ".  30%" + stockpurchase2
		alloc8 = "80%" + stockpurchase1 + ".  20%" + stockpurchase2
		alloc9 = "90%" + stockpurchase1 + ".  10%" + stockpurchase2
		alloc10 = "100%" + stockpurchase1 + ".  0%" + stockpurchase2

		sharpe_list = {alloc10: sharpe10, alloc9: sharpe9, alloc8: sharpe8, alloc7: sharpe7, alloc6: sharpe6, alloc5: sharpe5, alloc4: sharpe4, alloc3: sharpe3, alloc2: sharpe2, alloc1: sharpe1, alloc0: sharpe0}
		sharpevalue= max(sharpe_list.values())
		maxsharpe = sharpe_list.keys()[sharpe_list.values().index(sharpevalue)]
		return_list = {alloc0: return_0_100, alloc1: return_10_90, alloc2: return_20_80, alloc3: return_30_70, alloc4: return_40_60, alloc5: return_50_50, alloc6: return_60_40, alloc7: return_70_30, alloc8: return_80_20, alloc9: return_90_10, alloc10: return_100_0}
		returnvalue = max(return_list.values())
		maxreturn= return_list.keys()[return_list.values().index(returnvalue)]
		risk_list = {alloc0: volatility_0_100, alloc1: volatility_10_90, alloc2: volatility_20_80, alloc3: volatility_30_70, alloc4: volatility_40_60, alloc5: volatility_50_50, alloc6: volatility_60_40, alloc7: volatility_70_30, alloc8: volatility_80_20, alloc9: volatility_90_10, alloc10: volatility_100_0}
		riskvalue = min(risk_list.values())
		minrisk= risk_list.keys()[risk_list.values().index(riskvalue)]

		template = JINJA_ENVIRONMENT.get_template('templates/output.html')
		self.response.write(template.render({'maxsharpe': maxsharpe, 'maxreturn': maxreturn, 'minrisk': minrisk, 'alloc0': alloc0, 'alloc1':alloc1, 'alloc2': alloc2, 'alloc3': alloc3, 'alloc4': alloc4, 'alloc5': alloc5, 'alloc6': alloc6, 'alloc7': alloc7, 'alloc8': alloc8, 'alloc9': alloc9, 'alloc10': alloc10, 'return0': return_0_100, 'return1': return_10_90, 'return2': return_20_80, 'return3': return_30_70, 'return4': return_40_60, 'return5': return_50_50, 'return6': return_60_40, 'return7': return_70_30, 'return8': return_80_20, 'return9': return_90_10, 'return10': return_100_0, 'volatility0': volatility_0_100, 'volatility1': volatility_10_90, 'volatility2': volatility_20_80, 'volatility3': volatility_30_70, 'volatility4': volatility_40_60, 'volatility5': volatility_50_50, 'volatility6': volatility_60_40, 'volatility7': volatility_70_30, 'volatility8': volatility_80_20, 'volatility9': volatility_90_10, 'volatility10': volatility_100_0, 'sharpe0': sharpe0, 'sharpe1': sharpe1, 'sharpe2': sharpe2, 'sharpe3': sharpe3, 'sharpe4': sharpe4, 'sharpe5': sharpe5, 'sharpe6': sharpe6, 'sharpe7': sharpe7, 'sharpe8':sharpe8, 'sharpe9': sharpe9, 'sharpe10': sharpe10}))

class ErrorHandler(webapp2.RequestHandler):
	def get(self):
		logging.info("GET")
		template = JINJA_ENVIRONMENT.get_template('templates/error.html')
		self.response.write(template.render())

app = webapp2.WSGIApplication([
	('/', HomeHandler),
	('/home.html', HomeHandler),
	('/aboutus.html', AboutUsHandler),
	('/ouralgorithm.html', OurAlgorithmHandler),
	('/results.html', ResultsHandler),
	('/contactus.html', ContactUsHandler),
	('/newfeature.html', ContactUsHandler),
	('/foundbug.html', ContactUsHandler),
	('/connect.html', ContactUsHandler),
	('/portfolio.html', PortfolioHandler),
	('/diagnosis.html', DiagnoseHandler),
	('/recommend.html', RecommendHandler),
	('/output.html', OutputHandler),
], debug= False)
