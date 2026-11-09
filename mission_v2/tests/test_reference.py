import itertools,unittest
import numpy as np
from reference import solve,evaluate
from mission import motion,sanitize


class ReferenceTests(unittest.TestCase):
    def test_dp_matches_exhaustive_with_interruption(self):
        rng=np.random.default_rng(3)
        metrics=np.zeros((5,3,5));metrics[:,:,0]=10;metrics[:,:,1]=-70;metrics[:,:,2]=10
        metrics[:,:,3]=rng.uniform(.02,4,(5,3));metrics[:,:,4]=rng.uniform(0,.2,(5,3))
        demand=np.full(5,2.)
        for interruption in [0.,.05,.1,.15,.2]:
            for cap in [0,1,2,None]:
                best=-np.inf
                for path in itertools.product(range(3),repeat=5):
                    if cap is not None and np.count_nonzero(np.diff((0,)+path))>cap:continue
                    try:r=evaluate(path,metrics,demand,interruption=interruption)
                    except ValueError:continue
                    best=max(best,r['objective'])
                actual=solve(metrics,demand,interruption=interruption,max_switches=cap)
                self.assertAlmostEqual(actual['objective'],best,places=10)
                self.assertAlmostEqual(evaluate(actual['path'],metrics,demand,interruption=interruption)['objective'],best,places=10)

    def test_more_than_two_switches_are_allowed(self):
        x=np.zeros((12,3,5));x[:,:,0]=10;x[:,:,1]=-70;x[:,:,2]=10;x[:,:,4]=0
        for i in range(12):x[i,(i//2)%3,3]=10
        r=solve(x,np.full(12,2.),interruption=0,cost=.001)
        self.assertGreater(r['switches'],2)

    def test_motion_is_continuous(self):
        for t in [19.5,20.5,29.5,30.5]:
            a=motion(t-1e-7);b=motion(t+1e-7)
            self.assertLess(abs(a[0]-b[0]),1e-4);self.assertLess(abs(a[1]-b[1]),1e-4)

    def test_missing_delay_is_not_low(self):
        m=sanitize([[np.nan,np.nan,np.nan,0,1.3]])
        self.assertEqual(m[0,2],1000);self.assertEqual(m[0,4],1)


if __name__=='__main__':unittest.main()
