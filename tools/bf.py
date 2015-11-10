from bs4 import BeautifulSoup
soup = BeautifulSoup(open('index2.html'))

all_a = soup.find_all('a')
for a in all_a:
   if a.has_attr('class'):
	  pass
   else:
	  if a['href'] != '#':
		 print a
