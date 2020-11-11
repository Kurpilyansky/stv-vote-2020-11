#!/usr/bin/env python3

candidates = "Глеб Чипига	Даниил Любаров	Галина Селиванова	Анна Лазарева	Сергей Большаков	Мария Чебыкина	Дмитрий Наумов	Филипп Воробьёв	Иван Шальнев	Ольга Дмитриева".split('\t')
#candidates = "Ч Л С л Б ч Н В Ш Д".split()

ballots_data = """
9	7	5	4	1	10	6	3	2	8
1	2	10	8	6	5	3	7	9	4
10	8	4	2	3	9	7	1	5	6
5	1	10	9	7	4	2	3	6	8
2	7	6	4	5	8	1	9	10	3
2	4	9	8	5	1	3	7	6	10
10	8	6	3	2	5	9	1	7	4
6	10	4	1	2	3	7	8	5	9
7	4	2	5	3	6	10	8	1	9
3	2	10	5	8	4	1	6	9	7
10	6	3	2	4	7	9	1	8	5
6	2	5	9	3	4	1	7	10	8
2	3	4	5	7	6	1	8	9	10
8	10	5	4	1	7	9	6	3	2
	10	8	7	5			9		6
3	10	9	6	5	1	2	7	4	8
9	8	2	4	7	5	10	1	6	3
8	4	10	7	3	6	1	2	5	9
6	9	8	4	3	7	10	1	2	5
4	2	10	3	6	9	1	8	5	7
		7	8	10			5	6	9
10	2	8	3	1	7	4	9	5	6
3	10	2	6	7	9	5	4	1	8
10	9	8	4	3	5	6	1	2	7
9	4	7	6	2	5	10	1	3	8
8	9					10			
8	10		6	2	5	9	7	4	1
10	2	6	8	1	5	3	9	4	7
8	7				9	10			
9	7	2	1	4	8	10	5	3	6
3	2	9	5	7	4	1	6	10	8
4	5	6	7	2	1	3	10	8	9
10	5	4	2	6	8	1	9	7	3
5	10	4	7	2	8	1	9	6	3
2	4	10	7	5	1	3	9	6	8
9	8	3	4	5	10	2	1	6	7
3	2	1	4	5	10	9	8	6	7
2	8	9	10	4	6	1	5	7	3
9	5	2	3	1	8	7	4	10	6
9	4	7	3	1	8	10	5	2	6
6	7	4	10	8	5	3	1	9	2
4	8	5	3	1	10	9	7	6	2
5	1	6	9	8	4	3	7	2	10
7	6	9	3	1	10	5	4	2	8
1	6	10	2	5	7	8	3	4	9
9	3	2	7	1	6	8	10	5	4
6	9	2	5	3	10	4	1	8	7
2	9	8	10	5	4	1	3	7	6
1	7	9	8	2	6	5	4	3	10
"""

def parse(s):
	return int(s) if s else 0

ballots_marks = [list(map(parse, s.split('\t'))) for s in ballots_data.split('\n') if s]
#print(ballots_marks)

def to_ballot(array):
	a = [x[0] for x in sorted(zip(candidates, array), key=lambda x: -x[1]) if x[1] != 0]
	return {"ballot": [x for x in a], "done": [], "active_score": 1.0}

ballots = list(map(to_ballot, ballots_marks))
scores = {x: 0 for x in candidates}
for b in ballots:
  scores[b["ballot"][0]] += 1
#print(scores)
votes = len(ballots)
places = 6
round_num = 1
winners = set()
losers = set()

def stv(cand, votes, keep_vote):
  sum_active_score = 0
  for b in ballots:
    if b["ballot"] and b["ballot"][0] == cand:
      sum_active_score += b["active_score"]
  if sum_active_score == 0:
    return False
  any_changed = True
  #print(cand, votes, sum_active_score)
  scores[cand] -= votes
  for b in ballots:
    if b["ballot"] and b["ballot"][0] == cand:
      b["done"].append("%f\t%s" % (keep_vote * b["active_score"] / sum_active_score,  cand))
      b["ballot"] = list(b["ballot"][1:])
      while b["ballot"] and b["ballot"][0] in losers:
        b["done"].append("%f\t%s" % (0, b["ballot"][0]))
        b["ballot"] = list(b["ballot"][1:])
      if b["ballot"]:
        b["active_score"] *= votes / sum_active_score
        scores[b["ballot"][0]] += b["active_score"]
  return True


while len(winners) < places:
  quota = votes / (places + 1) + 1e-9
  print("Round #%d, quota %f" % (round_num, quota))
  for cand, score in scores.items():
    print('%s\t%f' % (cand, score))
  
  new_winners = set()
  for cand, score in scores.items():
    if (cand not in winners) and (score >= quota):
      new_winners.add(cand)

  if new_winners:
    print(', '.join(new_winners) + " became winners")
    for cand in new_winners:
      winners.add(cand)

  any_changed = False
  for cand in winners:
    excess = scores[cand] - quota
    if stv(cand, excess, quota if cand in new_winners else 0):
      any_changed = True

  if not any_changed:
    loser = min(scores, key=scores.get)
    print(loser + " was eliminated")
    stv(loser, scores[loser], 0)
    del scores[loser]
    losers.add(loser)

  round_num += 1

print('Победители:\t', '\t'.join(winners))
for b in ballots:
  v = b["done"]
  v += list(map(lambda x: '-\t'+x, b["ballot"]))
  print('\t'.join(v))


