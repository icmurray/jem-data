import mock

import jem_data.dal as dal
import test.jem_data.fixtures as fixtures

def test_delete_all():
    db = mock.MagicMock()
    repo = dal.GatewayRepository(db)

    repo.delete_all()
    db['gateways'].remove.assert_called_once_with()

def test_insert():
    db = mock.MagicMock()
    repo = dal.GatewayRepository(db)
    gateways = fixtures.stub_gateways()

    repo.insert(gateways)
    db['gateways'].insert.assert_called_once_with(mock.ANY)

def test_all():
    db = mock.MagicMock()
    repo = dal.GatewayRepository(db)
    gateways = fixtures.stub_gateways()

    repo.insert(gateways)
    db['gateways'].insert.assert_called_once_with(mock.ANY)
