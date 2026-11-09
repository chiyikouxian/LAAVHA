import unittest
import torch
from model import LAAVHA,torch_features,torch_topsis


class ModelTests(unittest.TestCase):
    def test_weights_are_trained_and_normalized(self):
        torch.manual_seed(8);torch.set_num_threads(1)
        m=LAAVHA();h=torch.randn(2,3,10,5);c=torch.rand(2,3)
        prediction,w=m(h,c)
        f=torch_features(h[:,:,-1],c[:,2]*8+.1)
        scores=torch_topsis(f,w)
        loss=prediction.square().mean()+(scores-torch.tensor([[1,0,0],[0,1,0]])).square().mean()
        loss.backward()
        self.assertEqual(tuple(prediction.shape),(2,3,3,5))
        torch.testing.assert_close(w.sum(1),torch.ones(2))
        self.assertGreater(m.attention.in_proj_weight.grad.abs().sum().item(),0)
        self.assertGreater(m.fc_weight[-1].weight.grad.abs().sum().item(),0)
        self.assertGreater(m.lstm1.weight_ih_l0.grad.abs().sum().item(),0)
        self.assertGreater(w.min().item(),.039)


if __name__=='__main__':unittest.main()
