import re
import os

t = re.compile('id = \{(.*?)\}', re.MULTILINE)
ans = t.search('id = {didi} \n id = {feiwu}').group(1)
print (ans)

print (len('\n'))

path = os.path.join('e:/abd', 'erf')
print (path)

# import theme_discovery.citation_based_method



