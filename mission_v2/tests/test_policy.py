import unittest
import numpy as np
from policy import Policy


class PolicyTests(unittest.TestCase):
    def test_dead_serving_link_is_escaped(self):
        m=np.array([[20,-60,2,0,1],[10,-75,10,3,0],[5,-80,1000,0,1]],float)
        p=Policy('topsis',threshold=.9,window=20);net=0
        for _ in range(3):net,_=p.decide(m,net,20,100,2)
        self.assertEqual(net,1)

    def test_short_spike_does_not_switch(self):
        p=Policy('topsis',window=3)
        good=np.array([[20,-60,5,10,0],[0,-100,100,1,.1],[-10,-120,1000,0,1]],float)
        target,_=p.decide(good,0,20,100,2);self.assertEqual(target,0)
        spike=good.copy();spike[0]=[0,-100,100,1,.1];spike[1]=[20,-60,5,10,0]
        target,_=p.decide(spike,0,20,100,2);self.assertEqual(target,0)
        target,_=p.decide(good,0,20,100,2);self.assertEqual(target,0)

    def test_cli_parameters_affect_behavior(self):
        m=np.array([[0,-100,100,1,.1],[20,-60,5,10,0],[-10,-120,1000,0,1]],float)
        p=Policy('topsis',window=1,threshold=0);q=Policy('topsis',window=8,threshold=0)
        self.assertEqual(p.decide(m,0,20,100,2)[0],1)
        self.assertEqual(q.decide(m,0,20,100,2)[0],0)

    def test_checkpoint_required(self):
        with self.assertRaises(ValueError):Policy('laavha')

    def test_all_unavailable_does_not_chatter(self):
        p=Policy('topsis',threshold=0,window=1)
        m=np.array([[20,-50,1000,0,1],[-20,-120,1000,0,1],[0,-100,1000,0,1]],float)
        for _ in range(8):self.assertEqual(p.decide(m,2,20,100,2)[0],2)


if __name__=='__main__':unittest.main()
