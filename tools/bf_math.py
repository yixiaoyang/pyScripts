from bs4 import BeautifulSoup
soup = BeautifulSoup(open('index2.html'))

all_a = soup.find_all('a')
for a in all_a:
   if not a.has_attr('class'):
	  pass
   else:
	  if a['class'] != 'personItem':
		 print a
