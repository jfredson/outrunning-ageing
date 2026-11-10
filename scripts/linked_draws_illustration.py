"""Illustration only: the headline with the branches linked (docs/method.md, parameter 7).

Not part of the headline. John ruled on 2026-10-17 that no link is implemented, because its
strength has no source. This script exists so that the illustrative figures quoted on the method
page and the home page can be rerun on the current records, instead of being left from an older
reading. The October 2026 scratch runs were not saved; this script reproduces them to within
about 0.2 percentage points when run on the records of that date.

Each run draws one shared "how the field is going" number. Every treatment's year is pulled the
same way by it (a Gaussian copula over each treatment's triangle), and r is the share of each
draw's variation that the shared number explains. The delay to ordinary people is drawn
separately, as in the headline. Seed 2004 and 200,000 runs, as in the headline.

    python3 scripts/linked_draws_illustration.py [REPOSITORY ROOT]

Written 2026-11-09.
"""

import sys, random, math
from pathlib import Path
from statistics import NormalDist
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent; sys.path.insert(0, str(root / 'scripts'))
import compute as c
L = c.load_and_validate(root / 'data', history=False)
recs = L['records']
br = {r['key']: r for r in recs if r['_kind'] == 'branch'}
leaves = {k: [] for k in c.BRANCH_ORDER}
for r in recs:
    if r['_kind'] == 'leaf' and r.get('branch') in leaves and c.leaf_counts(r):
        leaves[r['branch']].append(r)
def tri_inv(u, a, m, b):
    if a == b: return a
    f = (m - a) / (b - a)
    return a + math.sqrt(u * (b - a) * (m - a)) if u < f else b - math.sqrt((1 - u) * (b - a) * (b - m))
N = 200000; Phi = NormalDist().cdf
req = [k for k in c.BRANCH_ORDER if br[k].get('required')]
lo, mo, hi = c.LAG
for r in (0, 0.25, 0.5, 0.75):
    rng = random.Random(2004); out = []
    for _ in range(N):
        z = rng.gauss(0, 1); hy = []
        for k in req:
            ys = []
            for lf in leaves[k]:
                y = c.clinic_year(lf)
                if y is None:
                    a, m, b = c.clinic_range(lf)
                    u = Phi(math.sqrt(r) * z + math.sqrt(1 - r) * rng.gauss(0, 1))
                    y = tri_inv(u, a, m, b)
                ys.append(y)
            hy.append(sorted(ys)[int(br[k].get('handled_when', 2)) - 1])
        out.append(int(max(hy) + rng.triangular(lo, hi, mo)))
    out.sort(); p = lambda q: out[int(q / 100 * (N - 1))]
    print(f"r={r}: middle {p(50)}, before 2050 {sum(y < 2050 for y in out) / N:.2%}, spread {p(5)} to {p(95)}, after 2100 {sum(y > 2100 for y in out) / N:.2%}")
