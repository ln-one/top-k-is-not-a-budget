"""Check incremental certification against the independent array implementation."""
import random
import unittest
import uuid

from certifier import GroupedFrontier
from rank_bounds import UnequalDepthCertificate
from replay import preferred


class CertificateTests(unittest.TestCase):
    def test_observation_limits_exhaustion_and_both_schedules(self):
        rng = random.Random(20260912)
        documents = [str(uuid.UUID(int=i + 1)) for i in range(15)]
        for _ in range(30):
            first = rng.sample(documents, rng.randint(4, 15))
            second = rng.sample(documents, rng.randint(4, 15))
            for exhausted in ((False, False), (True, True), (True, False)):
                reference = UnequalDepthCertificate(
                    first, second, first_exhausted=exhausted[0],
                    second_exhausted=exhausted[1],
                )
                for policy in ("balanced", "dibud"):
                    cert = GroupedFrontier(first, second, exhausted)
                    previous = ()
                    for turn in range(len(first) + len(second)):
                        channel = preferred(cert, policy, turn, 1)
                        if channel is None:
                            break
                        if cert.depth[channel] == cert.maximum[channel]:
                            channel = 1 - channel
                        if cert.depth[channel] == cert.maximum[channel]:
                            break
                        cert.read(channel, 1)
                        output = cert.frontier()
                        self.assertEqual(output, reference.frontier(*cert.depth).output)
                        self.assertEqual(output[:len(previous)], previous)
                        previous = output


if __name__ == "__main__":
    unittest.main()
