import re

diffs = []
diff = None

class Diff:
    pass

with open('romeo_and_juliet_diff.txt') as f:
    lines = f.readlines()

for line in lines:
    lno = re.match(r'[0-9]+', line)
    if lno is not None:
        diffs.append(diff)
        diff = Diff()
        print(lno[0])