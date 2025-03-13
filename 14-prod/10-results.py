from common import get_prefix_list
import os
prefix_list = get_prefix_list(0)
for prefix in prefix_list:
	os.system(f'grep {prefix} database.txt')
