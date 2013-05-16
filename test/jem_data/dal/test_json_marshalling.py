import nose.tools as nose

import jem_data.dal.json_marshalling as json_marshalling
import jem_data.util as util
import test.jem_data.fixtures as fixtures

def test_marshalling_and_unmarshalling_gateways():
    nose.assert_equal(fixtures.raw_gateway_data(),
                      map(util.deep_asdict, fixtures.stub_gateways()))

    nose.assert_equal(fixtures.stub_gateways(),
                      map(json_marshalling.unmarshall_gateway,
                          fixtures.raw_gateway_data()))

